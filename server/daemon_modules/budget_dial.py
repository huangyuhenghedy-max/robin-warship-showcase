"""
budget_dial.py — 知更鸟预算优化引擎 (BudgetDial) v2 [P0硬上限]
==================================================

SOTA 调研基础:
1. 斯坦福/MIT论文(2026-04): Agent成本=输入token指数增长, 同任务差2-30倍, 需要"油表+刹车"
2. Model Routing: 80%任务不需要最强模型, 三层路由省40-70%, balanced质量损失<3%
3. 安全调研(2026-07-16): Open Claw 4h烧$1200无熔断 → 必须硬编码不可变上限
4. OWASP LLM10 Unbounded Consumption新增 → Denial-of-Wallet防护
5. PocketOS删库事件5层防线全失效 → 安全闸不可被Agent绕过

核心: 5档滑动刻度 + 任务复杂度自动评估 + 多模型分层路由 + Fable5专用策略
v2新增: HARD_CAP硬上限(不可被Agent修改) + 熔断机制
"""

import json, logging, os, time
import logging

from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, List, Tuple

logger = logging.getLogger(__name__)


logger = logging.getLogger("budget_dial")
SECRETS_PATH = Path(__file__).parent.parent / ".secrets.json"

# ═══════════════════════════════════════════════════════════════
# [P0安全] 全局token硬上限 — 不可被Agent修改
# 来源: Open Claw事故(递归4h烧$1200) + OWASP LLM10 DoW
# 规则: 此常量只有修改源代码才能改变，Agent/API/配置均无法覆盖
# ═══════════════════════════════════════════════════════════════
HARD_CAP_TOTAL_CALLS = 30000          # 单session硬上限(不可变) — DeepSeek 31,650次/5h
HARD_CAP_DAILY_CALLS = 80000          # 每日硬上限(不可变)
HARD_CAP_PREMIUM_CALLS = 100         # premium模型调用硬上限(不可变)
HARD_CAP_RECURSION_DEPTH = 50        # 递归最大深度(不可变)
HARD_CAP_BUDGET_FILE = ".hard_cap.lock"  # 熔断标记文件路径

# ─── 模型分层 ──────────────────────────────────────────────────────

MODEL_TIERS = {
    "budget": {
        "models": ["glm-5.2", "deepseek-v4-flash", "kimi-k2.6"],
        "cost_per_1m_output": 0.50,
        "quality_score": 0.65,
        "speed": "fast",
        "description": "日常编码/格式化/简单修复/文档生成",
        "best_for": ["boilerplate", "formatting", "simple_fix", "docs", "tests", "naming"],
    },
    "standard": {
        "models": ["glm-5.2-pro", "deepseek-v4-pro", "claude-sonnet-4.6"],
        "cost_per_1m_output": 3.00,
        "quality_score": 0.78,
        "speed": "medium",
        "description": "代码审查/多文件修改/中等复杂bug",
        "best_for": ["code_review", "multi_file_edit", "medium_bug", "refactoring", "planning"],
    },
    "premium": {
        "models": ["claude-fable-5", "gpt-5.5", "claude-opus-4.8"],
        "cost_per_1m_output": 30.00,
        "quality_score": 0.90,
        "speed": "slow",
        "description": "架构决策/复杂调试/安全审计/关键代码",
        "best_for": ["architecture", "complex_debug", "security_audit", "critical_code", "repo_level"],
    },
}

# ─── 5档滑动刻度 ──────────────────────────────────────────────────

BUDGET_PROFILES = {
    "eco": {
        "label": "省着用", "icon": "🪫",
        "description": "极度节省, 只用budget模型, 最大化调用次数",
        "budget_model_pct": 95, "standard_model_pct": 5, "premium_model_pct": 0,
        "max_retries": 1, "context_limit": 1500, "batch_size": 8,
        "call_interval": 120, "quality_threshold": 0.3,
        "estimated_calls_per_hour": 30, "cost_per_hour_usd": 0.05,
    },
    "conservative": {
        "label": "保守", "icon": "🔋",
        "description": "优先节省, 关键任务升级模型",
        "budget_model_pct": 80, "standard_model_pct": 15, "premium_model_pct": 5,
        "max_retries": 2, "context_limit": 2500, "batch_size": 5,
        "call_interval": 100, "quality_threshold": 0.35,
        "estimated_calls_per_hour": 25, "cost_per_hour_usd": 0.15,
    },
    "balanced": {
        "label": "均衡", "icon": "⚖️",
        "description": "质量与成本平衡, 推荐日常使用",
        "budget_model_pct": 60, "standard_model_pct": 30, "premium_model_pct": 10,
        "max_retries": 3, "context_limit": 4000, "batch_size": 3,
        "call_interval": 90, "quality_threshold": 0.40,
        "estimated_calls_per_hour": 20, "cost_per_hour_usd": 0.50,
    },
    "aggressive": {
        "label": "激进", "icon": "🔥",
        "description": "质量优先, 大部分任务用standard+",
        "budget_model_pct": 30, "standard_model_pct": 50, "premium_model_pct": 20,
        "max_retries": 3, "context_limit": 6000, "batch_size": 2,
        "call_interval": 75, "quality_threshold": 0.45,
        "estimated_calls_per_hour": 15, "cost_per_hour_usd": 1.50,
    },
    "max_performance": {
        "label": "拉满", "icon": "🚀",
        "description": "不计成本, 全力输出最高质量",
        "budget_model_pct": 10, "standard_model_pct": 40, "premium_model_pct": 50,
        "max_retries": 5, "context_limit": 8000, "batch_size": 1,
        "call_interval": 60, "quality_threshold": 0.50,
        "estimated_calls_per_hour": 10, "cost_per_hour_usd": 5.00,
    },
}

# ─── 数据模型 ──────────────────────────────────────────────────────

class TaskComplexity(str, Enum):
    TRIVIAL = "trivial"
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"
    CRITICAL = "critical"

@dataclass
class TaskPlan:
    task_description: str
    complexity: TaskComplexity
    model_tier: str
    model_name: str
    max_retries: int
    context_limit: int
    batch_size: int
    quality_threshold: float
    estimated_calls: int
    estimated_cost_usd: float
    strategy: str
    should_proceed: bool = True
    budget_warning: str = ""

@dataclass
class BudgetStatus:
    total_budget: int
    calls_used: int
    calls_remaining: int
    budget_pct: float
    current_profile: str
    profile_label: str
    model_distribution: Dict[str, int] = field(default_factory=dict)
    cost_by_tier: Dict[str, float] = field(default_factory=dict)
    estimated_hours_remaining: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    # [P0] HARD_CAP不可变上限信息
    hard_cap_total: int = HARD_CAP_TOTAL_CALLS
    hard_cap_remaining: int = 0
    hard_cap_premium_limit: int = HARD_CAP_PREMIUM_CALLS
    hard_cap_recursion_limit: int = HARD_CAP_RECURSION_DEPTH
    fusebox_tripped: bool = False


# ─── 核心引擎 ──────────────────────────────────────────────────────

class BudgetDial:
    """
    知更鸟预算优化引擎 v2 [P0硬上限]

    核心思路:
    1. 用户设置预算档位 (5档滑动刻度: eco→max_performance)
    2. 每个任务自动评估复杂度 (trivial→critical)
    3. 复杂度+档位 → 模型选择+策略
    4. 预算不足时自动降级 — **HARD_CAP不可被Agent修改**
    5. Fable5等premium调用只在关键决策时使用
    6. Fable5决策作为Contract指导GLM执行 (Contract-Coding模式)

    [P0安全] HARD_CAP系统:
    - HARD_CAP_TOTAL_CALLS: session总调用硬上限(默认2000)
    - HARD_CAP_PREMIUM_CALLS: premium模型硬上限(默认100)
    - HARD_CAP_RECURSION_DEPTH: 递归深度硬上限(默认50)
    - 以上上限仅通过修改源代码更改, Agent/API/配置均无法覆盖
    - 熔断文件(.hard_cap.lock)存在时所有调用被拒绝
    """

    def __init__(self, state_dir: Optional[Path] = None):
        self.state_dir = state_dir or Path(__file__).parent.parent
        self.state_file = self.state_dir / "budget_dial_state.json"
        self._fusebox_file = self.state_dir / HARD_CAP_BUDGET_FILE
        # ── [Task #414] 溯源加权经济系统 ──
        # 每个 task_type / file 维护动态权重, 基于历史成功率增减
        # weight ∈ [0.1, 2.0], 默认 1.0
        # - 完成 + real_diff=True → +0.05
        # - 完成 + real_diff=False → -0.02
        # - failed                 → -0.10
        # weight 持久化到 .fast_budget.json (独立文件, 高频写不污染主 state)
        self._weights_file = self.state_dir / ".fast_budget.json"
        self._success_weights: Dict[str, float] = {}  # key = "task_type:file" or "task_type"
        self._total_inheritance_events = 0
        self._profile = "balanced"
        self._model_usage: Dict[str, int] = {"budget": 0, "standard": 0, "premium": 0}
        self._cost_accumulated: Dict[str, float] = {"budget": 0.0, "standard": 0.0, "premium": 0.0}
        # [P0] total_budget由HARD_CAP锁定，state文件可读取但不能超过HARD_CAP
        self._total_budget = HARD_CAP_TOTAL_CALLS
        self._calls_used = 0
        self._recursion_depth = 0  # [P0] 递归深度追踪
        self._load_state()
        self._load_weights()
        # [P0] 任何情况下total_budget不得超过HARD_CAP
        if self._total_budget > HARD_CAP_TOTAL_CALLS:
            logger.warning(f"[P0安全] total_budget({self._total_budget})超过HARD_CAP({HARD_CAP_TOTAL_CALLS}), 强制修正")
            self._total_budget = HARD_CAP_TOTAL_CALLS

    # ─── 状态持久化 ─────────────────────────────────────────────

    def _load_state(self):
        if self.state_file.exists():
            try:
                data = json.loads(self.state_file.read_text(encoding="utf-8"))
                self._profile = data.get("profile", "balanced")
                self._model_usage = data.get("model_usage", {"budget": 0, "standard": 0, "premium": 0})
                self._cost_accumulated = data.get("cost_accumulated", {"budget": 0.0, "standard": 0.0, "premium": 0.0})
                # [P0安全] 从文件读取的total_budget不能超过HARD_CAP
                loaded_budget = data.get("total_budget", HARD_CAP_TOTAL_CALLS)
                self._total_budget = min(loaded_budget, HARD_CAP_TOTAL_CALLS)
                self._calls_used = data.get("calls_used", 0)
                # [P0] 校验状态文件未被篡改
                if loaded_budget > HARD_CAP_TOTAL_CALLS:
                    logger.warning(f"[P0安全] 状态文件total_budget({loaded_budget})超过HARD_CAP({HARD_CAP_TOTAL_CALLS}), 已修正")
            except Exception as e:
                logger.warning(f"BudgetDial state load failed: {e}")

    def _save_state(self):
        # [P0安全] 保存时也确保不写入超过HARD_CAP的值
        safe_budget = min(self._total_budget, HARD_CAP_TOTAL_CALLS)
        data = {
            "profile": self._profile,
            "model_usage": self._model_usage,
            "cost_accumulated": self._cost_accumulated,
            "total_budget": safe_budget,
            "calls_used": self._calls_used,
            "hard_cap": HARD_CAP_TOTAL_CALLS,  # [P0] 标记硬上限供审计
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        try:
            tmp = self.state_file.with_suffix(".tmp")
            tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            tmp.replace(self.state_file)
        except Exception as e:
            logger.error(f"BudgetDial state save failed: {e}")

    # ─── [Task #414] 溯源加权经济系统 ─────────────────────────────

    WEIGHT_MIN = 0.1
    WEIGHT_MAX = 2.0
    WEIGHT_DEFAULT = 1.0
    # 增量规则 (ZEBRA water-filling 思路: 高产文件多投, 低产文件少投)
    WEIGHT_DELTA_SUCCESS_DIFF = 0.05   # 完成 + 真实改动 → +0.05
    WEIGHT_DELTA_SUCCESS_NODIFF = -0.02  # 完成 + 无真实改动 → -0.02 (轻惩罚, 可能是验证类)
    WEIGHT_DELTA_FAILED = -0.10        # 失败 → -0.10 (重惩罚, 真问题)
    WEIGHT_DELTA_PENALTY_FLOOR = 0.1   # 即便权重很低也保留最低探索机会

    def _load_weights(self):
        """从 .fast_budget.json 加载溯源权重"""
        if self._weights_file.exists():
            try:
                data = json.loads(self._weights_file.read_text(encoding="utf-8"))
                weights = data.get("success_weights", {})
                # 类型校验 + 范围裁剪
                self._success_weights = {
                    str(k): max(self.WEIGHT_MIN, min(self.WEIGHT_MAX, float(v)))
                    for k, v in weights.items()
                    if isinstance(v, (int, float))
                }
                self._total_inheritance_events = data.get("total_events", 0)
            except Exception as e:
                logger.warning(f"weights load failed: {e}")
                self._success_weights = {}

    def _save_weights(self):
        """持久化溯源权重到 .fast_budget.json"""
        data = {
            "success_weights": self._success_weights,
            "total_events": self._total_inheritance_events,
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        try:
            tmp = self._weights_file.with_suffix(".tmp")
            tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            tmp.replace(self._weights_file)
        except Exception as e:
            logger.warning(f"weights save failed: {e}")

    def _weight_key(self, task_type: str, file_path: str = "") -> str:
        """构造 weight 索引 key. 优先级: task_type:file > task_type"""
        if file_path:
            # 归一化: 去绝对路径前缀, 统一斜杠
            normalized = str(file_path).replace("\\", "/").split("/")[-1]  # 只要文件名
            return f"{task_type}:{normalized}"
        return task_type

    def get_weight(self, task_type: str, file_path: str = "") -> float:
        """查询某 task_type/file 的当前权重 [0.1, 2.0]

        没记录则返回 WEIGHT_DEFAULT (1.0), 表示无偏好
        """
        key = self._weight_key(task_type, file_path)
        return self._success_weights.get(key, self.WEIGHT_DEFAULT)

    def update_weight(
        self,
        task_type: str,
        success: bool,
        real_diff: bool = False,
        file_path: str = "",
    ) -> float:
        """根据任务结果更新溯源权重, 返回更新后的权重

        规则 (ZEBRA water-filling 思路):
          success + real_diff=True  → +0.05  (高产任务/文件多投)
          success + real_diff=False → -0.02  (无真实改动, 轻惩罚)
          failed                    → -0.10  (重惩罚)

        边界: weight 裁剪到 [0.1, 2.0]
        持久化: 写入 .fast_budget.json

        使用方式 (capability_registry.handle_code 完成路径):
          ctx.budget.update_weight(
              task_type=task.get("type", "code"),
              success=(task["status"] == "completed"),
              real_diff=task.get("_real_diff", False),
              file_path=(task.get("_modified_files") or [""])[0],
          )
        """
        if success and real_diff:
            delta = self.WEIGHT_DELTA_SUCCESS_DIFF
        elif success and not real_diff:
            delta = self.WEIGHT_DELTA_SUCCESS_NODIFF
        else:
            delta = self.WEIGHT_DELTA_FAILED

        key = self._weight_key(task_type, file_path)
        old_w = self._success_weights.get(key, self.WEIGHT_DEFAULT)
        new_w = max(self.WEIGHT_MIN, min(self.WEIGHT_MAX, old_w + delta))
        self._success_weights[key] = new_w
        self._total_inheritance_events += 1

        # 只在权重变化超过阈值时落盘 (减少 IO)
        if abs(new_w - old_w) > 0.001:
            self._save_weights()

        logger.debug(
            f"[ProvenanceWeight] {key}: {old_w:.3f} → {new_w:.3f} "
            f"(success={success} real_diff={real_diff} delta={delta:+.3f})"
        )
        return new_w

    def get_weight_leaderboard(self, top_n: int = 10) -> Dict[str, list]:
        """获取权重排行榜 (供运维面板/调试)

        返回: {"top_gain": [...], "top_loss": [...], "by_task_type": {...}}
        """
        if not self._success_weights:
            return {"top_gain": [], "top_loss": [], "by_task_type": {}}

        sorted_items = sorted(
            self._success_weights.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        top_gain = [
            {"key": k, "weight": v}
            for k, v in sorted_items[:top_n]
            if v > self.WEIGHT_DEFAULT
        ]
        top_loss = [
            {"key": k, "weight": v}
            for k, v in sorted_items[-top_n:]
            if v < self.WEIGHT_DEFAULT
        ]

        # 按 task_type 聚合
        by_type: Dict[str, list] = {}
        for k, v in self._success_weights.items():
            task_type = k.split(":")[0]
            by_type.setdefault(task_type, []).append(v)
        by_type_summary = {
            t: {
                "count": len(ws),
                "avg_weight": sum(ws) / len(ws),
                "max": max(ws),
                "min": min(ws),
            }
            for t, ws in by_type.items()
        }

        return {
            "top_gain": top_gain,
            "top_loss": top_loss,
            "by_task_type": by_type_summary,
        }

    # ─── [P0] 熔断机制 ───────────────────────────────────────

    def _check_fusebox(self) -> bool:
        """检查熔断状态。返回True=已熔断(拒绝所有调用), False=正常"""
        if self._fusebox_file.exists():
            try:
                fuse_data = json.loads(self._fusebox_file.read_text(encoding="utf-8"))
                if fuse_data.get("tripped", False):
                    reason = fuse_data.get("reason", "未知原因")
                    time_left = fuse_data.get("cooldown_until", 0) - time.time()
                    if time_left > 0:
                        logger.critical(f"[FUSEBOX] 熔断中: {reason}, 剩余{int(time_left)}s")
                        return True
                    else:
                        # 冷却时间已过，自动复位
                        self._reset_fusebox()
            except Exception: logger.debug('ignored Exception', exc_info=True)
        return False

    def _trip_fusebox(self, reason: str, cooldown_seconds: int = 300):
        """触发熔断：写入熔断文件，所有调用被拒绝"""
        fuse_data = {
            "tripped": True,
            "reason": reason,
            "tripped_at": time.time(),
            "cooldown_until": time.time() + cooldown_seconds,
            "calls_used_at_trip": self._calls_used,
        }
        try:
            self._fusebox_file.write_text(
                json.dumps(fuse_data, ensure_ascii=False, indent=2), encoding="utf-8")
            logger.critical(f"[FUSEBOX] 熔断触发: {reason}, 冷却{cooldown_seconds}s")
        except Exception as e:
            logger.error(f"[FUSEBOX] 熔断写入失败: {e}")

    def _reset_fusebox(self):
        """复位熔断"""
        try:
            if self._fusebox_file.exists():
                self._fusebox_file.unlink()
            logger.info("[FUSEBOX] 熔断已复位")
        except Exception as e:
            logger.error(f"[FUSEBOX] 熔断复位失败: {e}")

    # ─── [P0] 递归深度检测 ────────────────────────────────────

    def check_recursion(self) -> bool:
        """检测是否超过递归深度上限。返回True=允许继续, False=超过上限"""
        if self._recursion_depth >= HARD_CAP_RECURSION_DEPTH:
            logger.critical(f"[P0安全] 递归深度{HARD_CAP_RECURSION_DEPTH}达到上限, 触发熔断")
            self._trip_fusebox(f"递归深度达到上限({HARD_CAP_RECURSION_DEPTH})")
            return False
        self._recursion_depth += 1
        return True

    def reset_recursion(self):
        """重置递归深度追踪（在非递归调用时调用）"""
        self._recursion_depth = 0

    # ─── [P0] 预算可用性检查 ─────────────────────────────────

    def can_spend(self, estimated_calls: int = 1, tier: str = "budget") -> Tuple[bool, str]:
        """[P0安全] 三重检查：HARD_CAP + 熔断 + premium上限
        返回: (是否允许, 拒绝原因)
        """
        # 检查1: 熔断
        if self._check_fusebox():
            return False, "系统已熔断"

        # 检查2: HARD_CAP总调用上限
        if self._calls_used + estimated_calls > HARD_CAP_TOTAL_CALLS:
            return False, f"HARD_CAP总调用上限({HARD_CAP_TOTAL_CALLS})将超过"

        # 检查3: premium模型独立上限
        if tier == "premium":
            premium_used = self._model_usage.get("premium", 0)
            if premium_used + 1 > HARD_CAP_PREMIUM_CALLS:
                return False, f"HARD_CAP premium上限({HARD_CAP_PREMIUM_CALLS})将超过"

        # 检查4: 软预算
        if self._calls_used + estimated_calls > self._total_budget:
            return False, "软预算不足(可尝试提高档位)"

        return True, "ok"

    # ─── 档位设置 ───────────────────────────────────────────────

    def set_profile(self, profile: str) -> Dict:
        if profile not in BUDGET_PROFILES:
            raise ValueError(f"Unknown profile: {profile}. Choose from: {list(BUDGET_PROFILES.keys())}")
        # [P0安全] 预算低时禁止切换激进/拉满档位
        remaining = HARD_CAP_TOTAL_CALLS - self._calls_used
        if profile in ("aggressive", "max_performance") and remaining < 200:
            raise ValueError(f"[P0安全] 预算不足(仅剩{remaining}次), 禁止切换{profile}档位")
        self._profile = profile
        self._save_state()
        return self.get_profile_info()

    def get_profile_info(self) -> Dict:
        p = BUDGET_PROFILES[self._profile]
        return {
            "profile": self._profile, "label": p["label"], "icon": p["icon"],
            "description": p["description"],
            "model_distribution": {"budget": p["budget_model_pct"], "standard": p["standard_model_pct"], "premium": p["premium_model_pct"]},
            "max_retries": p["max_retries"], "context_limit": p["context_limit"],
            "batch_size": p["batch_size"], "quality_threshold": p["quality_threshold"],
            "estimated_calls_per_hour": p["estimated_calls_per_hour"],
            "cost_per_hour_usd": p["cost_per_hour_usd"],
        }

    def list_profiles(self) -> List[Dict]:
        result = []
        for key, p in BUDGET_PROFILES.items():
            result.append({
                "id": key, "label": p["label"], "icon": p["icon"],
                "description": p["description"],
                "budget_pct": p["budget_model_pct"], "standard_pct": p["standard_model_pct"],
                "premium_pct": p["premium_model_pct"],
                "calls_per_hour": p["estimated_calls_per_hour"],
                "cost_per_hour": p["cost_per_hour_usd"],
            })
        return result

    # ─── 任务复杂度评估 ─────────────────────────────────────────

    def assess_complexity(self, task_description: str, file_count: int = 1,
                          estimated_lines: int = 0, is_architecture: bool = False,
                          is_security: bool = False) -> TaskComplexity:
        desc_lower = task_description.lower()
        score = 0  # 0=trivial, 1=simple, 2=medium, 3=complex, 4=critical

        for s in ["架构", "重构", "安全审计", "全仓库", "architecture", "refactor", "security audit", "repo-level", "migration", "迁移"]:
            if s in desc_lower: score = max(score, 4)
        for s in ["多文件", "复杂调试", "跨模块", "multi-file", "complex debug", "cross-module", "性能优化", "performance", "并发", "concurrent"]:
            if s in desc_lower: score = max(score, 3)
        for s in ["修复", "bug", "fix", "添加功能", "add feature", "修改", "多步", "multi-step", "集成", "integration"]:
            if s in desc_lower: score = max(score, 2)
        for s in ["格式化", "命名", "注释", "format", "rename", "comment", "文档", "docs", "测试", "test", "类型注解", "type hint"]:
            if s in desc_lower: score = max(score, 1)
        for s in ["空行", "空白", "whitespace", "拼写", "typo", "缩进", "indent"]:
            if s in desc_lower: score = max(score, 0)

        if file_count >= 5: score = max(score, 2)
        if file_count >= 10: score = max(score, 3)
        if estimated_lines >= 500: score = max(score, 2)
        if estimated_lines >= 2000: score = max(score, 3)
        if is_architecture: score = max(score, 3)
        if is_security: score = max(score, 4)
        if score == 0 and len(task_description) > 20: score = 1

        return {0: TaskComplexity.TRIVIAL, 1: TaskComplexity.SIMPLE, 2: TaskComplexity.MEDIUM,
                3: TaskComplexity.COMPLEX, 4: TaskComplexity.CRITICAL}.get(score, TaskComplexity.SIMPLE)

    # ─── 模型选择 ───────────────────────────────────────────────

    def select_model(self, complexity: TaskComplexity, budget_remaining: int,
                     force_tier: Optional[str] = None) -> Tuple[str, str]:
        profile = BUDGET_PROFILES[self._profile]

        if force_tier and force_tier in MODEL_TIERS:
            tier = force_tier
        else:
            default_map = {
                TaskComplexity.TRIVIAL: "budget", TaskComplexity.SIMPLE: "budget",
                TaskComplexity.MEDIUM: "standard", TaskComplexity.COMPLEX: "standard",
                TaskComplexity.CRITICAL: "premium",
            }
            tier = default_map.get(complexity, "budget")

            # 档位修正
            if self._profile == "eco":
                tier = {"standard": "budget", "premium": "standard"}.get(tier, tier)
            elif self._profile == "conservative":
                if tier == "premium" and complexity != TaskComplexity.CRITICAL:
                    tier = "standard"
            elif self._profile == "aggressive":
                if complexity in (TaskComplexity.SIMPLE, TaskComplexity.MEDIUM):
                    tier = "standard"
            elif self._profile == "max_performance":
                if complexity in (TaskComplexity.MEDIUM, TaskComplexity.COMPLEX):
                    tier = "premium"
                elif complexity == TaskComplexity.SIMPLE:
                    tier = "standard"

        # ── v8.6.1: RL 路由反馈—用历史质量数据修正路由 ──
        try:
            from daemon_modules.rl_router import get_routing_stats
            _rl_stats = get_routing_stats()
            _total_records = _rl_stats.get("total_records", 0)
            if _total_records > 50:  # 足量数据才启用
                _model_breakdown = _rl_stats.get("model_breakdown", {})
                _model = MODEL_TIERS.get(tier, {})
                _model_name = _model.get("model", "")
                if _model_name in _model_breakdown:
                    _sr = _model_breakdown[_model_name].get("rate", 0.5)
                    if _sr < 0.3 and tier != "budget":
                        # 当前模型历史成功率 < 30%, 主动降级
                        old_tier = tier
                        tier = "budget"
                        logger.info(f"[RL] model '{_model_name}' SR={_sr:.2f} < 0.3, "
                                    f"downgraded {old_tier}→budget")
        except Exception as _e: logger.warning("except:pass -> logged", exc_info=True)
        # 预算不足自动降级 — [P0] 使用HARD_CAP做硬检查
        calls_left = HARD_CAP_TOTAL_CALLS - self._calls_used
        if calls_left < 50 and tier == "premium":
            tier = "standard"
            logger.info(f"[P0] HARD_CAP剩余{calls_left}, premium→standard降级")
        if calls_left < 20 and tier == "standard":
            tier = "budget"
            logger.info(f"[P0] HARD_CAP剩余{calls_left}, standard→budget降级")
        # [P0] 熔断检查：剩余调用极低时全降budget
        if calls_left < 5:
            tier = "budget"
            logger.warning(f"[P0熔断] HARD_CAP仅剩{calls_left}次, 强制budget模式")

        model_name = self._pick_available_model(MODEL_TIERS[tier]["models"])
        return tier, model_name

    def _pick_available_model(self, model_list: List[str]) -> str:
        available = self._get_configured_models()
        for m in model_list:
            if m in available: return m
        return model_list[0]

    def _get_configured_models(self) -> List[str]:
        """从 .secrets.json 读取实际配置的模型名"""
        models = []
        if os.environ.get("ROBIN_GLM_API_KEY"):
            models.append(os.environ.get("ROBIN_GLM_MODEL", "glm-5.2"))
        try:
            if SECRETS_PATH.exists():
                secrets = json.loads(SECRETS_PATH.read_text(encoding="utf-8"))
                for seg in ("llm_deepseek", "llm_fast", "llm"):
                    cfg = secrets.get(seg, {})
                    m = cfg.get("model", "")
                    if m and m not in models:
                        models.append(m)
        except Exception: logger.debug('ignored Exception', exc_info=True)
        return models or ["glm-5.2", "deepseek-v4-flash"]

    # ─── 任务规划 ───────────────────────────────────────────────

    def plan_task(self, task_description: str, budget_remaining: Optional[int] = None,
                  file_count: int = 1, estimated_lines: int = 0,
                  is_architecture: bool = False, is_security: bool = False,
                  force_tier: Optional[str] = None) -> TaskPlan:
        complexity = self.assess_complexity(task_description, file_count, estimated_lines, is_architecture, is_security)
        remaining = budget_remaining or (self._total_budget - self._calls_used)
        tier, model_name = self.select_model(complexity, remaining, force_tier)
        profile = BUDGET_PROFILES[self._profile]
        tier_info = MODEL_TIERS[tier]

        calls_map = {TaskComplexity.TRIVIAL: 1, TaskComplexity.SIMPLE: 2, TaskComplexity.MEDIUM: 5,
                     TaskComplexity.COMPLEX: 10, TaskComplexity.CRITICAL: 20}
        estimated_calls = calls_map.get(complexity, 3) + profile["max_retries"]
        cost_per_call = (1000 / 1_000_000) * tier_info["cost_per_1m_output"]
        estimated_cost = estimated_calls * cost_per_call

        should_proceed = remaining >= estimated_calls
        warning = ""
        if remaining < estimated_calls:
            warning = f"预算不足: 需要{estimated_calls}次, 仅剩{remaining}次"
        elif remaining < estimated_calls * 3:
            warning = f"预算紧张: 剩余{remaining}次, 建议切换eco"

        strategy_map = {
            TaskComplexity.TRIVIAL: f"单次{model_name}调用, 快速处理",
            TaskComplexity.SIMPLE: f"1-2次{model_name}调用, 简单修复",
            TaskComplexity.MEDIUM: f"多步{model_name}调用, 分批处理{file_count}文件",
            TaskComplexity.COMPLEX: f"分阶段{model_name}调用, 先分析再修改, 最多{profile['max_retries']}次重试",
            TaskComplexity.CRITICAL: f"深度{model_name}调用, 全上下文+多轮验证, 最多{profile['max_retries']}次重试",
        }

        return TaskPlan(
            task_description=task_description, complexity=complexity,
            model_tier=tier, model_name=model_name,
            max_retries=profile["max_retries"], context_limit=profile["context_limit"],
            batch_size=profile["batch_size"], quality_threshold=profile["quality_threshold"],
            estimated_calls=estimated_calls, estimated_cost_usd=round(estimated_cost, 4),
            strategy=strategy_map.get(complexity, "标准执行"),
            should_proceed=should_proceed, budget_warning=warning,
        )

    # ─── 预算记账 ───────────────────────────────────────────────

    def record_call(self, tier: str, success: bool, output_tokens: int = 1000) -> bool:
        """[P0安全] 记录调用。在can_spend检查通过后调用。
        返回True=记账成功, False=被HARD_CAP拒绝(熔断)
        """
        allowed, reason = self.can_spend(1, tier)
        if not allowed:
            logger.critical(f"[P0安全] record_call被拒绝: {reason}")
            if "熔断" in reason or "HARD_CAP" in reason:
                self._trip_fusebox(f"record_call被HARD_CAP拒绝: {reason}")
            return False

        self._calls_used += 1
        self._model_usage[tier] = self._model_usage.get(tier, 0) + 1
        cost = (output_tokens / 1_000_000) * MODEL_TIERS.get(tier, MODEL_TIERS["budget"])["cost_per_1m_output"]
        self._cost_accumulated[tier] = self._cost_accumulated.get(tier, 0.0) + cost
        self._save_state()

        # [P0] 接近上限时告警
        remaining = HARD_CAP_TOTAL_CALLS - self._calls_used
        if remaining <= 10:
            logger.critical(f"[P0安全] HARD_CAP仅剩{remaining}次调用!")
        elif remaining <= 50:
            logger.warning(f"[P0安全] HARD_CAP剩余{remaining}次")
        return True

    # ─── 状态查询 ───────────────────────────────────────────────

    def get_status(self, daemon_calls_used: int = 0) -> BudgetStatus:
        remaining = self._total_budget - self._calls_used
        # [P0] 也计算HARD_CAP剩余
        hard_remaining = HARD_CAP_TOTAL_CALLS - self._calls_used
        profile = BUDGET_PROFILES[self._profile]
        calls_per_hour = profile["estimated_calls_per_hour"]
        hours_remaining = remaining / calls_per_hour if calls_per_hour > 0 else 0
        pct_used = self._calls_used / HARD_CAP_TOTAL_CALLS if HARD_CAP_TOTAL_CALLS > 0 else 0

        recommendations = []
        # [P0] HARD_CAP接近时优先告警
        if hard_remaining <= 10:
            recommendations.append(f"[P0熔断] HARD_CAP仅剩{hard_remaining}次! 系统将自动熔断")
        elif hard_remaining <= 50:
            recommendations.append(f"[P0警告] HARD_CAP剩余{hard_remaining}次")
        if pct_used > 0.8: recommendations.append("HARD_CAP使用>80%, 建议切换eco延长工作时间")
        if pct_used > 0.95: recommendations.append("HARD_CAP即将耗尽! 立即切换eco或停止非关键任务")
        if self._profile in ("aggressive", "max_performance") and remaining < 200:
            recommendations.append(f"剩余{remaining}次不够激进模式, 建议降为balanced")
        if self._model_usage.get("premium", 0) > self._calls_used * 0.3:
            recommendations.append("premium调用占比>30%, 检查是否有简单任务误用premium")
        if remaining > self._total_budget * 0.7 and self._profile == "eco":
            recommendations.append("预算充足, 可升级到balanced提升质量")

        return BudgetStatus(
            total_budget=self._total_budget, calls_used=self._calls_used,
            calls_remaining=remaining, budget_pct=round(pct_used * 100, 1),
            current_profile=self._profile, profile_label=profile["label"],
            model_distribution=dict(self._model_usage),
            cost_by_tier={k: round(v, 4) for k, v in self._cost_accumulated.items()},
            estimated_hours_remaining=round(hours_remaining, 1),
            recommendations=recommendations,
            hard_cap_remaining=hard_remaining,
            fusebox_tripped=self._check_fusebox(),
        )

    # ─── 智能推荐 ───────────────────────────────────────────────

    def recommend_profile(self, total_calls: int, hours_available: float,
                          quality_priority: str = "balanced") -> Dict:
        calls_per_hour = total_calls / hours_available if hours_available > 0 else 999

        if calls_per_hour >= 25: recommended, reason = "eco", f"每小时{calls_per_hour:.0f}次, eco最大化产出"
        elif calls_per_hour >= 15: recommended, reason = "conservative", f"每小时{calls_per_hour:.0f}次, conservative平衡"
        elif calls_per_hour >= 8: recommended, reason = "balanced", f"每小时{calls_per_hour:.0f}次, balanced最佳性价比"
        elif calls_per_hour >= 4: recommended, reason = "aggressive", f"每小时{calls_per_hour:.0f}次, aggressive确保质量"
        else: recommended, reason = "max_performance", f"每小时仅{calls_per_hour:.0f}次, 必须每次最大价值"

        if quality_priority == "quality" and recommended in ("eco", "conservative"):
            recommended = "balanced"; reason += " (质量优先修正)"
        elif quality_priority == "speed" and recommended in ("aggressive", "max_performance"):
            recommended = "balanced"; reason += " (速度优先修正)"

        fable5_calls = int(os.environ.get("FABLE5_CALL_LIMIT", "0"))
        fable5_strategy = ""
        if 0 < fable5_calls <= 20:
            fable5_strategy = f"Fable5仅{fable5_calls}次, 只在critical/complex任务使用(约{max(1, fable5_calls//3)}次), 其余全用GLM-5.2"

        p = BUDGET_PROFILES[recommended]
        return {
            "recommended_profile": recommended, "reason": reason,
            "calls_per_hour_available": round(calls_per_hour, 1),
            "total_calls": total_calls, "hours_available": hours_available,
            "fable5_strategy": fable5_strategy,
            "profile_details": {"label": p["label"], "icon": p["icon"],
                "budget_pct": p["budget_model_pct"], "standard_pct": p["standard_model_pct"],
                "premium_pct": p["premium_model_pct"], "est_calls_per_hour": p["estimated_calls_per_hour"]},
        }

    # ─── Fable5 混合策略 ────────────────────────────────────────

    def fable5_strategy(self, fable5_calls: int, glm_calls: int, tasks: List[str]) -> Dict:
        critical, complex_, medium, simple = [], [], [], []
        for task in tasks:
            c = self.assess_complexity(task)
            if c == TaskComplexity.CRITICAL: critical.append(task)
            elif c == TaskComplexity.COMPLEX: complex_.append(task)
            elif c == TaskComplexity.MEDIUM: medium.append(task)
            else: simple.append(task)

        f5_critical = min(len(critical), fable5_calls)
        f5_remaining = fable5_calls - f5_critical
        f5_complex = min(len(complex_), f5_remaining)
        f5_remaining -= f5_complex
        f5_medium = min(len(medium) // 3, f5_remaining)

        glm_needed = len(simple) + (len(medium) - f5_medium) + (len(complex_) - f5_complex) + (len(critical) - f5_critical)
        return {
            "fable5_allocation": {"critical": f5_critical, "complex": f5_complex,
                "medium": f5_medium, "total_used": f5_critical + f5_complex + f5_medium,
                "total_available": fable5_calls},
            "glm_allocation": {"total_needed": glm_needed, "total_available": glm_calls,
                "sufficient": glm_calls >= glm_needed},
            "strategy": f"Fable5({fable5_calls}次)专攻{f5_critical}critical+{f5_complex}complex做架构决策, GLM-5.2({glm_calls}次)执行日常, Fable5决策作Contract指导GLM",
            "efficiency_gain": f"混合策略覆盖{len(tasks)}任务(纯Fable5只能{fable5_calls}个), critical质量提升~30%",
        }

    # ─── 守护进程集成 ───────────────────────────────────────────

    def get_daemon_config(self) -> Dict:
        profile = BUDGET_PROFILES[self._profile]
        remaining = self._total_budget - self._calls_used
        if remaining < 50:
            return {"interval": 180, "batch_size": 10, "max_lines_per_edit": 3,
                    "quality_threshold": 0.25, "default_tier": "budget",
                    "allow_premium": False, "max_retries": 1}
        return {"interval": profile["call_interval"], "batch_size": profile["batch_size"],
                "max_lines_per_edit": 8, "quality_threshold": profile["quality_threshold"],
                "default_tier": "budget", "allow_premium": self._profile in ("aggressive", "max_performance"),
                "max_retries": profile["max_retries"]}


# ─── API 路由注册 ──────────────────────────────────────────────────

def register_budget_api(app, dial: BudgetDial):
    """注册预算优化API到aiohttp app"""
    from aiohttp import web

    async def api_get_profiles(request):
        return web.json_response(dial.list_profiles())

    async def api_get_profile(request):
        return web.json_response(dial.get_profile_info())

    async def api_set_profile(request):
        data = await request.json()
        profile = data.get("profile", "balanced")
        try:
            return web.json_response(dial.set_profile(profile))
        except ValueError as e:
            return web.json_response({"error": str(e)}, status=400)

    async def api_get_status(request):
        status = dial.get_status()
        return web.json_response(asdict(status))

    async def api_plan_task(request):
        data = await request.json()
        plan = dial.plan_task(
            task_description=data.get("task", ""),
            budget_remaining=data.get("budget_remaining"),
            file_count=data.get("file_count", 1),
            estimated_lines=data.get("estimated_lines", 0),
            is_architecture=data.get("is_architecture", False),
            is_security=data.get("is_security", False),
            force_tier=data.get("force_tier"),
        )
        result = asdict(plan)
        result["complexity"] = plan.complexity.value
        return web.json_response(result)

    async def api_recommend(request):
        data = await request.json() if request.body_exists else {}
        total_calls = data.get("total_calls", dial._total_budget)
        hours = data.get("hours_available", 5.0)
        quality = data.get("quality_priority", "balanced")
        return web.json_response(dial.recommend_profile(total_calls, hours, quality))

    async def api_fable5_strategy(request):
        data = await request.json()
        return web.json_response(dial.fable5_strategy(
            fable5_calls=data.get("fable5_calls", 10),
            glm_calls=data.get("glm_calls", 1500),
            tasks=data.get("tasks", []),
        ))

    async def api_record_call(request):
        data = await request.json()
        dial.record_call(
            tier=data.get("tier", "budget"),
            success=data.get("success", True),
            output_tokens=data.get("output_tokens", 1000),
        )
        return web.json_response({"status": "ok"})

    app.router.add_get("/api/budget/profiles", api_get_profiles)
    app.router.add_get("/api/budget/profile", api_get_profile)
    app.router.add_post("/api/budget/profile", api_set_profile)
    app.router.add_get("/api/budget/status", api_get_status)
    app.router.add_post("/api/budget/plan", api_plan_task)
    app.router.add_post("/api/budget/recommend", api_recommend)
    app.router.add_post("/api/budget/fable5", api_fable5_strategy)
    app.router.add_post("/api/budget/record", api_record_call)

    # [P0] HARD_CAP只读查询端点和熔断控制
    async def api_hard_cap_status(request):
        return web.json_response({
            "hard_cap_total": HARD_CAP_TOTAL_CALLS,
            "hard_cap_remaining": HARD_CAP_TOTAL_CALLS - dial._calls_used,
            "hard_cap_premium_limit": HARD_CAP_PREMIUM_CALLS,
            "hard_cap_recursion_limit": HARD_CAP_RECURSION_DEPTH,
            "calls_used": dial._calls_used,
            "fusebox_tripped": dial._check_fusebox(),
            "mutable_via_api": False,  # [P0] 明确告知前端此值不可通过API修改
        })

    async def api_fusebox_status(request):
        tripped = dial._check_fusebox()
        if tripped:
            fuse_data = json.loads(dial._fusebox_file.read_text(encoding="utf-8"))
            return web.json_response({"tripped": True, **fuse_data})
        return web.json_response({"tripped": False})

    async def api_fusebox_reset(request):
        """仅限系统管理员复位熔断（需要system_token验证）"""
        data = await request.json() if request.body_exists else {}
        token = data.get("system_token", "")
        # [P0] 硬编码系统令牌（实际应为环境变量）
        expected_token = os.environ.get("BUDGET_SYSTEM_TOKEN", "")
        if not expected_token or token != expected_token:
            return web.json_response({"error": "未授权"}, status=403)
        dial._reset_fusebox()
        return web.json_response({"status": "fusebox_reset"})

    app.router.add_get("/api/budget/hardcap", api_hard_cap_status)
    app.router.add_get("/api/budget/fusebox", api_fusebox_status)
    app.router.add_post("/api/budget/fusebox/reset", api_fusebox_reset)
