"""
知更鸟 编排层 (Orchestrator) — v3.2 重构
========================================
参考 BuilderIO/agent-native 分层思想重构：
  - router.py   : 路由层 — 消息分发，不包含业务逻辑
  - orchestrator.py : 编排层 — AI 对话、身份系统、记忆引擎、情绪管理
  - tool_registry.py : 工具注册层 — TTS、配置扫描等

导出函数（router.py / server.py 使用）:
  - call_ai()            : 核心 AI 对话（含记忆注入 + 情绪解析 + 记忆存储）
  - init_identity_auto() : 首次启动自动创建/恢复身份
  - recover_identity()   : 助记词恢复身份
  - get_identity_status(): 查询身份系统状态
  - check_llm_health()   : 检查 LLM 可用性
  - run_workbuddy()      : 运行 WorkBuddy 专家讨论
  - search_memory()      : 向量记忆语义搜索
  - forget_memory()      : 遗忘引擎
  - add_memory()         : 添加记忆（SQLite + 向量双写）
  - get_memory_stats()   : 获取记忆统计
  - update_emotion()     : 更新情绪状态
  - get_llm_info()       : 获取 LLM 配置信息
  - get_persona_state()  : 获取人格状态
  - _mnemo_words         : 最新生成的助记词
  - OPENAI_API_KEY       : OpenAI 兼容 API Key
"""

import asyncio
import hashlib
import os
import re
import json
import time
from typing import Optional, Callable, List, Tuple

from logger import get_logger
logger = get_logger("robin.orchestrator")

from config_loader import config

# ════════════════════════════════════════════════════════════
# 1. LLM 客户端初始化
# ════════════════════════════════════════════════════════════

from llm_client import LLMClient, RouterLLM

# SOTA 协作编排引擎（环境自适应 + 四层模型路由 + 5 拓扑）
from collaboration_engine import get_collaboration_engine, intent_is_collaborative

LLM_API_KEY = config.get("llm.api_key", "")
LLM_BASE_URL = config.get("llm.base_url", "https://api.openai.com/v1")
LLM_MODEL = config.get("llm.model", "gpt-4o-mini")
LLM_TIMEOUT = config.get("llm.timeout", 60.0)

OPENAI_API_KEY = config.get("openai.api_key", "")

# 主 LLM 客户端
_llm_client: Optional[LLMClient] = None
_router_llm: Optional[RouterLLM] = None

# ── 多模型提供商配置 ──
# 用户可通过 model=deepseek-chat 或 model=qwen-turbo 切换
# 默认使用主配置
MODEL_PROVIDERS = {
    "default": {
        "base_url": LLM_BASE_URL,
        "api_key": LLM_API_KEY,
        "model": LLM_MODEL,
    },
    "deepseek-chat": {
        "base_url": config.get("model_providers.deepseek.base_url", "https://api.deepseek.com/v1"),
        "api_key": config.get("model_providers.deepseek.api_key", ""),
        "model": "deepseek-chat",
    },
    "qwen-turbo": {
        "base_url": config.get("model_providers.qwen.base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
        "api_key": config.get("model_providers.qwen.api_key", ""),
        "model": "qwen-turbo",
    },
}

# 当前选中的模型提供商（默认 default）
_current_provider: str = "default"


def set_model_provider(provider_name: str) -> bool:
    """切换当前使用的模型提供商

    Args:
        provider_name: "default" | "deepseek-chat" | "qwen-turbo"

    Returns:
        是否切换成功
    """
    global _current_provider, _llm_client
    if provider_name not in MODEL_PROVIDERS:
        logger.warning(f"未知的模型提供商: {provider_name}，可用: {list(MODEL_PROVIDERS.keys())}")
        return False
    _current_provider = provider_name
    # 重置 LLM 客户端，下次调用时重新创建
    _llm_client = None
    logger.info(f"模型提供商已切换为: {provider_name} ({MODEL_PROVIDERS[provider_name]['model']})")
    return True


def get_current_provider() -> str:
    """获取当前模型提供商名称"""
    return _current_provider


def get_available_providers() -> list:
    """获取所有可用的模型提供商列表"""
    return list(MODEL_PROVIDERS.keys())


def _get_llm() -> LLMClient:
    global _llm_client
    if _llm_client is None:
        provider = MODEL_PROVIDERS[_current_provider]
        _llm_client = LLMClient(
            base_url=provider["base_url"],
            api_key=provider["api_key"],
            model=provider["model"],
            timeout=LLM_TIMEOUT,
        )
        # 跳过 /models probe（sfkey 中转没有此端点），直接认为可用
        _llm_client._available = True
    return _llm_client


def get_llm_info() -> dict:
    """返回 LLM 配置信息（不含 API Key）"""
    provider = MODEL_PROVIDERS[_current_provider]
    return {
        "base_url": provider["base_url"],
        "model": provider["model"],
        "timeout": LLM_TIMEOUT,
        "available": _llm_client is not None,
        "current_provider": _current_provider,
        "available_providers": list(MODEL_PROVIDERS.keys()),
    }


def check_llm_health() -> bool:
    """检查 LLM 是否可用（同步快速检查）"""
    try:
        client = _get_llm()
        if client._available is None:
            return True  # 还没探测过，乐观认为可用
        return client._available
    except Exception:
        return False


# ════════════════════════════════════════════════════════════
# 2. 身份系统 (Vault + 助记词)
# ════════════════════════════════════════════════════════════

from identity import generate as _identity_generate, verify as _identity_verify
from identity import derive_master_key as _derive_key

from vault import Vault

_vault: Optional[Vault] = None
_mnemo_words: list = []  # 最新生成的助记词（router.py 引用）
_identity_ready: bool = False
_identity_vault_path: str = os.path.join(
    os.path.dirname(__file__), "robin_identity.json"
)


def _load_identity() -> Optional[dict]:
    """从磁盘加载已保存的身份（含加密助记词哈希）"""
    if not os.path.exists(_identity_vault_path):
        return None
    try:
        with open(_identity_vault_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, Exception):
        return None


def _save_identity(data: dict):
    """保存身份数据到磁盘"""
    os.makedirs(os.path.dirname(_identity_vault_path), exist_ok=True)
    with open(_identity_vault_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_identity_status() -> dict:
    """查询身份系统状态"""
    global _identity_ready
    return {
        "ready": _identity_ready and _vault is not None,
        "has_vault": _vault is not None,
        "has_mnemo": len(_mnemo_words) > 0,
    }


async def init_identity_auto() -> bool:
    """首次启动：检测已有身份或创建新身份"""
    global _vault, _identity_ready, _mnemo_words

    # 1. 尝试加载已有身份
    identity_data = _load_identity()
    if identity_data and identity_data.get("identity_initialized"):
        # 身份已存在，Vault 密钥需从助记词重建
        # 但助记词不存磁盘（只存校验哈希），所以需要用户交互
        # 这里标记为未就绪，交 router 层处理
        _identity_ready = True
        logger.info("身份系统已就绪（已有身份文件）")
        return True

    # 2. 创建新身份
    try:
        words = _identity_generate()
        _mnemo_words = words
        # 创建设置 Vault
        master_key = _derive_key(words)
        _vault = Vault(master_key)
        # 保存身份元数据（不存助记词明文）
        _save_identity({
            "identity_initialized": True,
            "created_at": time.time(),
            "mnemo_checksum": hashlib.sha256(" ".join(words).encode()).hexdigest()[:16],
        })
        _identity_ready = True
        logger.info("新身份已创建（12 词助记词已生成）")
        return True
    except Exception as e:
        logger.error(f"身份创建失败: {e}")
        _identity_ready = False
        return False


async def recover_identity(mnemo_words: list) -> Tuple[bool, str]:
    """用助记词恢复身份"""
    global _vault, _identity_ready, _mnemo_words

    if len(mnemo_words) < 12:
        return False, "助记词不足 12 个"

    try:
        if not _identity_verify(mnemo_words):
            return False, "助记词校验失败"

        master_key = _derive_key(mnemo_words)
        _vault = Vault(master_key)
        _mnemo_words = mnemo_words
        _identity_ready = True

        # 保存身份元数据
        _save_identity({
            "identity_initialized": True,
            "recovered_at": time.time(),
            "mnemo_checksum": hashlib.sha256(" ".join(mnemo_words).encode()).hexdigest()[:16],
        })

        logger.info("身份已恢复（助记词验证通过）")
        return True, "身份恢复成功"
    except Exception as e:
        logger.error(f"身份恢复失败: {e}")
        return False, f"身份恢复失败: {e}"


def get_persona_state() -> dict:
    """获取人格状态（供 router 层查询）"""
    emotion_state = get_emotion_state_dict()
    identity_status = get_identity_status()
    return {
        "emotion": emotion_state,
        "identity": identity_status,
        "llm_available": check_llm_health(),
        "memory_count": 0,
    }


# ════════════════════════════════════════════════════════════
# 3. 情绪引擎
# ════════════════════════════════════════════════════════════

from emotion import get_emotion as _get_emotion_engine, EmotionState

_emotion_engine: Optional[EmotionState] = None


def _get_emotion() -> EmotionState:
    global _emotion_engine
    if _emotion_engine is None:
        _emotion_engine = _get_emotion_engine()
    return _emotion_engine


def update_emotion(emotion_tag: str) -> dict:
    """更新情绪状态，返回 {emotion, intensity}"""
    engine = _get_emotion()
    engine.update(emotion_tag)
    return engine.to_dict()


def get_emotion_state_dict() -> dict:
    """获取当前情绪状态 dict"""
    engine = _get_emotion()
    return engine.to_dict()


# ════════════════════════════════════════════════════════════
# 4. 记忆系统 (SQLite + 向量)
# ════════════════════════════════════════════════════════════

from memory import get_memory as _get_sql_memory, RobinMemory
from memory_vec import VectorMemory
from forget import ForgetEngine
from knowledge_graph import get_knowledge_graph as _get_kg

_sql_memory: Optional[RobinMemory] = None
_vec_memory: Optional[VectorMemory] = None
_forget_engine: Optional[ForgetEngine] = None

# 嵌入函数（使用 LLM 的 embedding 端点，或 fallback 简单哈希）
_EMBEDDING_DIM = 384


def _simple_embed(text: str) -> list:
    """简易嵌入函数 — 基于字符哈希的 384 维向量。
    当 LLM 不支持 embedding 时使用，确保向量记忆可用。
    """
    import hashlib
    dims = []
    for i in range(_EMBEDDING_DIM):
        h = hashlib.md5(f"{text}:{i}".encode()).hexdigest()
        val = (int(h[:8], 16) / 0xFFFFFFFF) * 2 - 1
        dims.append(val)
    # 归一化
    norm = sum(d * d for d in dims) ** 0.5
    if norm > 0:
        dims = [d / norm for d in dims]
    return dims


def _init_memory_system():
    """初始化所有记忆子系统"""
    global _sql_memory, _vec_memory, _forget_engine

    _sql_memory = _get_sql_memory()

    if _vault is not None:
        _vec_memory = VectorMemory(
            vault=_vault,
            embed_fn=_simple_embed,
        )
        _forget_engine = ForgetEngine(_vec_memory)
        logger.info("向量记忆系统已初始化")
    else:
        logger.warning("Vault 未初始化，向量记忆不可用（仅 SQLite 记忆）")


async def add_memory(role: str, text: str, emotion: str = "") -> None:
    """添加记忆（SQLite + 向量双写）"""
    # SQLite 记忆
    if _sql_memory:
        try:
            await _sql_memory.add(role, text, emotion)
        except Exception as e:
            logger.warning(f"SQLite 记忆写入失败: {e}")

    # 向量记忆（需 vault 初始化）
    if _vec_memory and _vault:
        try:
            await _vec_memory.add(role, text, emotion)
        except Exception as e:
            logger.warning(f"向量记忆写入失败: {e}")


async def search_memory(query: str, limit: int = 10, mode: str = "semantic", range_days: int = 1) -> list:
    """语义搜索记忆

    Args:
        query: 搜索查询
        limit: 最多返回条数
        mode: "semantic" | "keyword" | "date"
        range_days: 日期范围搜索时的天数
    """
    results = []

    if mode == "semantic" and _vec_memory:
        try:
            results = await _vec_memory.search(query, limit=limit)
        except Exception as e:
            logger.warning(f"向量记忆搜索失败: {e}")

    # 如果向量搜索为空或失败，回退到 SQLite 关键词搜索
    if not results and _sql_memory:
        try:
            rows = await _sql_memory.get_recent(limit=limit)
            # 简易关键词过滤
            q_lower = query.lower()
            results = []
            for role, text in rows:
                if q_lower in text.lower():
                    results.append({
                        "role": role,
                        "text": text,
                        "_source": "sqlite_kw",
                    })
        except Exception as e:
            logger.warning(f"SQLite 记忆搜索失败: {e}")

    return results


async def forget_memory(mode: str = "keyword", **kwargs) -> dict:
    """遗忘引擎入口

    Args:
        mode: "keyword" | "date_range" | "last_n" | "emotion"
        **kwargs: 传递给遗忘引擎的参数
    """
    if _forget_engine is None:
        return {"error": "遗忘引擎未初始化（需先设置身份）"}

    try:
        if mode == "keyword":
            keyword = kwargs.get("keyword", kwargs.get("query", ""))
            if not keyword:
                return {"error": "keyword 参数为空"}
            return await _forget_engine.forget_keyword(keyword)

        elif mode == "date_range":
            start = kwargs.get("start", kwargs.get("start_date", ""))
            end = kwargs.get("end", kwargs.get("end_date", ""))
            if not start or not end:
                return {"error": "start 和 end 参数必填"}
            return await _forget_engine.forget_date_range(start, end)

        elif mode == "last_n":
            n = kwargs.get("n", kwargs.get("count", 5))
            return await _forget_engine.forget_last_n(n)

        elif mode == "emotion":
            emotion = kwargs.get("emotion", "")
            if not emotion:
                return {"error": "emotion 参数为空"}
            return await _forget_engine.forget_by_emotion(emotion)

        else:
            return {"error": f"不支持的遗忘模式: {mode}"}
    except Exception as e:
        logger.error(f"遗忘操作失败: {e}")
        return {"error": str(e)}


async def get_memory_stats() -> dict:
    """获取记忆统计信息"""
    stats = {"sqlite": 0, "vector": 0, "kg": {}}

    # SQLite 统计
    if _sql_memory:
        try:
            rows = await _sql_memory.get_recent(limit=10000)
            # 从数据库直接 count
            stats["sqlite"] = len(rows) if len(rows) < 10000 else "10000+"
        except Exception:
            pass

    # 向量统计
    if _vec_memory:
        try:
            vec_stats = await _vec_memory.stats()
            stats["vector"] = vec_stats.get("total", 0)
        except Exception:
            pass

    # 知识图谱统计
    try:
        kg = _get_kg()
        kg_stats = await kg.get_stats()
        stats["kg"] = kg_stats
    except Exception:
        pass

    return stats


# ════════════════════════════════════════════════════════════
# 5. System Prompt 加载
# ════════════════════════════════════════════════════════════

from prompt_loader import get_system_prompt as _get_sp


def _build_system_prompt(user_text: str = "") -> str:
    """构建完整的系统提示词

    Args:
        user_text: 本次用户请求文本（用于企业级技能路由注入；可为空）
    """
    base_prompt = _get_sp("text")

    # 注入情绪状态
    emotion_state = get_emotion_state_dict()
    emotion_line = f"\n## 当前情绪状态\n当前情绪: {emotion_state.get('emotion', 'peaceful')}\n强度: {emotion_state.get('intensity', 1.0)}\n"

    prompt = base_prompt + emotion_line

    # 注入企业级技能调度指令（按本次用户意图路由；惰性导入，失败则跳过）
    if user_text:
        try:
            from superpowers_bridge import get_skill_router
            _router = get_skill_router()
            if _router is not None:
                directive = _router.build_directive(user_text)
                if directive:
                    prompt += "\n" + directive
        except Exception as _e:
            logger.debug("企业级技能指令注入跳过: %s", _e)

    # 注入上网调研能力 (SOTA 级 Web Research + GitHub 集成)
    try:
        research_prompt = """
## 🔍 上网调研能力
你有完整的上网调查研究和GitHub集成能力, 可通过 HTTP API 调用:

### 网络搜索与研究
- `POST /api/research/search` → 搜索互联网 (query, max_results)
- `POST /api/research/read` → 深度读取页面内容 (url, max_chars)
- `POST /api/research/investigate` → 全流程调查研究 (query, depth="standard")
  - 自动: 多查询 × 并行搜索 × 深度阅读 × 交叉验证 × 自验证
  - depth: "quick"(快速) | "standard"(标准) | "deep"(深度)
- `POST /api/research/wait` → 同步等待完整研究报告 (goal, depth)

### GitHub 集成
- `POST /api/research/github/search` → 搜索仓库 (query, language, min_stars)
- `POST /api/research/github/analyze` → 深度分析仓库 (repo="owner/repo")
  - 输出: 健康度评分、语言分布、贡献者、README摘要
- `POST /api/research/github/trending` → Trend榜单 (language, since)
- `POST /api/research/github/code` → 搜索代码 (query, language)

### 使用示例
- 调研新技术: POST /api/research/wait {"goal": "调研 LangGraph vs CrewAI 对比", "depth": "standard"}
- 搜开源项目: POST /api/research/github/search {"query": "video editing", "min_stars": 500}
- 分析仓库: POST /api/research/github/analyze {"repo": "owner/repo"}
- 快速搜索: POST /api/research/search {"query": "GLM-5.2 最新消息"}

**能力来源**: SOTA 级 Web Researcher + GitHub Bridge + Research Orchestrator
"""
        prompt += research_prompt
    except Exception as _e:
        logger.debug("上网调研 prompt 注入跳过: %s", _e)

    # 注入自主开发能力 (Agentic Dev Loop)
    try:
        dev_loop_prompt = """
## 🛠 自主开发能力
你有完整的自主开发能力, 可对任意项目执行 Fable5 开发循环:

### 核心入口
- `POST /api/dev/run` → 同步执行开发任务 {"goal": "...", "project": "项目名"}
- `POST /api/dev/start` → 异步启动开发 {"goal": "...", "project": "..."}
- `GET /api/dev/task/{id}` → 查异步任务状态

### 工作方式
1. 你说需求 → 我执行 Fable5 六步法循环 (Think→Diagnose→Fix→Verify→Review)
2. 每步自动调用 code_tools 读写文件和执行命令
3. 改完自动验证 (py_compile / 跑测试)
4. 发现问题自动修复再验证
5. 需要你确认时会 ask

### 支持的项目
- 知更鸟Agent, AutoAMV, CashFlow, 高考提分, 小米表盘

### 使用示例
- "帮我修 CashFlow 的支付宝支付bug"
- "给 AutoAMV 加一个导出功能"
- "优化知更鸟的桌面显示性能"
"""
        prompt += dev_loop_prompt
    except Exception as _e:
        logger.debug("开发循环 prompt 注入跳过: %s", _e)

    return prompt


# ════════════════════════════════════════════════════════════
# 6. 核心 AI 对话
# ════════════════════════════════════════════════════════════

from local_fallback import get_engine as _get_fallback

_fallback = _get_fallback()


# ★ 后端自动情绪分类（LLM 未输出标签时的 fallback）
def _detect_task_type(text: str) -> str:
    """从用户文本粗判任务类型, 供协作引擎选拓扑。"""
    t = (text or "").lower()
    if any(k in t for k in ["辩论", "debate", "评审", "review", "决策", "decision", "研究", "research"]):
        return "research"
    if any(k in t for k in ["重构", "refactor", "迁移", "migration"]):
        return "refactor"
    if any(k in t for k in ["内容", "文章", "文档", "doc", "content", "流水线", "pipeline"]):
        return "content"
    if any(k in t for k in ["自主", "进化", "evolve", "优化", "improve", "optimize"]):
        return "improve"
    if any(k in t for k in ["开发", "实现", "feature", "新功能", "写代码", "修", "fix", "修复", "bug", "协作", "团队"]):
        return "dev"
    return "dev"


def _classify_emotion(text: str) -> str:
    """基于关键词的回复情绪自动分类"""
    t = text.lower()
    # 困倦（优先匹配，避免与 sad 冲突）
    if any(w in t for w in ["晚安", "好眠", "困了", "想睡", "好困"]):
        return "sleepy"
    # 谢谢
    if any(w in t for w in ["谢谢", "感谢", "感激"]):
        return "grateful"
    # 惊讶
    if any(w in t for w in ["哇", "真的吗", "惊讶", "不敢相信", "天哪", "居然", "竟然"]):
        return "surprised"
    # 开心/积极
    if any(w in t for w in ["开心", "高兴", "快乐", "太好了", "真棒", "喜欢", "幸福", "喜悦", "欢笑", "兴奋"]):
        return "happy"
    # 消极/低落（不含"困"——避免冲突）
    if any(w in t for w in ["累", "辛苦", "疲惫", "难过", "伤心", "哭", "失落", "痛", "泪", "撑不住"]):
        return "sad"
    # 生气/不满
    if any(w in t for w in ["生气", "愤怒", "可恶", "烦", "讨厌", "火大"]):
        return "angry"
    # 思考/专注
    if any(w in t for w in ["让我想想", "考虑", "思考", "问题在于"]):
        return "thinking"
    # 担心/关心
    if any(w in t for w in ["担心", "关心", "还好吗", "放心", "别怕", "安全", "保护"]):
        return "concerned"
    # 顽皮/轻松
    if any(w in t for w in ["开玩笑", "嘻嘻", "哈哈", "逗你", "好玩"]):
        return "playful"
    # 鼓励/专注
    if any(w in t for w in ["加油", "努力", "坚持", "奋斗", "冲冲冲"]):
        return "focused"
    # 单字"困"（上一步未匹配到"困了/好困"才到这里）
    if "困" in t and "想" not in t:
        return "sleepy"
    return "peaceful"


async def call_ai(
    text: str,
    stream_callback: Optional[Callable[[str], None]] = None,
    conversation_messages: Optional[list] = None,
    model: Optional[str] = None,
) -> Tuple[str, str]:
    """核心 AI 对话函数

    流程:
      1. 构建 messages（system prompt + 记忆上下文 + 用户输入）
      2. 调用 LLM（流式/非流式）
      3. 解析情绪标签
      4. 存储记忆
      5. 返回 (reply_text, emotion_tag)

    Args:
        text: 用户输入文本
        stream_callback: 流式回调，每收到一个 token 调用
        conversation_messages: 可选的完整对话历史（OpenAI 兼容模式）
        model: 可选的模型提供商名称（如 "deepseek-chat"、"qwen-turbo"），
               用于临时切换模型。如果为 None，则使用当前默认模型。

    Returns:
        (reply_text, emotion_tag)
    """
    if not text.strip():
        return "嗯？", "peaceful"

    # ── 输入长度检查 ──
    if len(text) > 10000:
        logger.warning("用户输入过长 (%d chars)，已截断至 10000 字符", len(text))
        text = text[:10000]

    # ── 模型切换逻辑 ──
    original_provider = _current_provider
    if model and model in MODEL_PROVIDERS:
        set_model_provider(model)
        logger.info(f"本次对话临时切换模型为: {model}")
    elif model:
        logger.warning(f"未知模型 '{model}'，使用当前默认模型: {_current_provider}")

    # ── SOTA 协作引擎门控 ──
    # 开发/协作类任务自动进入多智能体协作流（环境自适应选拓扑 + 四层模型路由），
    # 普通闲聊仍走单 LLM 对话。仅 WebSocket 聊天模式触发（OpenAI 兼容模式不劫持）。
    if not conversation_messages and intent_is_collaborative(text):
        try:
            engine = get_collaboration_engine()
            ttype = _detect_task_type(text)
            run = await engine.dispatch(objective=text, task_type=ttype, on_event=None)
            synth = (run.get("result") or {}).get("synthesis", "")
            if not synth:
                synth = json.dumps(run.get("result", {}), ensure_ascii=False)[:1500]
            strat = run.get("strategy", "ORCHESTRATOR_WORKER")
            header = f"【知更鸟协作 · {strat}】\n"
            await add_memory("user", text, "focused")
            await add_memory("assistant", synth, "focused")
            return f"<emotion:focused>{header}{synth}", "focused"
        except Exception as _ce:
            logger.warning("协作引擎门控失败, 回退普通对话: %s", _ce)
            # 继续走下方普通 call_ai 流程

    try:
        # ── 构建消息列表 ──
        messages = []

        if conversation_messages:
            # OpenAI 兼容模式：使用传入的完整消息列表
            # 先注入 system prompt（如果第一条不是 system）
            if not conversation_messages or conversation_messages[0].get("role") != "system":
                system_prompt = _build_system_prompt(text)
                messages.append({"role": "system", "content": system_prompt})
            messages.extend(conversation_messages)

        else:
            # WebSocket 聊天模式：自动构建
            system_prompt = _build_system_prompt(text)
            messages.append({"role": "system", "content": system_prompt})

            # 注入记忆上下文
            if _sql_memory:
                try:
                    history = await _sql_memory.get_recent_context(limit=10)
                    if history:
                        messages.append({
                            "role": "system",
                            "content": f"## 近期对话上下文\n{history}\n",
                        })
                except Exception as e:
                    logger.warning(f"获取记忆上下文失败: {e}")

            # 注入知识图谱上下文
            try:
                kg = _get_kg()
                kg_ctx = await kg.to_context(limit=20)
                if kg_ctx:
                    messages.append({
                        "role": "system",
                        "content": f"## 知识图谱\n{kg_ctx}\n",
                    })
            except Exception as e:
                logger.warning(f"获取知识图谱失败: {e}")

            # 注入结构化事实
            if _sql_memory:
                try:
                    facts = await _sql_memory.recall_structured(limit=15)
                    if facts:
                        messages.append({
                            "role": "system",
                            "content": f"## 关于你的记忆\n{facts}\n",
                        })
                except Exception as e:
                    logger.warning(f"获取结构化事实失败: {e}")

            messages.append({"role": "user", "content": text})

        # ★ 在最后一条 user 消息后追加格式指令（GLM 对 system 消息免疫，但紧跟 user 的格式描述最有效）
        for i in range(len(messages) - 1, -1, -1):
            if messages[i].get("role") == "user":
                last = messages[i]
                last["content"] = (
                    (last["content"] if isinstance(last["content"], str) else "")
                    + "\n\n---\n【格式要求】你必须以 <emotion:xxx> 开头回复。标签：peaceful happy focused concerned surprised thinking playful sad angry shy sleepy excited grateful"
                )
                break

        # ── 调用 LLM ──
        llm = _get_llm()
        reply_text = None

        try:
            if stream_callback:
                reply_text = await llm.chat_stream(messages, callback=stream_callback)
            else:
                reply_text = await llm.chat(messages)
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}", exc_info=True)

        # ── Fallback ──
        if not reply_text:
            logger.warning("LLM 返回空，使用 local fallback")
            reply_text = _fallback(text)

        # ── 解析情绪标签 ──
        emotion_tag = "peaceful"
        clean_reply = reply_text      # 记忆用（纯净文本）
        reply_frontend = reply_text   # 返回给前端（带标签）

        # 解析 <emotion:xxx> 标签（如果 LLM 输出了）
        emotion_match = re.search(r'<emotion:(\w+)>', reply_text)
        if emotion_match:
            emotion_tag = emotion_match.group(1).lower()
            # 标准化情绪标签
            valid_emotions = {"peaceful", "happy", "focused", "concerned",
                              "surprised", "thinking", "playful", "sad",
                              "angry", "shy", "sleepy", "excited", "grateful"}
            if emotion_tag not in valid_emotions:
                emotion_tag = "peaceful"
            # 保留标签供前端解析，存记忆时剥离
            clean_reply = re.sub(r'<emotion:\w+>\s*', '', reply_text).strip()
            reply_frontend = reply_text
        else:
            # ★ LLM 未输出标签 → 后端自动分类
            emotion_tag = _classify_emotion(reply_text)
            # 把标签写回文本供前端 emotionBridge 解析
            reply_frontend = f"<emotion:{emotion_tag}>{reply_text}"

        logger.info(f"情绪分类完成: {emotion_tag} | 来源: {'LLM标签' if emotion_match else '后端分类'}")

        # ── 更新情绪状态 ──
        update_emotion(emotion_tag)

        # ── 存储记忆（存纯净文本，不含标签）──
        # 非 OpenAi 兼容模式（即 conversation_messages 为空时）自动存储
        if not conversation_messages:
            await add_memory("user", text, emotion_tag)
            await add_memory("assistant", clean_reply, emotion_tag)

        # ── 检测 <emotion> 标签并自动触发 TTS ──
        # 如果回复中包含 <emotion> 标签，自动调用 Edge TTS 合成语音
        if '<emotion' in reply_frontend:
            try:
                # 提取纯净文本（去掉所有标签）
                tts_text = re.sub(r'<[^>]+>', '', reply_frontend).strip()
                if tts_text:
                    # 异步调用 TTS，不阻塞主流程
                    asyncio.create_task(_auto_tts(tts_text))
            except Exception as e:
                logger.warning(f"自动 TTS 触发失败: {e}")

        return reply_frontend, emotion_tag

    finally:
        # 如果临时切换了模型，恢复为原始提供商
        if model and model in MODEL_PROVIDERS and original_provider != _current_provider:
            set_model_provider(original_provider)
            logger.info(f"对话结束，恢复模型为: {original_provider}")


# ── 自动 TTS 函数 ──
async def _auto_tts(text: str, voice: str = "zh-CN-XiaoxiaoNeural", rate: str = "+0%"):
    """自动调用 Edge TTS 合成语音并广播音频数据

    Args:
        text: 要合成的文本
        voice: 语音名称
        rate: 语速
    """
    try:
        import edge_tts
        communicate = edge_tts.Communicate(text, voice=voice, rate=rate)
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        if audio_data:
            # 广播音频数据给所有连接的 WebSocket 客户端
            from router import broadcast
            import json
            await broadcast(json.dumps({
                "type": "tts_audio",
                "audio": audio_data.hex(),
                "text": text,
            }))
            logger.info(f"自动 TTS 完成: {text[:30]}...")
    except Exception as e:
        logger.warning(f"自动 TTS 失败: {e}")


# ════════════════════════════════════════════════════════════
# 7. WorkBuddy 专家讨论
# ════════════════════════════════════════════════════════════

from workbuddy import WorkBuddy

_wb: Optional[WorkBuddy] = None


def _get_workbuddy() -> WorkBuddy:
    global _wb
    if _wb is None:
        _wb = WorkBuddy(
            llm_client=_get_llm(),
            conv_engine=None,
            memory=_sql_memory,
        )
    return _wb


async def run_workbuddy(topic: str, on_message: Optional[Callable] = None):
    """运行 WorkBuddy 专家团队讨论"""
    wb = _get_workbuddy()
    await wb.start_project(topic, on_message=on_message)


# ════════════════════════════════════════════════════════════
# 8. 初始化
# ════════════════════════════════════════════════════════════

# 模块导入时自动初始化

# 尝试自动初始化身份
try:
    identity_data = _load_identity()
    if identity_data and identity_data.get("identity_initialized"):
        _identity_ready = True
        logger.info("身份系统已就绪")
except Exception:
    pass

# 尝试初始化记忆系统
_init_memory_system()

logger.info(
    "Orchestrator v3.2 已加载 | "
    f"模型: {LLM_MODEL} | "
    f"身份: {'就绪' if _identity_ready else '未初始化'} | "
    f"记忆: {'SQLite+向量' if _vec_memory else '仅SQLite'}"
)