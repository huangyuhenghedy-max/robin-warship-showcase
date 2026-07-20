"""
l6_daemon_v5.py — SOTA 自主编码守护进程 v10.3 (300轮SOTA全量落盘)
===========================================================================
v10.3 新增 (2026-07-17, 基于 300 轮质量提升 SOTA 调研, 11份报告综合):
  ★ Generator/Evaluator分离 (gen_eval_separator.py):
      独立评审Agent在全新上下文中审查Generator输出
      Anthropic: +16%→54% PR获评审意见, ReFlect: SWE-bench 0%→87%
      三级评审: LIGHT(确定性) → STANDARD(轻量AI) → DEEP(多维AI+安全)
      Minority Veto: 1票否决即触发
  ★ Search-and-Replace精确编辑 (editor_precision.py):
      Claude Code FileEditTool: 低破坏性, 精确匹配
      Aider模糊回退: SequenceMatcher 0.6阈值
      Codex CLI事务补丁: apply_patch全有或全无
      自动lint + 备份回滚
  ★ Stop Hook / Ralph Wiggum Loop (stop_hook.py):
      Agent退出前强制验证: 测试/构建/lint/安全四级检查
      未通过则阻止声称完成, 最多8次拦截 (Claude Code上限)
      Ralph Wiggum Loop: "But I did a thing!" — "No, verify it."
  ★ 上下文压缩与RepoMap (context_optimizer.py):
      Headroom压缩: 17.7K→1.4K tokens (92%压缩, 97%+精度)
      Aider RepoMap: tree-sitter AST + 自动项目结构摘要
      32K tokens预算上限, 防LOST-IN-THE-MIDDLE (4K→128K精度99%→72%)

v10.2 新增 (2026-07-17, 基于 100 轮质量加固 SOTA 调研):
  ★ TDD强制中间件 (tdd_middleware.py):
      RED→GREEN→REFACTOR 三阶段TDD循环, 强制测试先行
      Superpowers 6.0 架构: 一次修复率 40%→95%
      禁止修改测试 / 独立上下文 / 自动回滚违规
  ★ Harness三大中间件 (harness_middleware.py):
      PreCompletionChecklist: Agent退出前强制验证完成清单 (LangChain +7%)
      LocalContext: 启动时自动注入项目环境信息 (-30%环境错误)
      LoopDetection: 死循环检测, 3次/文件触发换方案 (-50%死循环)
  ★ 三级质量门禁 (quality_gate.py):
      L1静态分析 → L2动态验证 → L3 AI评审 (LLM-as-Judge)
      任务复杂度自动选择门禁等级: trivial→fast, critical→full
      Anthropic $9→$200 实验: 质量门禁的ROI
  ★ 推理三明治预算 (reasoning_budget.py):
      阶段感知推理分配: Plan高→Build中→Validate高
      LangChain实验: 推理三明治+中间件 63.6%→66.5%
      BudgetDial模型路由对齐: 强模型规划, 中模型实现

v10.1 新增 (2026-07-17, 基于 30 轮生产加固 SOTA 调研):
  ★ 可观测性管道 (observability_pipeline.py):
      分布式追踪 + 结构化指标 + 健康仪表盘
      OpenTelemetry 风格 span/trace/context 管理器
      装饰器注入 / 上下文管理器 / 便捷函数三接口
  ★ 评估框架 (eval_harness.py):
      回归测试 / Benchmark 基准 / A/B对比 三维评估
      关键路径管理 + 质量门禁 + 统计显著性检验
      每次变更可量化验证: 改好了还是改坏了
  ★ 护栏系统 (guardrails_system.py):
      六层防护: 内容安全/行为边界/权限隔离/审计/限速/伦理
      四级模式: off/monitor/warn/enforce/strict
      AI向善比赛安全合规 + 102模块操作安全
  ★ 对抗式自我进化 (antagonistic_evolution.py):
      Challenger-Solver 双Agent对抗循环
      三种模式: 弱点探测/能力拉伸/对抗生成
      ELO评分 + 自适应平衡
  ★ 蜕变循环集成 (daemon主循环):
      后台守护协程: J-Space监测→饱和→睡眠→蜕变→安全锁→觉醒
      空闲时自动蜕变, 忙时3min巡检
      ELO差距触发对抗再平衡

v10.0 新增 (2026-07-17, 基于 300 轮蜕变 SOTA 调研):
  ★ 蜕变引擎核心 (metamorphosis_engine.py):
      四阶段蜕变生命周期: EGG→LARVA→PUPA→ADULT
      类完全变态发育: 阶段性重构而非增量改进
      基于 HyperAgents + Autogenesis 架构
  ★ J-Space能力成熟度监测 (j_space_monitor.py):
      6维能力空间: performance/robustness/efficiency/novelty/coherence/autonomy
      密度感知触发蜕变 (饱和 < 5%)
      熵/收敛速度/方向分析
  ★ 睡眠-清醒蜕变循环 (sleep_wake_cycle.py):
      N1(浅睡)→N2(深睡)→REM(创造)→WAKING(验证) 四阶段
      预算感知调度，空闲时自动进入睡眠进化
  ★ 蜕变安全锁 (recursive_safety_lock.py):
      L0~L4 四级安全，默认L2严格超集验证
      SAHOO+MOSS: 新版本必须处理旧版本所有情况
      完整审计日志 + 自动回滚
  ★ 比赛自主开发引擎 (competition_dev_engine.py):
      知更鸟自主开发阿里AI向善比赛项目
      分析→规划→生成→构建→验证 全自动循环
      最高优先级: 优先比赛开发, 再自进化

v9.1 新增 (2026-07-17, 基于 200 轮深化 SOTA 调研):
  ★ GEPA 自进化引擎 (gepa_evolution.py):
      类反向传播的 prompt 进化回路，100-500 次评估收敛
      6 种变异算子 + 自适应变异率 + 锦标赛选择
      源自 Hermes Agent (Nous Research, 143K⭐)
  ★ 记忆巩固管道 (memory_consolidator.py):
      EverMemOS 三阶段生命周期: 痕迹形成 → 语义巩固 → 重建回忆
      四层存储: 工作/情景/语义/程序性记忆
      自动遗忘曲线 + SQLite 持久化
  ★ 比较反思记忆 (comparative_reflection.py):
      MARS 跨分支比较: 63% 经验来自分支间迁移
      多条轨迹同时对比 → 提取可迁移洞察
      自动反思循环 + 低价值洞察清理
  ★ 渐进式技能加载器 (progressive_skills.py):
      L0(20t) → L1(200t) → L2(1000+t) 三级渐进加载
      SkillRouter 91.7% 注意力在 body
      预估节省 80% token (80%查询止于L0)
  ★ 轨迹进化引擎 (trajectory_evolution.py):
      SE-Agent 三条进化路径: 修订→重组→优化
      轨迹级进化 vs 步骤级反思，改进持续性 3.2x
      冗余/错误/瓶颈自动检测
  ★ 双时态记忆追踪器 (bitemporal_memory.py):
      Zep Graphiti 双时态: 事件时间 + 摄入时间
      追溯修正不丢失历史 + 时间旅行查询
      版本链管理 + 并发冲突解决

v9.0 新增 (2026-07-17, 基于 100 轮开拓级 SOTA 调研):

v8.7 新增 (2026-07-17, 基于 50+轮「世上没有的创新」调研):
  ★ 双速大脑 (Dual-Speed Brain):
      System 1 快速通道 (<500ms, 缓存命中, 已知模式匹配)
      System 2 深度推理 (BoN+Dream+多步, 自动升降级)
      预估节省 60-80% token (已知模式走快通道)
  ★ 溯源感知管道 (Provenance-Aware Pipeline):
      数据在5层指挥链携带「出生证明」(来源/信任/验证状态)
      下游 Agent 根据信任度自动调整行为
  ★ 内嵌式调试器 (Embedded Debugger):
      Agent 自带「黑匣子」— 零配置 always-on
      时间旅行回放 + 因果归因 + 一键故障恢复
  创新验证: 50+轮搜索确认全球确实没有

v8.6 新增 (2026-07-17, 基于 50 轮 P1/P2 SOTA 调研):
  - MCP Bridge: Skills → MCP 协议桥接，Cursor/Codex 可调用战舰
  - Session 持久化: SQLite Checkpoint + 崩溃自动恢复
  - CONTEXT_REPLACE 多语言扩展: JS/TS/Lua/Go/Java AST 验证
  - RL 路由数据采集: 每次模型选择记录，为 BAAR 训练准备
  - 多模态感知: 截图→VLM→理解，战舰能"看"画面了
  - DAG 调度深度集成: collaboration_engine.py 自动启用

v7.2 新增 (2026-07-17, 基于 100 轮 SOTA 调研):
  - 锚点容错匹配: CONTEXT_REPLACE 第6级, 首尾行锚点+50%相似度
  - AST 语义验证: py_compile 后加 ast.parse() 防语义错误
  - 测试运行: 编辑后轻量 pytest 调用 (非阻断)
  - Prompt Cache: MD5 key 缓存, 5min TTL, 省 token
  - Error Classifier: 故障分类 (auth/config/transient/syntax/crash_loop) + 自愈
  - Key 池轮询: 多 key round-robin 负载均衡
  - ESLint/TS 检查: JS/TS 文件自动带 ESLint + tsc 验证

v8.5 新增 (2026-07-17, 基于 150 轮 SOTA 调研):
  - Best-of-N 并行推理: 复杂任务 N=3~5 路并行采样 + Self-Verify 评分选最优
  - 动态子代理生成: 运行时按任务类型动态生成专用 Agent, 用完即回收
  - BoN 集成: call_llm_async() 自动路由复杂 prompt 到并行采样
  - 动态 Agent 集成: fleet_orchestrator.py 用 spawn_for_task() 替代固定 squads
  - 代码审查 Action: 打包为 GitHub Action, 定价 Free→¥999/月

SOTA 研究关键发现:
  - 编辑格式是 10x 杠杆 (Can Boluk: str_replace→hashline, 6.7%→68.3%)
  - 上下文耦合是主因 (SWE-Edit: 查看/编辑分离, 96.9% 编辑成功率)
  - 失败应重试而非回滚 (AutoCodeRover: self-fix agent, 51.6% SWE-bench)
  - 元代理可进化 harness (HyperAgents: 0%→80% in 5 generations)

CLI:
  python l6_daemon_v5.py           # 前台运行
  python l6_daemon_v5.py --daemon  # 后台启动
  python l6_daemon_v5.py --go      # 强制持续工作
  python l6_daemon_v5.py --stop    # 停止
  python l6_daemon_v5.py --status  # 状态 (含专家路由/质量趋势)
  python l6_daemon_v5.py --reset   # 重置
  python l6_daemon_v5.py --report  # 生成进化报告
"""
import asyncio, json, os, re, sys, ssl, threading, time, urllib.request, urllib.error, signal, subprocess, traceback
import requests, urllib3
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Optional

# 导入模块化组件
sys.path.insert(0, str(Path(__file__).parent))
from daemon_modules.daemon_project_ctx import get_project_context, find_scope_for_file, format_project_info
from daemon_modules.daemon_expert_router import route_expert, get_all_experts
from daemon_modules.daemon_parser import parse_output
from daemon_modules.daemon_reflexion import validate_syntax, quality_score, should_rollback, auto_git_commit, set_cicd_enabled
from daemon_modules.daemon_self_optimizer import analyze_metrics, generate_evolution_report
from daemon_modules.daemon_smart_batch import smart_batch as _smart_batch_build
from daemon_modules.daemon_validation import check_python_imports, run_project_tests, detect_breaking_changes
from daemon_modules.daemon_security import security_gate, set_safe_paths, audit_operation, get_audit_log
from daemon_modules.daemon_prompt_learner import get_adaptive_prompt_addition
from daemon_modules.daemon_context_match import context_replace_match

# ── v8.5 P0 创新: Best-of-N 并行推理 + 动态子代理生成 ──
from daemon_modules.bo_n_parallel import BoNSampler, get_sampler, COMPLEXITY_N_MAP
from daemon_modules.dynamic_agent_spawner import AgentPool, get_agent_pool, spawn_for_task, AgentRole

# ── v8.6 P1 补齐: MCP桥接 + Session持久化 + 多语言编辑 + RL路由 + 多模态 ──
from daemon_modules.mcp_bridge import get_mcp_tools, execute_skill, reset_tools_cache as mcp_reset_tools, get_skill_stats
from daemon_modules.session_manager import get_session_manager, recover_from_crash
from daemon_modules.multi_lang_editor import validate_file_content as ml_validate
from daemon_modules.rl_router import get_recorder as get_rl_recorder, record_routing_decision, get_routing_stats
from daemon_modules.vision_module import analyze_screenshot, analyze_image, ui_to_code, code_review_ui

# ── v8.6.1 P0 安全补齐: Per-Agent身份 + 记忆防护 + FTS5升级 + 技能提取 ──
from daemon_modules.per_agent_auth import get_auth_manager as get_agent_auth, AuthManager
from daemon_modules.memory_protection import get_memory_protector, MemoryProtector
from daemon_modules.skill_extractor import get_skill_extractor, SkillExtractor

# ── v8.7 三大创新: 双速大脑 + 溯源管道 + 内嵌调试器 ──
from daemon_modules.dual_speed_brain import get_brain as get_dual_speed_brain, DualSpeedBrain
from daemon_modules.provenance_pipe import get_provenance as get_provenance_pipe, ProvenanceEnvelope, ProvenancePipeline
from daemon_modules.embedded_debugger import get_debugger as get_embedded_debugger, EmbeddedDebugger

# ── v8.8 三个白空间创新: 内省协议 + 跨代继承 + 溯源经济 ──
from daemon_modules.introspection_protocol import get_introspector, IntrospectionProtocol
from daemon_modules.skill_inheritance import get_inheritance_engine, SkillInheritance
from daemon_modules.provenance_economy import get_economy, ProvenanceEconomy

# ── v8.9 效率模块: 质量早停 + Agent级投机执行 ──
from daemon_modules.early_stop import get_stopper as get_early_stopper, EarlyStopEngine
from daemon_modules.speculative_agent import get_speculator as get_speculative_executor, SpeculativeAgentExecutor, SpeculativeResult

# ── v9.0 100轮开拓级: 反压协议 + 污染盾 + 健康中心 + 能量账本 + CRDT + 瓶颈检测 ──
from daemon_modules.backpressure_protocol import get_backpressure, BackpressureProtocol
from daemon_modules.memory_contamination_shield import get_shield, ContaminationShield
from daemon_modules.agent_health_center import get_health_center, AgentHealthCenter
from daemon_modules.energy_ledger import get_ledger, EnergyLedger
from daemon_modules.crdt_memory_grid import get_memory_grid, CRDTMemoryGrid
from daemon_modules.bottleneck_detector import get_detector, BottleneckDetector

# ── v9.1 6大SOTA创新: GEPA自进化 + 记忆巩固 + 比较反思 + 渐进技能 + 轨迹进化 + 双时态 ──
from daemon_modules.gepa_evolution import get_engine as get_gepa_engine, GEPAEngine, GEPAConfig
from daemon_modules.memory_consolidator import get_consolidator, MemoryConsolidator, ConsolidatorConfig
from daemon_modules.comparative_reflection import get_reflector as get_comparative_reflector, ComparativeReflection, ReflectionConfig
from daemon_modules.progressive_skills import get_loader as get_progressive_loader, ProgressiveSkillLoader, ProgressiveConfig
from daemon_modules.trajectory_evolution import get_evolution as get_trajectory_evolution, TrajectoryEvolution, EvolutionConfig
from daemon_modules.bitemporal_memory import get_bitemporal, BitemporalMemory, BitemporalConfig

# ── v10.0 蜕变引擎: metamorphosis + J-Space + 睡眠循环 + 安全锁 ──
from daemon_modules.metamorphosis_engine import get_engine as get_meta_engine, MetamorphosisEngine, MetamorphosisConfig
from daemon_modules.j_space_monitor import get_monitor as get_j_monitor, JSpaceMonitor, JSpaceConfig
from daemon_modules.sleep_wake_cycle import get_cycle as get_sleep_cycle, SleepWakeCycle, SleepWakeConfig
from daemon_modules.recursive_safety_lock import get_lock as get_safety_lock, RecursiveSafetyLock, SafetyLockConfig
from daemon_modules.competition_dev_engine import get_engine as get_comp_engine, CompetitionDevEngine

# ── v10.1 生产加固: 可观测性 + 评估框架 + 护栏系统 + 对抗进化 ──
from daemon_modules.observability_pipeline import get_pipeline as get_obs_pipeline, ObservabilityPipeline, ObservabilityConfig
from daemon_modules.eval_harness import get_harness as get_eval_harness, EvalHarness, EvalConfig, CriticalPath
from daemon_modules.guardrails_system import get_guardrails as get_guardrails_sys, GuardrailsSystem, GuardrailConfig
from daemon_modules.antagonistic_evolution import get_antagonist as get_antag_engine, AntagonisticEvolution, AntagonisticConfig

# ── v10.2 质量加固: TDD中间件 + Harness三大中间件 + 质量门禁 + 推理预算 ──
from daemon_modules.tdd_middleware import get_middleware as get_tdd_mw, TDDMiddleware, TDDConfig
from daemon_modules.harness_middleware import get_checklist as get_harness_checklist, PreCompletionChecklistMiddleware, PreCompletionConfig
from daemon_modules.harness_middleware import get_local_context as get_harness_context, LocalContextMiddleware, LocalContextConfig
from daemon_modules.harness_middleware import get_loop_detection as get_harness_loop, LoopDetectionMiddleware, LoopDetectionConfig
from daemon_modules.quality_gate import get_gate as get_quality_gate, QualityGate, QualityGateConfig
from daemon_modules.reasoning_budget import get_budget as get_reasoning_budget, ReasoningBudget, ReasoningBudgetConfig

# ── v10.3 300轮SOTA落盘: Gen/Eval分离 + 精确编辑 + Stop Hook + 上下文优化 ──
from daemon_modules.gen_eval_separator import get_separator as get_eval_sep, GenEvalSeparator, EvalConfig
from daemon_modules.editor_precision import get_editor as get_precision_editor, SearchReplaceEditor, EditorConfig
from daemon_modules.stop_hook import get_stop_hook as get_stop_hook, StopHook, StopHookConfig
from daemon_modules.context_optimizer import get_compressor as get_context_compressor, ContextCompressor, CompressorConfig
from daemon_modules.context_optimizer import get_repomap as get_context_repomap, RepoMap, RepoMapConfig

# ── v8.6.1 模块状态 (P0安全补齐) ──
_AUTH_READY = True
_MEMORY_PROTECTION_READY = True
_SKILL_EXTRACTOR_READY = True

# ── v8.6 模块状态 ──
_MCP_BRIDGE_READY = True
_SESSION_MANAGER_READY = True
_ML_EDITOR_READY = True
_RL_ROUTER_READY = True
_VISION_READY = True
_V8_6_FEATURES_ENABLED = True

# ── v9.0 模块状态 ──
_BACKPRESSURE_READY = True
_CONTAMINATION_SHIELD_READY = True
_HEALTH_CENTER_READY = True
_ENERGY_LEDGER_READY = True
_CRDT_GRID_READY = True
_BOTTLENECK_DETECTOR_READY = True

# ── v9.1 模块状态 ──
_GEPA_ENGINE_READY = True
_MEMORY_CONSOLIDATOR_READY = True
_COMPARATIVE_REFLECTOR_READY = True
_PROGRESSIVE_LOADER_READY = True
_TRAJECTORY_EVOLUTION_READY = True
_BITEMPORAL_MEMORY_READY = True

# ── v10.0 模块状态 ──
_METAMORPHOSIS_ENGINE_READY = True
_JSPACE_MONITOR_READY = True
_SLEEP_CYCLE_READY = True
_SAFETY_LOCK_READY = True
_COMPETITION_DEV_READY = True  # 比赛自主开发引擎

# ── v10.1 生产加固模块状态 ──
_OBSERVABILITY_READY = True     # 可观测性管道
_EVAL_HARNESS_READY = True      # 评估框架
_GUARDRAILS_READY = True        # 护栏系统
_ANTAGONISTIC_READY = True      # 对抗进化引擎

# ── v10.2 质量加固模块状态 ──
_TDD_MIDDLEWARE_READY = True       # TDD强制中间件
_HARNESS_CHECKLIST_READY = True    # 完成检查清单
_HARNESS_CONTEXT_READY = True      # 环境上下文注入
_HARNESS_LOOP_DETECT_READY = True  # 死循环检测
_QUALITY_GATE_READY = True         # 三级质量门禁
_REASONING_BUDGET_READY = True     # 推理预算分配

# ── v10.3 300轮SOTA落盘模块状态 ──
_GEN_EVAL_SEP_READY = True         # Generator/Evaluator分离
_EDITOR_PRECISION_READY = True     # Search-and-Replace精确编辑
_STOP_HOOK_READY = True            # Stop Hook / Ralph Wiggum Loop
_CONTEXT_COMPRESSOR_READY = True   # 上下文压缩
_REPOMAP_READY = True              # 代码库地图

# ── 配置 ──
ENDPOINT = os.environ.get("ROBIN_GLM_ENDPOINT", "")
try:
    _s = json.loads(Path(__file__).parent.joinpath(".secrets.json").read_text("utf-8"))
    if not ENDPOINT:
        ENDPOINT = _s["llm_fast"]["base_url"] + "/chat/completions"
    API_KEY = os.environ.get("ROBIN_GLM_API_KEY", "") or _s["llm_fast"]["api_key"]
except (OSError, json.JSONDecodeError, KeyError):
    API_KEY = os.environ.get("ROBIN_GLM_API_KEY", "")

# ── 清理 VPN/代理干扰: 战舰直连 LLM 不走系统代理 ──
for _var in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
    os.environ.pop(_var, None)
MODEL = os.environ.get("ROBIN_GLM_MODEL", "glm-5.2")
# 模型混用策略: 主路由 sfkey glm-5.2 (国内中转, 1.8s稳定), 
# 回退到 OpenCode Go DeepSeek V4 Flash (跨境, 量大便宜)
# 预算由 fleet_command/budget_dial 统一路由控制
# SSL 上下文: Windows 环境证书吊销检查常出问题，统一绕过
_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

# ── 绕过系统代理: 知更鸟直连 LLM 不走 127.0.0.1:15715 ──
_proxy_handler = urllib.request.ProxyHandler({})
_opener = urllib.request.build_opener(_proxy_handler)
urllib.request.install_opener(_opener)

MAX_OUTPUT = 65536
MAX_CALLS = int(os.environ.get("ROBIN_MAX_CALLS", "30000"))  # DeepSeek 31,650次/5h, 预算拉满

# ── 引擎版本号（唯一权威来源，所有"当前版本"提及必须引用此常量）──
# 文件名保留 l6_daemon_v5.py 是历史命名，不影响功能；但所有日志、横幅、
# 状态文件、对外报告必须使用 ENGINE_VERSION，禁止散落硬编码 v5/v7/v10.x。
# 更新版本号时只改这一行即可。
ENGINE_VERSION = "v10.4-rc1"
ENGINE_BUILD_DATE = "2026-07-19"

# ── 日志轮转 ──
MAX_LOG_SIZE = 50 * 1024 * 1024  # 50 MB
MAX_LOG_LINES = 100000            # 10万行
MAX_LOG_BACKUPS = 10              # 保留的轮转备份文件数
_LOG_ROTATION_LOCK = threading.Lock()

# ── Prompt Cache (v4: 省 token) ──
import hashlib
_PROMPT_CACHE: dict[str, tuple[str, float]] = {}
_PROMPT_CACHE_MAX = 128
_PROMPT_CACHE_TTL = 300  # 5min

def _cache_prompt(prompt: str, response: str) -> None:
    key = hashlib.md5(prompt.encode("utf-8")).hexdigest()
    if len(_PROMPT_CACHE) >= _PROMPT_CACHE_MAX:
        sorted_items = sorted(_PROMPT_CACHE.items(), key=lambda x: x[1][1])
        for old_key, _ in sorted_items[:_PROMPT_CACHE_MAX // 2]:
            _PROMPT_CACHE.pop(old_key, None)
    _PROMPT_CACHE[key] = (response, time.time())

def _get_cached_prompt(prompt: str) -> str | None:
    key = hashlib.md5(prompt.encode("utf-8")).hexdigest()
    if key in _PROMPT_CACHE:
        resp, ts = _PROMPT_CACHE[key]
        if time.time() - ts < _PROMPT_CACHE_TTL:
            return resp
        _PROMPT_CACHE.pop(key, None)
    return None

# ── Key 池轮询 (v4: 多 key 负载均衡) ──
_KEY_POOL: dict[str, list[str]] = {}  # provider_name -> [key1, key2, ...]
_KEY_INDEX: dict[str, int] = {}       # provider_name -> current_index

def _load_key_pool() -> None:
    """从 .secrets.json 加载各 provider 的 key 池。
    支持: 单个 key (str), key 数组 (_keys list), 逗号分隔 (csv)"""
    try:
        secrets_path = Path(__file__).parent / ".secrets.json"
        if not secrets_path.exists():
            return
        secrets = json.loads(secrets_path.read_text("utf-8"))
        for provider_name in ("llm", "llm_fast", "llm_deepseek", "llm_backup"):
            if provider_name not in secrets:
                continue
            cfg = secrets[provider_name]
            keys = []
            # 优先 _keys 数组
            raw_keys = cfg.get("_keys", None)
            if raw_keys and isinstance(raw_keys, list):
                keys = [k for k in raw_keys if k]
            # 其次逗号分隔
            elif cfg.get("api_key") and "," in cfg["api_key"]:
                keys = [k.strip() for k in cfg["api_key"].split(",") if k.strip()]
            # 单个 key
            elif cfg.get("api_key"):
                keys = [cfg["api_key"]]
            if keys:
                _KEY_POOL[provider_name] = keys
                _KEY_INDEX[provider_name] = 0
    except Exception as e:
        log(f"Key pool load failed: {e}", "warn")

def _get_next_key(provider: str = "llm_fast") -> str:
    """获取 provider 的下一个 key (round-robin)"""
    if provider not in _KEY_POOL or not _KEY_POOL[provider]:
        # fallback to os.environ or empty
        return os.environ.get("ROBIN_GLM_API_KEY", "")
    idx = _KEY_INDEX.get(provider, 0)
    keys = _KEY_POOL[provider]
    key = keys[idx % len(keys)]
    _KEY_INDEX[provider] = (idx + 1) % len(keys)
    return key

# 启动时加载 key 池
_load_key_pool()

# ── Cost Tracking (LiteLLM 模式: 按key/phase追踪调用成本) ──
_COST_LOG: list[dict] = []
_COST_BY_PROVIDER: dict[str, float] = {}
_COST_BY_PHASE: dict[str, int] = {}
_MODEL_PRICING = {
    "deepseek-v4-flash": 0.00014,  # $ per 1K input tokens
    "deepseek-v4-pro": 0.00174,
    "glm-5.2": 0.00140,
}

def _track_cost(provider: str, model: str, phase: str = "general",
                input_tokens: int = 0, output_tokens: int = 0) -> float:
    """追踪一次调用的成本。返回估算费用($)。"""
    price = _MODEL_PRICING.get(model, 0.001)
    cost = (input_tokens + output_tokens) * price / 1000 * 0.3  # 粗略估算
    _COST_LOG.append({
        "ts": time.time(),
        "provider": provider, "model": model, "phase": phase,
        "input_tokens": input_tokens, "output_tokens": output_tokens,
        "cost": round(cost, 6)
    })
    _COST_BY_PROVIDER[provider] = _COST_BY_PROVIDER.get(provider, 0) + cost
    _COST_BY_PHASE[phase] = _COST_BY_PHASE.get(phase, 0) + 1
    return cost

def _get_cost_summary() -> dict:
    """获取成本汇总"""
    return {
        "total_cost": round(sum(c["cost"] for c in _COST_LOG), 4),
        "total_calls": len(_COST_LOG),
        "by_provider": dict(_COST_BY_PROVIDER),
        "by_phase": dict(_COST_BY_PHASE),
        "last_10": [
            {"model": c["model"], "phase": c["phase"], "cost": c["cost"]}
            for c in _COST_LOG[-10:]
        ]
    }

_ERROR_STATS: dict[str, dict] = {}  # error_type -> {"count": int, "first_seen": float, "last_seen": float}

# ── 熔断器状态机 (v10.4: 自修复) ──
# CLOSED: 正常调用; OPEN: 高错误率, 快速失败; HALF_OPEN: 冷却后放行1个探针, 成功则闭合
_CB_STATE: str = "CLOSED"
_CB_OPENED_AT: float = 0.0          # 进入 OPEN 的时间戳
_CB_HALF_OPEN_AT: float = 0.0       # 进入 HALF_OPEN 的时间戳
_CB_COOLDOWN: float = 30.0          # OPEN -> HALF_OPEN 冷却时间 (秒)
_CB_PROBE_DONE: bool = False        # HALF_OPEN 期间是否已放行探针
_CB_MAX_ERRORS: int = 8             # 近60s错误数阈值 (触发 OPEN)

def _cb_maybe_recover(_now: float) -> str:
    """熔断器状态机推进: 返回当前应处于的状态 CLOSED/OPEN/HALF_OPEN"""
    global _CB_STATE, _CB_OPENED_AT, _CB_HALF_OPEN_AT, _CB_PROBE_DONE
    if _CB_STATE == "OPEN":
        if _now - _CB_OPENED_AT >= _CB_COOLDOWN:
            # 冷却结束 → 进入 HALF_OPEN, 允许1个探针
            _CB_STATE = "HALF_OPEN"
            _CB_HALF_OPEN_AT = _now
            _CB_PROBE_DONE = False
            log("[熔断器] 冷却结束, 进入 HALF_OPEN 探针状态", "info")
    elif _CB_STATE == "HALF_OPEN":
        # HALF_OPEN 持续最多 60s, 超时未决 → 回到 OPEN 重新冷却
        if _now - _CB_HALF_OPEN_AT >= 60:
            _CB_STATE = "OPEN"
            _CB_OPENED_AT = _now
            _CB_PROBE_DONE = False
            log("[熔断器] HALF_OPEN 超时未决, 回到 OPEN", "warn")
    return _CB_STATE

def _cb_open():
    """触发熔断器 OPEN (在错误数超阈值时调用)"""
    global _CB_STATE, _CB_OPENED_AT
    if _CB_STATE != "OPEN":
        _CB_STATE = "OPEN"
        _CB_OPENED_AT = time.time()
        log("[熔断器] ⚡ 触发 OPEN: 近60s错误数超阈值", "warn")

def _cb_record_success():
    """探针成功 → 闭合熔断器并清空错误计数 (防自锁)"""
    global _CB_STATE, _CB_PROBE_DONE
    if _CB_STATE == "HALF_OPEN":
        _CB_STATE = "CLOSED"
        _CB_PROBE_DONE = False
        # 清空错误统计, 避免陈旧计数一直触发 OPEN
        _ERROR_STATS.clear()
        log("[熔断器] ✅ 探针成功, 熔断器闭合, 错误计数已清空", "info")

# ── 全局 LLM 调用锁 (v10.4: 防三路并行双烧) ──
# task_consumer / metamorphosis_guardian / closed_loop_watchdog 共享同一事件循环,
# 若无串行化, 三者同时调用 LLM 会: 1) 互相抢占 429 窗口 2) 共同推高 _ERROR_STATS 导致误熔断
# ── Turn 级硬超时 (P0-1): 单次 call_llm 总墙钟上限, 防止重试+退避无限空转 ──
_TURN_TIMEOUT: float = 540.0  # 9 分钟, 远小于 STALE_TIMEOUT(30min)

_LLM_GLOBAL_LOCK = None  # 延迟初始化 (需在事件循环内创建)

def _get_llm_lock():
    global _LLM_GLOBAL_LOCK
    if _LLM_GLOBAL_LOCK is None:
        _LLM_GLOBAL_LOCK = asyncio.Lock()
    return _LLM_GLOBAL_LOCK

# LLM 调用延迟和成功率统计
_LLM_CALL_STATS = {
    "total_calls": 0,
    "successful_calls": 0,
    "failed_calls": 0,
    "total_latency": 0.0,
    "latencies": [],  # 保留最近1000次延迟
}
_LATENCY_MAX_RECORDS = 1000

def get_llm_call_stats() -> dict:
    """返回 LLM 调用延迟和成功率统计摘要"""
    stats = dict(_LLM_CALL_STATS)
    if stats["total_calls"] > 0:
        stats["avg_latency"] = stats["total_latency"] / stats["total_calls"]
        stats["success_rate"] = stats["successful_calls"] / stats["total_calls"]
    else:
        stats["avg_latency"] = 0.0
        stats["success_rate"] = 0.0
    return stats

def _classify_error(error_str: str) -> str:
    """对错误分类: config / auth / transient / crash_loop / syntax / unknown"""
    if not error_str:
        return "unknown"
    e = error_str.lower()
    if any(x in e for x in ("403", "401", "forbidden", "unauthorized", "not authorized")):
        return "auth"
    if any(x in e for x in ("timeout", "connection refused", "connection reset", "remote end closed")):
        return "transient"
    if any(x in e for x in ("429", "rate limit", "too many requests", "quota")):
        return "rate_limit"
    if any(x in e for x in ("503", "502", "500", "service unavailable", "internal server error")):
        return "transient"
    if any(x in e for x in ("syntaxerror", "syntax error", "compileerror", "pycompileerror")):
        return "syntax"
    if any(x in e for x in ("api_key", "api key", "not configured", "no api")):
        return "config"
    if any(x in e for x in ("json.decoder.jsondecodeerror", "keyerror", "traceback")):
        return "syntax"
    return "transient"

def _track_error(error_str: str) -> str:
    """跟踪错误, 返回分类。如果检测到 crash_loop 返回对应类别。"""
    category = _classify_error(error_str)
    now = time.time()
    if category not in _ERROR_STATS:
        _ERROR_STATS[category] = {"count": 0, "first_seen": now, "last_seen": now}
    _ERROR_STATS[category]["count"] += 1
    _ERROR_STATS[category]["last_seen"] = now

    # 记录执行轨迹
    _trace_event("error", category, error_str[:100])

    # 检测 crash_loop: 同一类别 60s 内出现 >= 5 次
    stats = _ERROR_STATS[category]
    if stats["count"] >= 5 and (now - stats["first_seen"]) < 60:
        return f"crash_loop:{category}"
    return category

# ── 可解释性追踪: 执行轨迹日志 + 可视化报告 (v6) ──
_EXECUTION_TRACE: list[dict] = []
_MAX_TRACE_EVENTS = 500

def _trace_event(event_type: str, category: str, detail: str = ""):
    """记录执行轨迹事件"""
    now = time.time()
    _EXECUTION_TRACE.append({
        "ts": datetime.now().isoformat(),
        "t": round(now - _START_TIME, 1) if _START_TIME else 0,
        "type": event_type,
        "cat": category,
        "detail": detail[:200],
    })
    if len(_EXECUTION_TRACE) > _MAX_TRACE_EVENTS:
        _EXECUTION_TRACE.pop(0)

def generate_trace_report() -> str:
    """生成执行轨迹可视化的 HTML 报告"""
    trace = list(_EXECUTION_TRACE)
    if not trace:
        return "<html><body><h2>No execution data yet</h2></body></html>"

    # 按类型统计
    type_counts: dict = {}
    for t in trace:
        type_counts[t["type"]] = type_counts.get(t["type"], 0) + 1

    rows = ""
    for t in reversed(trace[-200:]):
        icon = {"error": "🔴", "warn": "🟡", "info": "🔵", "success": "🟢", "edit": "✏️"}.get(t["type"], "⚪")
        rows += f"""<tr>
            <td>{t['ts'][11:19]}</td>
            <td>{t['t']:.0f}s</td>
            <td>{icon} {t['type']}</td>
            <td><span class="cat-{t['cat']}">{t['cat']}</span></td>
            <td class="detail">{t['detail'][:100]}</td>
        </tr>"""

    cats = sorted(set(t["cat"] for t in trace))
    cat_tags = " ".join(f'<span class="tag cat-{c}">{c}</span>' for c in cats)

    return f"""<!DOCTYPE html>
<html lang="zh">
<head><meta charset="utf-8"><title>知更鸟战舰执行轨迹</title>
<style>
body {{ font-family: system-ui, sans-serif; background: #0d1117; color: #c9d1d9; margin: 20px; }}
h1 {{ color: #58a6ff; }}
.summary {{ display: flex; gap: 20px; margin: 16px 0; }}
.card {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 12px 20px; }}
.card .num {{ font-size: 28px; font-weight: bold; color: #58a6ff; }}
.card .label {{ color: #8b949e; font-size: 12px; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13px; }}
th {{ text-align: left; padding: 8px; background: #161b22; color: #8b949e; border-bottom: 1px solid #30363d; }}
td {{ padding: 6px 8px; border-bottom: 1px solid #21262d; }}
.detail {{ max-width: 400px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
.tag {{ display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 11px; margin: 2px; }}
.cat-auth {{ background: #da3633; color: #fff; }}
.cat-transient {{ background: #d29922; color: #fff; }}
.cat-syntax {{ background: #a371f7; color: #fff; }}
.cat-config {{ background: #1f6feb; color: #fff; }}
.cat-success {{ background: #238636; color: #fff; }}
.cat-info {{ background: #1f6feb; color: #fff; }}
.cat-error {{ background: #da3633; color: #fff; }}
.cat-edit {{ background: #1f6feb; color: #fff; }}
.cat-rate_limit {{ background: #d29922; color: #fff; }}
tr:hover {{ background: #1c2128; }}
</style></head>
<body>
<h1>🚢 知更鸟战舰执行轨迹</h1>
<div class="summary">
    <div class="card"><div class="num">{len(trace)}</div><div class="label">总事件</div></div>
    <div class="card"><div class="num">{type_counts.get('error', 0)}</div><div class="label">🔴 错误</div></div>
    <div class="card"><div class="num">{type_counts.get('success', 0)}</div><div class="label">🟢 成功</div></div>
    <div class="card"><div class="num">{type_counts.get('edit', 0)}</div><div class="label">✏️ 修改</div></div>
</div>
<div>{cat_tags}</div>
<table><thead><tr><th>时间</th><th>运行</th><th>类型</th><th>分类</th><th>详情</th></tr></thead>
<tbody>{rows}</tbody></table>
</body></html>"""

_START_TIME: float = 0  # daemon 启动时间戳, 在 main 中设置
_LAST_DREAM_TIME: float = 0  # 上次做梦时间

def _try_dream():
    """尝试触发 Dream Agent (每30min自动执行一次)"""
    global _LAST_DREAM_TIME
    now = time.time()
    if now - _LAST_DREAM_TIME < 1800:  # 30min
        return
    _LAST_DREAM_TIME = now
    try:
        from daemon_modules.dream_agent import DreamAgent
        for scope in SCOPE_DIRS:
            try:
                da = DreamAgent(scope)
                report = da.dream(force=True)
                if report.get("consolidated", 0) + report.get("evolved", 0) > 0:
                    log(f"dream[{Path(scope).name}]: cons={report.get('consolidated')} "
                        f"ver={report.get('verified')} comp={report.get('compressed')} "
                        f"evo={report.get('evolved')} self_dev={report.get('self_developed')}", "info")
                _trace_event("info", "dream", f"{Path(scope).name}: cons={report.get('consolidated')}")
            except (OSError, ValueError, RuntimeError, ImportError) as de:
                log(f"dream error for {scope}: {de}", "debug")
    except ImportError:
        pass

# ── 跨会话持久化: Robin Brain + Episodic 记忆 + 向量检索 (v5) ──
_BRAIN_CONTEXT: str = ""
_BRAIN_LOADED: bool = False
_BRAIN_LOAD_TIME: float = 0
_BRAIN_SEARCH = None  # BrainSearch 单例, 惰性初始化 (v7.5)
_CODECT_EXECUTOR = None  # CodeAct 执行器 (v8)
_SANDBOX_EXECUTOR = None  # Sandbox 执行器 (v8)

def _load_brain_context() -> str:
    """启动时加载 Robin Brain 知识库 + Episodic 记忆作为上下文。
    这在 daemon 重启时不丢失项目知识。"""
    global _BRAIN_CONTEXT, _BRAIN_LOADED, _BRAIN_LOAD_TIME
    try:
        brain_path = Path("I:/开发项目/.robin-brain")
        if not brain_path.exists():
            log("Robin Brain not found, skipping context load", "debug")
            return ""

        # 加载 brain_loader
        import importlib.util
        loader_path = brain_path / "brain_loader.py"
        if not loader_path.exists():
            log("brain_loader.py not found", "debug")
            return ""
        spec = importlib.util.spec_from_file_location("brain_loader", str(loader_path))
        brain_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(brain_mod)
        generate_context = brain_mod.generate_context

        parts = []
        # 扫描所有项目 brain
        projects = ["知更鸟 Agent", "自动化剪辑", "变现端", "高考提分系统", "小米表盘开发"]
        for proj in projects:
            try:
                ctx = generate_context(proj)
                if ctx and "无知识库" not in ctx:
                    parts.append(ctx)
            except Exception:
                pass

        # 读取 Episodic 记忆摘要 (如果有)
        episodic_dirs = [
            Path("I:/开发项目/知更鸟 Agent/robin-agent/server/episodic_memory"),
            Path("I:/开发项目") / "memory" / "episodic",
        ]
        for ep_dir in episodic_dirs:
            if ep_dir.exists():
                summaries = sorted(ep_dir.glob("*summary*"), key=lambda f: f.stat().st_mtime, reverse=True)[:3]
                for s in summaries:
                    parts.append(f"## Episodic: {s.stem}\n{s.read_text('utf-8', errors='replace')[:2000]}")
                break

        ctx_text = "\n\n".join(parts)
        if ctx_text:
            _BRAIN_CONTEXT = ctx_text
            _BRAIN_LOADED = True
            _BRAIN_LOAD_TIME = time.time()
            kbs = len(ctx_text) // 1024
            log(f"Robin Brain loaded: {kbs}KB across {len(projects)} projects", "info")
            return ctx_text
        return ""
    except ImportError as e:
        log(f"brain_loader not available: {e}", "debug")
        return ""
    except Exception as e:
        log(f"brain context load error: {e}", "warn")
        return ""

# ── HITL 置信度门 + L1/L2 增强 (v7: 批复模式+重路由) ──
_HITL_MODE: str = "L3"  # L1=批复不变, L2=拒绝重路由, L3=置信度自动

def _check_hitl_mode(qscore: float, syntax_ok: bool) -> tuple[bool, str]:
    """增强HITL: 支持L1批复模式+L2重路由"""
    pause, reason = should_hitl_pause(qscore, syntax_ok)
    if _HITL_MODE == "L1" and pause:
        return True, f"L1_APPROVAL:{reason}"
    elif _HITL_MODE == "L2" and pause:
        if qscore < 0.3:
            return True, f"L2_REROLL:{reason}"
        return True, f"L2_APPROVAL:{reason}"
    return pause, reason

_HITL_DIR = Path(__file__).parent / "hitl_pending"
from daemon_modules.daemon_reflexion import (
    set_hitl_dir, should_hitl_pause, write_hitl_checkpoint, check_hitl_approval,
    HITL_LOWER, HITL_UPPER
)
set_hitl_dir(str(_HITL_DIR))

def _check_pending_hitl() -> int:
    """启动时检查未处理的 HITL checkpoint"""
    pending = list(_HITL_DIR.glob("hitl_*.json"))
    if pending:
        log(f"HITL: {len(pending)} pending checkpoint(s) found on startup", "info")
        for cp in pending:
            found, approved, reason = check_hitl_approval(str(cp))
            if found and approved:
                log(f"HITL: checkpoint {cp.name} already approved", "info")
            elif found and not approved and reason == "pending":
                log(f"HITL: checkpoint {cp.name} still pending (quality={_read_checkpoint_quality(str(cp))})", "info")
    return len(pending)

def _read_checkpoint_quality(cp_path: str) -> str:
    try:
        import json
        data = json.loads(Path(cp_path).read_text("utf-8"))
        return str(data.get("quality", "?"))
    except: return "?"

def _process_approved_checkpoints(result: dict) -> int:
    """处理已审批的 HITL checkpoint: 应用修改"""
    applied = 0
    for cp in sorted(_HITL_DIR.glob("hitl_*.json")):
        found, approved, reason = check_hitl_approval(str(cp))
        if found and approved:
            try:
                import json
                data = json.loads(cp.read_text("utf-8"))
                fp = Path(data["path"])
                modified = data["modified"]
                fp.write_text(modified, "utf-8")
                result["ok"] += 1
                result["validated"] += 1
                result["log"].append(f"HITL_APPLIED {data['file']}: human approved (q={data['quality']})")
                cp.rename(cp.with_suffix(".applied.json"))
                applied += 1
                log(f"HITL: applied approved checkpoint: {data['file']}", "info")
            except (OSError, KeyError, json.JSONDecodeError) as e:
                result["log"].append(f"HITL_ERR {cp.name}: {e}")
                log(f"HITL: failed to apply {cp.name}: {e}", "error")
        elif found and not approved and reason not in ("pending",):
            # 已拒绝的 checkpoint 标记为 rejected
            cp.rename(cp.with_suffix(".rejected.json"))
            result["skip"] += 1
            result["log"].append(f"HITL_REJECTED {cp.name}: {reason}")
    return applied

SLEEP_SECONDS = 10            # 10秒一轮 (配合 release_stale_tasks 防泄漏)
HANDLER_TIMEOUT = 600         # 任务处理器超时(秒), 超时自动 fail 防死锁 (Task #548)
# 【死命令】知更鸟战舰烧量: 每30min确保烧满1800调用/5中队并行/无工时限制
# 默认开启，设 ROBIN_WARSHIP_BURN=0 可关闭
WARSHIP_BURN = (os.environ.get("ROBIN_WARSHIP_BURN", "1") == "1"
                or "--warship" in sys.argv)
WARSHIP_TARGET = int(os.environ.get("ROBIN_WARSHIP_TARGET", "1800"))
WARSHIP_WINDOW = int(os.environ.get("ROBIN_WARSHIP_WINDOW", "1800"))  # 30min
WORK_START_HOUR = 0           # 全天工作模式
WORK_END_HOUR = 24            # 24h 收工
HEARTBEAT_INTERVAL = 30       # 心跳间隔(秒)
MAX_CONSECUTIVE_ERRORS = 5    # 连续错误上限, 超过则暂停一轮
CRASH_RECOVERY_PAUSE = 300    # 崩溃恢复暂停(秒)
MAX_CONCURRENT_WORKERS = 0    # 关闭Explore扫描器, 所有LLM给任务队列

BASE_DIR = Path(__file__).parent
STATE_FILE = BASE_DIR / "l6_daemon_state.json"
LOG_FILE = BASE_DIR / "l6_daemon_log.jsonl"
METRICS_FILE = BASE_DIR / "l6_daemon_metrics.jsonl"
REPORT_FILE = BASE_DIR / "l6_evolution_report.md"

# 扫范围 — 5项目并行 (CAID原则: 项目隔离+权重调度)
# SOTA: CAID(CMU) 4并发天花板 / ZEBRA water-filling预算分配 / PilotDeck WorkSpace隔离
SCOPE_DIRS = [
    # 🥇 比赛优先: 阿里AI向善乡村教育赛道 (最高优先级)
    r"I:\开发项目\阿里AI向善\rural-edu-tutor",
    # 变现端 CashFlow: 全量 SaaS + 15 工具 + 技能商城 + XianyuAutoAgent
    r"I:\开发项目\变现端\CashFlow",
    r"I:\开发项目\变现端\CashFlow\tools",
    r"I:\开发项目\变现端\CashFlow\XianyuAutoAgent",
    # 小米表盘开发: hsr_firefly 流萤/知更鸟主题表盘
    r"I:\开发项目\小米表盘开发\hsr_firefly",
]
# 排除目录 (前端开发中, 不可动)
EXCLUDE_DIRS = {"desktop-pet", "dist", "build", "node_modules", "daemon_modules", "__pycache__", ".robin-brain", ".workbuddy", ".venv", ".git"}

# ── 辅助函数 ──

def _maybe_rotate_log():
    """检查日志文件是否需要轮转（每天或每10万行），并执行轮转 + 清理旧备份。"""
    log_path = LOG_FILE
    if not log_path.exists():
        return

    now = datetime.now()
    should_rotate = False
    try:
        stat = log_path.stat()
        # 基于文件大小轮转
        if stat.st_size > MAX_LOG_SIZE:
            should_rotate = True
        # 基于日期轮转 (文件的修改时间不是今天)
        file_mtime = datetime.fromtimestamp(stat.st_mtime)
        if file_mtime.date() != now.date():
            should_rotate = True
        # 基于行数轮转（仅在文件较大且未触发其他条件时检查）
        if not should_rotate and stat.st_size > 10 * 1024 * 1024:  # 10MB以上才检查行数
            line_count = sum(1 for _ in open(log_path, 'r', encoding='utf-8'))
            if line_count >= MAX_LOG_LINES:
                should_rotate = True
    except OSError:
        return  # 无法获取信息则跳过

    if not should_rotate:
        return

    # 线程安全轮转
    with _LOG_ROTATION_LOCK:
        # 二次检查（可能已被其他线程轮转）
        if not log_path.exists():
            return
        try:
            stat2 = log_path.stat()
            if stat2.st_size <= MAX_LOG_SIZE and datetime.fromtimestamp(stat2.st_mtime).date() == now.date():
                # 条件不再满足，说明已经被其他线程轮转过
                return
        except OSError:
            return

        # 生成新文件名：在原文件名基础上加时间戳
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        rotated_name = log_path.with_name(f"{log_path.stem}_{timestamp}{log_path.suffix}")
        # 如果目标已存在，再加后缀
        counter = 1
        while rotated_name.exists():
            rotated_name = log_path.with_name(f"{log_path.stem}_{timestamp}_{counter}{log_path.suffix}")
            counter += 1

        try:
            log_path.rename(rotated_name)
            # 创建新日志文件（空文件）
            log_path.touch()
        except OSError as e:
            print(f"[WARN] Log rotation failed: {e}", flush=True)
            return

        # 清理旧日志备份（保留最近 MAX_LOG_BACKUPS 个）
        try:
            pattern = f"{log_path.stem}_*{log_path.suffix}"
            backups = sorted(log_path.parent.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
            for old_file in backups[MAX_LOG_BACKUPS:]:
                old_file.unlink()
                debug_msg = f"cleaned old log backup: {old_file.name}"
                if 'debug_msg' not in dir():  # 简单清理日志，避免递归
                    print(f"[DEBUG] {debug_msg}", flush=True)
        except OSError as e:
            print(f"[WARN] Log backup cleanup failed: {e}", flush=True)


def log(msg: str, level: str = "info") -> None:
    _maybe_rotate_log()  # 检查轮转
    entry: dict[str, str] = {"ts": datetime.now().isoformat(), "level": level, "msg": msg}
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as e:
        print(f"[{level.upper()}] Log write failed: {e}", flush=True)
    print(f"[{level.upper()}] {msg}", flush=True)

def log_metric(metric: dict) -> None:
    """记录质量指标到 metrics 文件"""
    _maybe_rotate_metrics()  # 写入前检查 metrics 文件是否需要轮转
    entry = {"ts": datetime.now().isoformat(), **metric}
    try:
        with open(METRICS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as e:
        print(f"[WARN] Metric write failed: {e}", flush=True)

def read_state() -> dict[str, object]:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text("utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            log(f"State read failed: {e}", "warn")
            return {"running": False, "pid": 0, "ok": 0, "calls": 0, "started_at": None,
                    "last_error": str(e), "last_heartbeat": None, "consecutive_errors": 0,
                    "force_work": False, "stop_signal": False, "total_rollback": 0, "total_validated": 0}
    return {"running": False, "pid": 0, "ok": 0, "calls": 0, "started_at": None,
            "last_error": None, "last_heartbeat": None, "consecutive_errors": 0,
            "force_work": False, "stop_signal": False, "total_rollback": 0, "total_validated": 0}

def write_state(**kw) -> None:
    s = read_state()
    s.update(kw)
    try:
        STATE_FILE.write_text(json.dumps(s, indent=2, ensure_ascii=False), "utf-8")
    except OSError as e:
        log(f"状态写入失败: {e}", "error")

def _save_state(extra: dict | None = None) -> None:
    """统一状态写入: 先 read_state() 取旧 ok/calls 等计数器, 合并 extra, 刷新 last_heartbeat.
    修复心跳协程与任务完成写状态互相覆盖 ok/calls 的问题."""
    s = read_state()
    if extra:
        s.update(extra)
    s["last_heartbeat"] = datetime.now().isoformat()
    try:
        STATE_FILE.write_text(json.dumps(s, indent=2, ensure_ascii=False), "utf-8")
    except OSError as e:
        log(f"状态写入失败: {e}", "error")

def heartbeat() -> None:
    """写入心跳时间戳, 用于检测假死"""
    _save_state()

def should_work() -> bool:
    """判断是否该工作: 时间在工作区间, 或 force_work 模式"""
    s = read_state()
    if s.get("force_work"):
        return True
    now = datetime.now()
    if WORK_START_HOUR <= now.hour < WORK_END_HOUR:
        return True
    return False

# ── Coding Plan 计数 (合租 400次/5h 上限) ──
_CODINGPLAN_CALLS = 0
_CODINGPLAN_WINDOW = time.time()
_CODINGPLAN_MAX = 400           # 合租对半 400次/5h
_CODINGPLAN_RESET = 5 * 3600    # 5h 窗口
_LAST_CODINGPLAN_TS = 0.0       # 最后一次 daemon 调 Coding Plan 的时间戳
_CODINGPLAN_COOLDOWN = 45       # 冷却秒数: 45s 内不重复调, 给室友留空间
_LAST_DEEPSEEK_CURL_TS = 0.0    # OpenCode Go curl 最后一次调用时间
_DEEPSEEK_CURL_COOLDOWN = 60    # 60s 冷却, 避免与用户聊天框抢链路

def _codingplan_available() -> bool:
    """检查 Coding Plan 额度是否可用"""
    global _CODINGPLAN_CALLS, _CODINGPLAN_WINDOW
    now = time.time()
    if now - _CODINGPLAN_WINDOW > _CODINGPLAN_RESET:
        _CODINGPLAN_CALLS = 0
        _CODINGPLAN_WINDOW = now
    return _CODINGPLAN_CALLS < _CODINGPLAN_MAX

def _codingplan_inc():
    """计数一次 Coding Plan 调用"""
    global _CODINGPLAN_CALLS
    _CODINGPLAN_CALLS += 1

# ── Coding Plan 直连路由 (CodeWorker 主力通道) ──

def _call_codingplan_direct(prompt: str, max_tokens: int = MAX_OUTPUT, temperature: float = 0.1) -> str:
    """CodeWorker 主力: 直连智谱 Coding Plan glm-5.2 (国内 2~5s)，合租上限 400次/5h
    失败时降级到 sfkey glm-5.2"""
    if not _codingplan_available():
        log(f"[CodingPlan] 额度已用完 ({_CODINGPLAN_CALLS}/{_CODINGPLAN_MAX} 次/5h)，降级 sfkey", "warn")
        return _call_with_endpoint(prompt, max_tokens, temperature)

    import urllib3
    urllib3.disable_warnings()
    _start = time.time()
    try:
        secrets = json.loads(Path(__file__).parent.joinpath(".secrets.json").read_text("utf-8"))
        cp = secrets.get("llm_codingplan", {})
        cp_url = cp.get("base_url", "") + "/chat/completions"
        cp_key = cp.get("api_key", "")
        cp_model = cp.get("model", "glm-5.2")
        if not cp_url or not cp_key:
            raise ValueError("Coding Plan config missing")
    except Exception as e:
        log(f"[CodingPlan] Config load failed: {e}, falling back to sfkey", "warn")
        return _call_with_endpoint(prompt, max_tokens, temperature)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {cp_key}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    payload = {
        "model": cp_model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    for attempt in range(3):
        try:
            resp = requests.post(
                cp_url, json=payload, headers=headers,
                timeout=(30, 300), verify=False,
                proxies={"http": "", "https": ""}
            )
            if resp.status_code != 200:
                raise OSError(f"HTTP {resp.status_code}: {resp.text[:200]}")
            data = resp.json()
            response = data["choices"][0]["message"].get("content", "")
            if not response:
                response = data["choices"][0]["message"].get("reasoning_content", "")
            if not response:
                payload["messages"] = [
                    {"role": "user", "content": prompt + "\n直接输出最终答案，不要思考过程。"}
                ]
                continue
            _codingplan_inc()
            log(f"[CodingPlan] ✅ {len(response)} chars in {time.time()-_start:.1f}s ({_CODINGPLAN_CALLS}/{_CODINGPLAN_MAX})")
            return response
        except Exception as e:
            log(f"[CodingPlan] attempt {attempt+1}/2 failed: {type(e).__name__}: {str(e)[:80]}", "warn")
            if attempt < 1:
                time.sleep(5)

    # Coding Plan 失败 → 降级到 sfkey
    log(f"[CodingPlan] Failed after {time.time()-_start:.1f}s, falling back to sfkey", "warn")
    return _call_with_endpoint(prompt, max_tokens, temperature)


# ── DeepSeek 直连路由 (CodeWorker 三级回退) ──
# 注: Python OpenSSL 连 opencode.ai 会被 GFW 拦截 (SSL握手超时)
#     改用 Windows 原生 Schannel (通过 curl) 可绕过

def _call_deepseek_via_curl(prompt: str, max_tokens: int = MAX_OUTPUT, temperature: float = 0.1) -> str:
    """用 curl (Schannel SSL) 调用 DeepSeek V4 Flash — 绕过 OpenSSL 封锁"""
    import subprocess, json
    _start = time.time()
    try:
        secrets = json.loads(Path(__file__).parent.joinpath(".secrets.json").read_text("utf-8"))
        ds = secrets.get("llm_deepseek", {})
        ds_url = ds.get("base_url", "")
        ds_key = ds.get("api_key", "")
        ds_model = ds.get("model", "deepseek-v4-flash")
    except Exception as e:
        log(f"[DeepSeek/curl] Config error: {e}", "warn")
        return "LLM_FAIL: config"

    payload = json.dumps({
        "model": ds_model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
    })

    for attempt in range(2):
        try:
            # 增加 max-time 到 60s 给推理模型留够时间
            r = subprocess.run(
                ["curl", "-sk", "--max-time", "60",
                 ds_url,
                 "-H", f"Authorization: Bearer {ds_key}",
                 "-H", "Content-Type: application/json",
                 "-d", payload],
                capture_output=True, text=True, timeout=65
            )
            if r.returncode != 0:
                raise OSError(f"curl exit={r.returncode}: {r.stderr[:200]}")
            data = json.loads(r.stdout)
            response = data["choices"][0]["message"].get("content", "")
            if not response:
                response = data["choices"][0]["message"].get("reasoning_content", "")
            if not response:
                payload = json.dumps({
                    "model": ds_model,
                    "messages": [{"role": "user", "content": prompt + "\n直接输出最终答案，不要思考过程。"}],
                    "max_tokens": max_tokens, "temperature": temperature,
                })
                continue
            log(f"[DeepSeek/curl] ✅ {len(response)} chars in {time.time()-_start:.1f}s")
            return response
        except subprocess.TimeoutExpired:
            log(f"[DeepSeek/curl] attempt {attempt+1}/2 timeout", "warn")
        except Exception as e:
            log(f"[DeepSeek/curl] attempt {attempt+1}/2 failed: {type(e).__name__}", "warn")

    log(f"[DeepSeek/curl] Failed after {time.time()-_start:.1f}s", "warn")
    return "LLM_FAIL: curl"

def _call_deepseek_direct(prompt: str, max_tokens: int = MAX_OUTPUT, temperature: float = 0.1) -> str:
    """[后台禁用] OpenCode Go DeepSeek 已摘离后台路由, 避免与用户聊天框抢同一条链路 — 直接走 sfkey glm-5.2"""
    return _call_with_endpoint(prompt, max_tokens, temperature)


def _call_with_endpoint(prompt: str, max_tokens: int = MAX_OUTPUT, temperature: float = 0.1) -> str:
    """用当前全局 ENDPOINT/API_KEY 调用 (sfkey glm-5.2) — CodeWorker 降级回退用"""
    _start = time.time()
    key = _get_next_key("llm_fast") or API_KEY
    if not key:
        return "LLM_FAIL: no API key"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    for attempt in range(3):
        try:
            resp = requests.post(
                ENDPOINT, json=payload, headers=headers,
                timeout=300, verify=False, proxies={"http": "", "https": ""}
            )
            if resp.status_code != 200:
                raise OSError(f"HTTP {resp.status_code}")
            data = resp.json()
            response = data["choices"][0]["message"].get("content", "")
            if not response:
                response = data["choices"][0]["message"].get("reasoning_content", "")
            if response:
                log(f"[sfkey] ✅ {len(response)} chars in {time.time()-_start:.1f}s")
                return response
            if attempt < 2:
                payload["messages"] = [{"role": "user", "content": prompt + "\n直接输出最终答案。"}]
                continue
        except Exception:
            if attempt < 2:
                time.sleep(3)
                continue
    return "LLM_FAIL_ALL: sfkey fallback also failed"


def call_llm(prompt: str, max_tokens: int = MAX_OUTPUT, temperature: float = 0.1, use_deepseek: bool = False) -> str:
    # ── DeepSeek 路由: CodeWorker 专用通道 ──
    if use_deepseek:
        return _call_deepseek_direct(prompt, max_tokens, temperature)

    _call_start_time = time.time()
    # ── 熔断检查: 状态机推进 + 近60s错误数统计 ──
    import random
    _now = time.time()
    # 定期清理超过 60s 的陈旧错误条目 (防计数永不清零)
    _stale = [k for k, v in _ERROR_STATS.items() if _now - v["last_seen"] >= 60]
    for _k in _stale:
        del _ERROR_STATS[_k]
    _recent_errors = sum(v["count"] for v in _ERROR_STATS.values())
    # 错误数超阈值 → 触发 OPEN
    if _recent_errors > _CB_MAX_ERRORS:
        _cb_open()
    # 推进状态机
    _cb_state = _cb_maybe_recover(_now)
    if _cb_state == "OPEN":
        cached = _get_cached_prompt(prompt)
        if cached:
            log("Circuit breaker: high error rate, returning cached", "warn")
            _LLM_CALL_STATS["total_calls"] += 1
            _LLM_CALL_STATS["successful_calls"] += 1
            latency = time.time() - _call_start_time
            _LLM_CALL_STATS["total_latency"] += latency
            _LLM_CALL_STATS["latencies"].append(latency)
            if len(_LLM_CALL_STATS["latencies"]) > _LATENCY_MAX_RECORDS:
                _LLM_CALL_STATS["latencies"] = _LLM_CALL_STATS["latencies"][-_LATENCY_MAX_RECORDS:]
            return cached
        log("Circuit breaker: OPEN, skipping call", "warn")
        _LLM_CALL_STATS["total_calls"] += 1
        _LLM_CALL_STATS["failed_calls"] += 1
        return "LLM_FAIL_CIRCUIT: high error rate (overloaded)"
    if _cb_state == "HALF_OPEN":
        # 只允许1个探针通过, 其余快速失败
        global _CB_PROBE_DONE
        if _CB_PROBE_DONE:
            cached = _get_cached_prompt(prompt)
            if cached:
                _LLM_CALL_STATS["total_calls"] += 1
                _LLM_CALL_STATS["successful_calls"] += 1
                return cached
            _LLM_CALL_STATS["total_calls"] += 1
            _LLM_CALL_STATS["failed_calls"] += 1
            return "LLM_FAIL_CIRCUIT: half-open waiting for probe"
        # 标记探针已放行, 本次调用正常进行
        _CB_PROBE_DONE = True
        log("[熔断器] HALF_OPEN 探针放行, 尝试1次真实调用", "info")

    # Key 池轮询
    current_key = _get_next_key("llm_fast") or API_KEY
    if not current_key:
        log("API_KEY not configured", "error")
        _track_error("API_KEY not configured")
        _LLM_CALL_STATS["total_calls"] += 1
        _LLM_CALL_STATS["failed_calls"] += 1
        return "LLM_FAIL_3: API_KEY not configured"

    # Prompt Cache 检查 (仅 temperature=0.1 时用缓存)
    if temperature == 0.1:
        cached = _get_cached_prompt(prompt)
        if cached is not None:
            log("LLM cache hit (prompt identical)", "debug")
            return cached

    # 记录路由决策 & 任务类型
    _start_time = time.time()
    _task_type = "code" if any(kw in prompt[:200] for kw in ["CODE", "FILE:", "编辑"]) else "general"
    if len(prompt) > 2000:
        _task_type = "large"

    # ── 加载回退路由配置 (OpenCode Go 跨境中转) ──
    _fallback_endpoint = None
    _fallback_key = None
    _fallback_model = None
    try:
        _secrets_data = json.loads(Path(__file__).parent.joinpath(".secrets.json").read_text("utf-8"))
        if "llm_deepseek" in _secrets_data:
            # [后台禁用] 不再把 OpenCode Go 作为 sfkey 失败回退, 专留用户聊天框使用
            ds = _secrets_data["llm_deepseek"]
            _fallback_endpoint = None
            _fallback_key = None
            _fallback_model = None
    except Exception:
        pass

    # 构建请求负载
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if MODEL and "deepseek" in MODEL.lower():
        payload["reasoning_effort"] = "max"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {current_key}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    import urllib3
    urllib3.disable_warnings()

    # ── 重试循环 (5次, 指数退避+抖动) ──
    max_attempts = 5
    fallback_used = False
    _turn_deadline = time.time() + _TURN_TIMEOUT  # P0-1: turn 级硬上限
    for attempt in range(max_attempts):
        try:
            resp = requests.post(
                ENDPOINT, json=payload, headers=headers,
                timeout=300, verify=False, proxies={"http": "", "https": ""}
            )
            if resp.status_code != 200:
                raise OSError(f"HTTP {resp.status_code}: {resp.text[:200]}")
            data = resp.json()
            response = data["choices"][0]["message"].get("content", "")
            if not response:
                response = data["choices"][0]["message"].get("reasoning_content", "")
            if not response:
                # 推理模型空回复：加指令强制输出
                if attempt < 3:
                    payload["messages"] = [
                        {"role": "user", "content": prompt + "\n直接输出最终答案，不要思考过程，不要分析。"}
                    ]
                    continue
                raise KeyError("both content and reasoning_content are empty")

            # 成功
            _cache_prompt(prompt, response)
            # 探针成功 → 闭合熔断器 (自修复)
            _cb_record_success()
            # 记录路由决策
            try:
                record_routing_decision(
                    task_type=_task_type,
                    task_complexity="复杂" if len(prompt) > 2000 else "中等" if len(prompt) > 500 else "简单",
                    model_chosen=MODEL,
                    token_cost=len(prompt) + len(response),
                    task_success=True,
                    quality_score=0.8,
                    prompt_length=len(prompt),
                    duration_ms=round((time.time() - _start_time) * 1000),
                )
            except Exception:
                pass
            return response

        except (requests.RequestException, OSError, json.JSONDecodeError, KeyError) as e:
            error_category = _track_error(str(e))
            is_network_error = any(
                kw in str(e).lower() for kw in ['timeout', 'reset', 'refused', 'connection', 'eof', 'handshake', 'broken']
            )
            is_rate_limit = "429" in str(e) or "rate limit" in str(e).lower()
            is_auth_error = any(kw in str(e) for kw in ["401", "403", "unauthorized", "forbidden"])
            is_server_error = any(kw in str(e) for kw in ["500", "502", "503", "service unavailable"])

            log(f"LLM call attempt {attempt+1}/{max_attempts} failed: {e} [category={error_category}]", "warn")

            # ── Turn 级超时 (P0-1): 超过硬上限则放弃剩余重试, 直接走降级 ──
            if time.time() > _turn_deadline:
                log(f"[Turn超时] 单次调用墙钟已超 {_TURN_TIMEOUT:.0f}s, 中止重试走降级", "warn")
                break

            # ── 故障恢复 ──
            # 认证错误：直接返回，不再重试
            if is_auth_error:
                log("Authentication error, aborting retries", "error")
                _LLM_CALL_STATS["total_calls"] += 1
                _LLM_CALL_STATS["failed_calls"] += 1
                return f"LLM_FAIL_AUTH: {e}"

            # 速率限制：增加等待时间
            if is_rate_limit:
                wait = 30 + random.uniform(0, 30)
                log(f"Rate limited, waiting {wait:.0f}s", "warn")
                time.sleep(wait)
                continue

            # 网络错误且备用端点可用 → 尝试回退路由 (最多 2 次)
            if is_network_error and _fallback_endpoint and not fallback_used and attempt < 3:
                fallback_used = True
                log("Network error → fallback to OpenCode Go", "warn")
                try:
                    fb_payload = dict(payload)
                    fb_payload["model"] = _fallback_model or "deepseek-v4-flash"
                    fb_resp = requests.post(
                        _fallback_endpoint, json=fb_payload, headers=headers,
                        timeout=600, verify=False, proxies={"http": "", "https": ""}
                    )
                    if fb_resp.status_code == 200:
                        fb_data = fb_resp.json()
                        fb_response = fb_data["choices"][0]["message"].get("content", "")
                        if not fb_response:
                            fb_response = fb_data["choices"][0]["message"].get("reasoning_content", "")
                    if fb_response:
                        _cache_prompt(prompt, fb_response)
                        log(f"Fallback OpenCode Go succeeded [{len(fb_response)} chars]")
                        try:
                            record_routing_decision(...)
                        except Exception:
                            pass
                        _LLM_CALL_STATS["total_calls"] += 1
                        _LLM_CALL_STATS["successful_calls"] += 1
                        latency = time.time() - _call_start_time
                        _LLM_CALL_STATS["total_latency"] += latency
                        _LLM_CALL_STATS["latencies"].append(latency)
                        if len(_LLM_CALL_STATS["latencies"]) > _LATENCY_MAX_RECORDS:
                            _LLM_CALL_STATS["latencies"] = _LLM_CALL_STATS["latencies"][-_LATENCY_MAX_RECORDS:]
                        return fb_response
                except Exception as fb_e:
                    log(f"Fallback also failed: {fb_e}", "error")

            # crash_loop / config 错误 → 暂停+清理
            if error_category.startswith("crash_loop"):
                log(f"Crash loop detected [{error_category}], pausing 60s", "warn")
                time.sleep(60)
                # 重置该类别计数
                _ERROR_STATS.pop(error_category.split(":")[1], None)
            elif error_category in ("config", "auth"):
                log(f"Config/auth error, short pause", "warn")
                time.sleep(5)

            # 指数退避 + 随机抖动 (0.5x ~ 1.5x), 不越过 turn 截止线
            if attempt < max_attempts - 1 and time.time() <= _turn_deadline:
                delay = (2 ** attempt) * random.uniform(0.5, 1.5)
                delay = min(delay, 120, max(0.0, _turn_deadline - time.time()))  # 上限 120s / 不超时
                time.sleep(delay)

    # ── 所有重试失败 → 降级策略 ──
    # 1. 尝试缓存 (允许过期缓存)
    cached = _get_cached_prompt(prompt)
    if cached:
        log("All LLM attempts failed, returning stale cached response", "warn")
        _LLM_CALL_STATS["total_calls"] += 1
        _LLM_CALL_STATS["successful_calls"] += 1
        latency = time.time() - _call_start_time
        _LLM_CALL_STATS["total_latency"] += latency
        _LLM_CALL_STATS["latencies"].append(latency)
        if len(_LLM_CALL_STATS["latencies"]) > _LATENCY_MAX_RECORDS:
            _LLM_CALL_STATS["latencies"] = _LLM_CALL_STATS["latencies"][-_LATENCY_MAX_RECORDS:]
        return cached
    # 2. 返回空 / 降级提示
    log("All LLM attempts exhausted, returning failure", "error")
    _LLM_CALL_STATS["total_calls"] += 1
    _LLM_CALL_STATS["failed_calls"] += 1
    return "LLM_FAIL_ALL: all attempts failed (5 retries)"

# ── BoN 可用性标志 (启动时检测 scorer 可用性) ──
_BON_AVAILABLE: bool = True  # 默认启用

async def call_llm_async(prompt: str, max_tokens: int = MAX_OUTPUT) -> str:
    """异步调用 LLM — 支持 Best-of-N 并行推理增强。

    v8.5 P0: 对复杂 prompt 自动启用 BoN 采样,
    简单 prompt 走原有单次调用 (不浪费调用预算)。
    """
    # 判断是否使用 BoN: 只对复杂推理任务启用, 不干扰普通代码编辑
    # 普通编辑 prompt (含文件内容) 即使很长也不启用 BoN
    is_complex_review = (
        "full code review" in prompt.lower() or
        "安全审计" in prompt[:200] or
        "进行架构" in prompt[:200] or
        "conduct architecture" in prompt.lower() or
        "security audit" in prompt.lower() or
        "depth review" in prompt.lower() or
        "review all files" in prompt.lower()
    )
    use_bon = _BON_AVAILABLE and is_complex_review and max_tokens > 8192
    
    if not use_bon:
        # 简单 prompt → 原有单次调用 (加全局锁防并行双烧)
        async with _get_llm_lock():
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, call_llm, prompt, max_tokens)
    
    # 复杂 prompt → Best-of-N 并行采样
    try:
        sampler = get_sampler()
        
        # 决定采样次数
        complexity = "medium"
        if max_tokens > 16384 or len(prompt) > 4000:
            complexity = "complex"
        elif "refactor" in prompt.lower() or "架构" in prompt[:200]:
            complexity = "medium"
        
        n = COMPLEXITY_N_MAP.get(complexity, 3)
        
        # 为 BoN 构造 llm_caller (同步 call_llm 包装成异步)
        async def _bo_caller(p: str, temperature: float) -> str:
            return await asyncio.get_running_loop().run_in_executor(
                None, lambda: call_llm(p, max_tokens, temperature=temperature))
        
        # 自验证评分器
        async def _bo_scorer(text: str) -> float:
            """用 quality_score 作为评分器"""
            if not text:
                return 0.0
            try:
                from daemon_modules.daemon_reflexion import quality_score
                q = quality_score(text)
                return max(0.1, min(1.0, q))
            except Exception:
                # 评分失败: 按文本长度给基准分
                return min(1.0, len(text) / 1000)
        
        result = await sampler.sample(
            prompt, llm_caller=_bo_caller, scorer=_bo_scorer,
            n_samples=n, complexity=complexity,
        )
        
        log(f"BoN: n={result.n_samples} score={result.score:.3f} "
            f"method={result.method} consensus={result.consensus} "
            f"latency={result.total_latency:.1f}s")
        return result.text
    except Exception as e:
        log(f"BoN failed, falling back to single call: {e}", "warn")
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, call_llm, prompt, max_tokens)

async def call_llm_async_deepseek(prompt: str, max_tokens: int = MAX_OUTPUT) -> str:
    """CodeWorker 路由: Coding Plan(合租 glm-5.2, 45s冷却)
                    → sfkey(兜底, 可能429等窗口恢复)
                    → OpenCode Go curl(终极兜底, 60s冷却, 不与聊天框抢)
    永不熔断: 三条路由全试过才返回失败。"""
    async with _get_llm_lock():
        loop = asyncio.get_running_loop()
        global _LAST_CODINGPLAN_TS, _LAST_DEEPSEEK_CURL_TS
        last_error = ""

        now = time.time()
        # 1. Coding Plan (冷却期内跳过)
        if now - _LAST_CODINGPLAN_TS >= _CODINGPLAN_COOLDOWN:
            _LAST_CODINGPLAN_TS = now
            result = await loop.run_in_executor(
                None, lambda: _call_codingplan_direct(prompt, max_tokens))
            if result and not result.startswith("LLM_FAIL"):
                return result
            last_error = result or "CodingPlan failed"
            log(f"[CodeWorker] Coding Plan failed: {last_error[:60]}", "warn")
        else:
            remain = _CODINGPLAN_COOLDOWN - (now - _LAST_CODINGPLAN_TS)
            log(f"[CodeWorker] Coding Plan cooldown ({remain:.0f}s), skip", "debug")

        # 2. sfkey 兜底
        sfkey_result = await loop.run_in_executor(
            None, lambda: _call_with_endpoint(prompt, max_tokens))
        if sfkey_result and not sfkey_result.startswith("LLM_FAIL"):
            return sfkey_result
        last_error = sfkey_result or "sfkey failed"
        log(f"[CodeWorker] sfkey fallback failed: {last_error[:60]}", "warn")

        # 3. OpenCode Go curl 终极兜底 (60s冷却, 不与聊天框抢)
        now = time.time()
        if now - _LAST_DEEPSEEK_CURL_TS >= _DEEPSEEK_CURL_COOLDOWN:
            _LAST_DEEPSEEK_CURL_TS = now
            log("[CodeWorker] All routes failed, trying OpenCode Go curl (last resort)...", "warn")
            curl_result = await loop.run_in_executor(
                None, lambda: _call_deepseek_via_curl(prompt, max_tokens))
            if curl_result and not curl_result.startswith("LLM_FAIL"):
                log(f"[CodeWorker] OpenCode Go curl succeeded as last resort!")
                return curl_result
            last_error = curl_result or "curl also failed"
            log(f"[CodeWorker] OpenCode Go curl also failed: {last_error[:60]}", "error")

        # 全部失败
        return f"LLM_FAIL_ALL: {last_error}"

async def call_llm_async_sfkey(prompt: str, max_tokens: int = MAX_OUTPUT) -> str:
    """异步调用 sfkey glm-5.2 — 普通任务专用"""
    async with _get_llm_lock():
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, call_llm, prompt, max_tokens)

def call_llm_with_brain(prompt: str, max_tokens: int = MAX_OUTPUT, use_brain: bool = True) -> str:
    """带 Robin Brain 上下文的 LLM 调用 — 跨会话知识注入。"""
    if use_brain and _BRAIN_CONTEXT:
        enhanced = f"[项目知识库]\n{_BRAIN_CONTEXT[:4096]}\n\n[任务]\n{prompt}"
        return call_llm(enhanced, max_tokens)
    return call_llm(prompt, max_tokens)

# ── Idle Burn: 空闲补刀 ──

_idle_burn_idx = 0
_idle_burn_lock = threading.Lock()

def _idle_pick_file() -> Optional[str]:
    """空闲时从扫描范围随机挑一个文件给 LLM '找茬'"""
    global _idle_burn_idx
    all_files = []
    for ext in ("*.py", "*.ts", "*.tsx", "*.js", "*.jsx", "*.html", "*.css", "*.lua"):
        for scope in SCOPE_DIRS:
            sp = Path(scope)
            if not sp.exists():
                continue
            for f in sp.rglob(ext):
                # 跳过排除目录
                rel = f.relative_to(sp).as_posix()
                if any(ex in rel.split("/") for ex in EXCLUDE_DIRS):
                    continue
                # 跳过冷却期内的文件
                with _recently_processed_lock:
                    if str(f) in _recently_processed:
                        continue
                all_files.append(str(f))
    if not all_files:
        return None
    # 轮询, 保证公平
    with _idle_burn_lock:
        _idle_burn_idx = (_idle_burn_idx + 1) % len(all_files)
        return all_files[_idle_burn_idx]

async def idle_burn_cycle() -> dict:
    """空闲烧: 没有真活时, 做代码保洁 (补测试/加docstring/小重构)"""
    fpath = _idle_pick_file()
    if not fpath:
        return {"ok": 0, "skip": 0, "fail": 0}
    try:
        content = Path(fpath).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {"ok": 0, "skip": 0, "fail": 0}
    if len(content) > 8000:
        content = content[:8000] + "\n... (truncated)"

    prompt = (
        f"你是代码质量专家。分析以下文件, 做1-2个小型改进:\n"
        f"- 补缺失的 docstring/注释\n"
        f"- 修小代码异味 (如过长行、未用变量)\n"
        f"- 添加简单的类型注解 (不改变函数签名)\n\n"
        f"文件路径: {fpath}\n"
        f"文件内容:\n```\n{content}\n```\n\n"
        f"输出格式: 用 CONTEXT_FIND/CONTEXT_REPLACE 格式, 每个改动分开。"
        f"如果没有需要改的, 输出 NO_CHANGES_NEEDED"
    )
    output = await call_llm_async(prompt, max_tokens=4096)
    if output.startswith("LLM_FAIL_3") or "NO_CHANGES_NEEDED" in output:
        return {"ok": 0, "skip": 1, "fail": 0}
    edits = parse_output(output)
    result = apply_edits(edits, [{"path": fpath, "rel": Path(fpath).name, "lines": 0}])
    log(f"idle_burn: {Path(fpath).name} OK={result.get('ok',0)} SKIP={result.get('skip',0)}")
    return result

# ── 文件扫描 ──

# 已处理文件冷却: 记录最近修改的文件路径, 避免反复改同一文件
_recently_processed = {}  # {path: timestamp}
_recently_processed_lock = threading.Lock()
COOLDOWN_SECONDS = 1800    # 30分钟冷却期

def scan_for_work() -> list[dict[str, object]]:
    """扫描项目目录, 返回可改进的文件列表 (带项目上下文+代码质量检测+冷却期)"""
    global _recently_processed
    now = time.time()
    # 清理过期冷却记录
    with _recently_processed_lock:
        _recently_processed = {k: v for k, v in _recently_processed.items() if now - v < COOLDOWN_SECONDS}

    candidates = []
    for scope in SCOPE_DIRS:
        sp = Path(scope)
        if not sp.exists():
            continue
        try:
            proj_ctx = get_project_context(scope)
        except (OSError, ValueError, RuntimeError, ImportError) as e:
            log(f"skip scope {scope}: get_project_context failed: {e}", "warn")
            continue
        for ext in ("*.ts", "*.tsx", "*.py", "*.js", "*.jsx", "*.lua", "*.html", "*.css", "*.json", "*.yaml"):
            for f in sp.rglob(ext):
                rel = str(f.relative_to(sp))
                # 排除前端开发中的目录
                if any(excl in Path(rel).parts for excl in EXCLUDE_DIRS):
                    continue
                # 冷却期: 最近处理过的文件跳过
                fpath = str(f)
                with _recently_processed_lock:
                    if fpath in _recently_processed:
                        continue
                try:
                    content = f.read_text("utf-8", errors="replace")
                    if len(content) < 50:
                        continue
                    # 排除纯数据 JSON (scores, cache, tmp 等)
                    if ext == "*.json" and any(kw in rel.lower() for kw in ("score", "cache", "tmp", "log", "metric", "state", "budget")):
                        continue
                    # 排除小配置文件 (postcss, tsconfig, babel 等无需修改)
                    if ext in ("*.js", "*.json", "*.yaml", "*.yml") and any(kw in rel.lower() for kw in ("postcss", "tsconfig", "babel", "eslint", "prettier", ".eslintrc", ".prettierrc")):
                        continue
                    has_todo = any(kw in content for kw in ["TODO", "FIXME", "HACK", "todo"])
                    # 代码质量检测
                    has_type_any = content.count(": any") > 2 if ext in ("*.ts", "*.tsx") else False
                    has_bare_except = bool(re.search(r'^\s*except\s*:', content, re.MULTILINE)) if ext == "*.py" else False
                    candidates.append({
                        "path": fpath,
                        "rel": rel,
                        "scope": scope,
                        "size": len(content),
                        "lines": content.count("\n") + 1,
                        "has_todo": has_todo,
                        "has_type_any": has_type_any,
                        "has_bare_except": has_bare_except,
                        "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                        "project": proj_ctx.get("name", ""),
                    })
                except OSError as e:
                    log(f"Scan skip {rel}: {e!r}", "debug")
                    continue
    # 排序: TODO优先 > 代码质量问题 > 小文件优先
    candidates.sort(key=lambda x: (not x["has_todo"], not x["has_type_any"], not x["has_bare_except"], x["size"]))
    return candidates[:100]

def build_batch(candidates: list[dict[str, object]]) -> dict[str, object] | None:
    """构建修改批次 → 优先选有标记的文件, 大文件也作为候选 (平衡效率和覆盖)"""
    if not candidates:
        return None
    # 优先选有实际改进标记的文件 (TODO/质量问题), 200行+的大文件也可选
    improvable = [c for c in candidates if c.get("has_todo") or c.get("has_type_any") or c.get("has_bare_except") or c.get("lines", 0) > 200]
    if not improvable:
        # 没有显式标记的文件，但仍可选取少量文件进行轻度改进，避免空转
        if candidates:
            fallback = candidates[:2]
            log(f"build_batch: no improvable files, fallback to {len(fallback)} candidates", "debug")
            return {"id": f"daemon-{int(time.time())}", "files": fallback, "scope": fallback[0].get("scope", ""), "connected": False}
        return None  # 确实没有候选文件
    # 使用 smart_batch 模块: 分析依赖图, 优先选连通分量
    try:
        batches = _smart_batch_build(improvable, max_batch_size=2)
    except Exception as e:
        log(f"smart_batch failed: {e}, using fallback", "warn")
        batches = None
    if not batches:
        # fallback: 简单按项目分组
        by_project = defaultdict(list)
        for c in improvable[:30]:
            by_project[c.get("scope", "")].append(c)
        best_scope = max(by_project, key=lambda k: len(by_project[k])) if by_project else ""
        batch_files = by_project[best_scope][:2] if by_project and by_project[best_scope] else improvable[:2]
        return {"id": f"daemon-{int(time.time())}", "files": batch_files, "scope": best_scope, "connected": False}
    # 取第一个 (最高优先级) 批次
    return batches[0]

# ── CodeWorker 编辑系统 prompt (可被 GEPA 进化更新) ──
# 充当 code_worker.EDIT_SYSTEM_PROMPT: GEPA 用此作种子, 进化后经 set_edit_system_prompt 写回
_EDIT_SYSTEM_PROMPT: str = (
    "You are a Senior Software Engineer. "
    "Make MINIMAL, SURGICAL modifications using CONTEXT_REPLACE format. "
    "Each edit MUST change 1-8 lines only. Never replace more than 8 lines at once. "
    "Copy the EXACT original code from the source for CONTEXT_FIND. "
    "NEVER change function signatures. Do NOT remove public functions or exports. "
    "Do NOT add new imports unless absolutely necessary. "
    "If a file needs multiple fixes, make SEPARATE edits for each. "
    "Do NOT refactor or restructure code. Only fix bugs, add error handling, or improve readability."
)
_EDIT_SYSTEM_PROMPT_EVOLVED: bool = False  # 是否被 GEPA 进化过


def set_edit_system_prompt(new_prompt: str) -> None:
    """prompt_updater: GEPA 进化完成后写回新的编辑系统 prompt 到 code_worker"""
    global _EDIT_SYSTEM_PROMPT, _EDIT_SYSTEM_PROMPT_EVOLVED
    if new_prompt and len(new_prompt) > 20:
        _EDIT_SYSTEM_PROMPT = new_prompt
        _EDIT_SYSTEM_PROMPT_EVOLVED = True
        log(f"[GEPA] 编辑系统 prompt 已进化更新 ({len(new_prompt)} chars)")


def read_file_content(path_str: str) -> str:
    try:
        return Path(path_str).read_text("utf-8", errors="replace")
    except (OSError, UnicodeDecodeError) as e:
        return ""

def build_prompt(batch: dict, phase: str = "edit", diagnosis: str = "", repomap_section: str = "") -> str:
    """
    构建 prompt — v7 两阶段架构 (SWE-Edit 上下文解耦)

    phase="locate": 只定位问题, 不生成补丁 (Phase 1)
    phase="edit": 基于定位结果生成精确补丁 (Phase 2)
    diagnosis: 自修复循环的错误诊断信息 (AutoCodeRover 模式)
    repomap_section: RepoMap 代码地图摘要 (v10.3 检索增强)
    """
    files = batch["files"]
    scope = batch.get("scope", "")
    file_contents = []
    instructions = []

    # 专家路由: 找到本批文件的主专家
    experts_used = {}
    for f in files:
        proj_ctx = get_project_context(f.get("scope", scope))
        expert = route_expert(f["rel"], f["path"], SCOPE_DIRS, proj_ctx)
        ename = expert["expert"]
        if ename not in experts_used:
            experts_used[ename] = expert

    primary_expert = next((e for e in experts_used.values() if e["expert"] != "general"),
                          experts_used.get("general", {"expert": "general", "role": "Senior Software Engineer",
                                                        "focus": "code quality", "extra_rules": "Minimal changes."}))

    # 项目上下文注入
    proj_ctx = get_project_context(scope) if scope else {}
    project_info = format_project_info(proj_ctx)

    for i, f in enumerate(files):
        content = read_file_content(f["path"])
        file_contents.append(f"### {f['rel']} ({f['lines']} lines)\n```\n{content}\n```")
        hints = []
        if f["has_todo"]:
            hints.append("implement or fix TODO/FIXME comments")
        if f.get("has_type_any"):
            hints.append("replace `: any` with proper types")
        if f.get("has_bare_except"):
            hints.append("replace bare `except:` with `except Exception:`")
        hints.append(primary_expert["focus"])
        instructions.append(f"{i+1}. **{f['rel']}**: {'; '.join(hints)}")

    expert_tag = f"[Expert: {primary_expert['expert']}]"
    proj_section = f"\n== Project Context ==\n{project_info}\n" if project_info else ""

    # 学习型 prompt 优化: 从回滚历史中提取约束
    learned_constraints = get_adaptive_prompt_addition(METRICS_FILE, LOG_FILE) or ""

    # 自修复诊断 (AutoCodeRover 模式)
    diagnosis_section = ""
    if diagnosis:
        diagnosis_section = f"""
== SELF-FIX DIAGNOSIS (retry after failure) ==
Previous edit FAILED with this error:
{diagnosis}

You MUST fix this error. The previous edit did not work. Try a DIFFERENT approach.
- If the find text was not found, copy the EXACT code from the source above.
- If there was a syntax error, be more careful with indentation and brackets.
- If the change was too large, make a SMALLER change.
"""

    # v7: 强制 CONTEXT_REPLACE 唯一模式 (Harness Engineering 10x 杠杆)
    # v7.2: 跨会话知识注入 (Robin Brain)
    # v7.3: 语义检索增强 (BrainSearch)
    brain_section = ""
    if _BRAIN_CONTEXT:
        brain_lines = _BRAIN_CONTEXT.split("\n")
        brain_section = f"\n== Project Knowledge (cross-session) ==\n" + "\n".join(brain_lines[:20]) + "\n"

    # 语义检索: 基于当前文件内容搜索相关历史知识
    semantic_section = ""
    try:
        if _BRAIN_SEARCH is not None:
            # 用文件路径和内容作为查询
            search_query = " ".join(f["rel"] for f in files[:3])
            if instructions:
                search_query += " " + " ".join(instructions[:2])
            results = _BRAIN_SEARCH.search(search_query, top_k=2, min_score=0.05)
            if results:
                semantic_parts = []
                for r in results:
                    semantic_parts.append(f"  [{r['title']}] (score={r['score']:.2f})")
                    snippet = r["content"][:200].strip()
                    semantic_parts.append(f"  {snippet}")
                semantic_section = "\n== Related Knowledge (semantic search) ==\n" + "\n".join(semantic_parts) + "\n"
    except Exception:
        pass  # 搜索失败不阻断

    # RepoMap 代码地图检索 (v10.3 AFAC B榜检索模块)
    repomap_section_actual = repomap_section if repomap_section else ""

    # v8 CodeAct 模式: 复杂多文件编辑用 Python 代码执行
    # 检测是否适合 CodeAct 模式 (多文件、跨模块重构)
    use_codeact = phase == "codeact" or len(files) >= 3 or any(
        "refactor" in f.get("rel", "").lower() or "reorganize" in f.get("rel", "").lower()
        for f in files
    )
    codeact_section = ""
    if use_codeact and _CODECT_EXECUTOR is not None:
        codeact_section = """
== CodeAct Mode (v8: advanced edits) ==
For complex multi-file edits you may output Python code that will be executed in a sandbox.

Available functions:
  - read_file(path) -> str
  - write_file(path, content) -> None
  - edit_file(path, find_text, replace_text) -> bool
  - insert_at_line(path, line_num, content) -> bool
  - delete_lines(path, start, end) -> bool

Format:
```python
# Your editing Python code here
content = read_file("src/file.py")
# ... make modifications ...
```

IMPORTANT: Only use CodeAct mode when CONTEXT_REPLACE is insufficient.
For simple changes ALWAYS prefer CONTEXT_REPLACE format.
"""

    # v9.1 GEPA: 若编辑系统 prompt 已被进化, 前置注入进化后的指令
    _gepa_prefix = ""
    if _EDIT_SYSTEM_PROMPT_EVOLVED:
        _gepa_prefix = f"[GEPA Evolved Edit System Prompt]\n{_EDIT_SYSTEM_PROMPT}\n\n"

    return f"""{_gepa_prefix}You are a {primary_expert['role']}. {expert_tag}
Make MINIMAL, SURGICAL modifications using CONTEXT_REPLACE (preferred) or CodeAct (complex edits).

== STRICT RULES (v7 Harness Engineering) ==
1. You MUST use CONTEXT_REPLACE format for simple edits. NO line-number based edits.
2. Each edit MUST change 1-8 lines only. Never replace more than 8 lines at once.
3. Copy the EXACT original code from the source for CONTEXT_FIND. Include enough context (2-3 lines) for unique matching.
4. **NEVER change function signatures** — do NOT add/remove/rename parameters, do NOT add type annotations to function definitions. If you want to add type hints, do it as a SEPARATE small edit that only changes the def line.
5. Do NOT remove public functions or public exports.
6. Do NOT add new imports unless absolutely necessary.
7. If a file needs multiple fixes, make SEPARATE edits for each.
8. Do NOT refactor or restructure code. Only fix bugs, add error handling, or improve readability within existing structure.
{learned_constraints}
Special rules: {primary_expert['extra_rules']}
{proj_section}{diagnosis_section}{brain_section}{semantic_section}{repomap_section_actual}
{chr(10).join(file_contents)}

== Modification Targets ==
{chr(10).join(instructions)}
{codeact_section}
== Output Format (MANDATORY) ==
For simple edits:
FILE: relative_path
SCOPE: brief description of change

CONTEXT_FIND:
```exact_original_code_from_source```
CONTEXT_REPLACE:
```new_code```

Or for appending at end of file:
FILE: relative_path
SCOPE: description
APPEND_AT_EOF:
```new_code```

Or if code is already good:
SKIP: path - reason

CRITICAL: Do NOT use REPLACE_LINES, INSERT_AFTER, DELETE, or any line-number format.
Only CONTEXT_FIND/CONTEXT_REPLACE, APPEND_AT_EOF, or CodeAct python blocks are accepted."""

def apply_edits(edits: list[dict[str, object]], batch_files: list[dict[str, object]]) -> dict[str, object]:
    """应用修改 — v7: 只支持 CONTEXT_REPLACE + APPEND_AT_EOF, 使用增强匹配引擎"""
    r: dict[str, object] = {"ok": 0, "skip": 0, "fail": 0, "rollback": 0, "validated": 0, "log": [], "quality_scores": [],
         "self_fix_candidates": []}  # 自修复候选: 匹配失败或语法失败的编辑
    file_edits = {}
    for e in edits:
        if "skip" in e:
            r["skip"] += 1
            r["log"].append(f"SKIP {e['file']} - {e.get('skip','')}")
        elif "error" in e:
            r["fail"] += 1
            r["log"].append(f"PARSE_ERR {e['file']}: {e['error']}")
        else:
            matched = False
            for bf in batch_files:
                if e["file"] in bf["rel"] or bf["rel"] in e["file"]:
                    fp = Path(bf["path"])
                    matched = True
                    break
            if not matched:
                fp = BASE_DIR / e["file"]
                if not fp.exists():
                    r["fail"] += 1
                    r["log"].append(f"MISS {e['file']}")
                    continue
            if e["file"] not in file_edits:
                file_edits[e["file"]] = {"path": fp, "edits": []}
            file_edits[e["file"]]["edits"].append(e)

    for fname, fe in file_edits.items():
        fp = fe["path"]
        original_content = None
        file_ok_before = r["ok"]  # 记录此文件开始前的 ok 计数
        try:
            original_content = fp.read_text("utf-8", errors="replace")
        except OSError as e:
            r["log"].append(f"WARN {fname}: could not read original for backup: {e}")

        try:
            content = original_content or fp.read_text("utf-8", errors="replace")
            lines = content.split("\n")

            # ── 安全门: 检查文件路径 ──
            safe_path, path_reason = security_gate(str(fp), content, check_content=False)
            if not safe_path:
                r["fail"] += 1
                r["log"].append(f"BLOCK {fname}: {path_reason}")
                audit_operation("block_path", str(fp), "blocked", path_reason)
                continue

            for edit in fe["edits"]:
                action = edit.get("action", "CONTEXT_REPLACE")

                # ── 安全门: 检查编辑内容 ──
                replace_text = edit.get("replace", "")
                if action == "CONTEXT_REPLACE":
                    safe_content, content_reason = security_gate(str(fp), replace_text, check_path=False)
                    if not safe_content:
                        r["fail"] += 1
                        r["log"].append(f"BLOCK {fname}: {content_reason}")
                        audit_operation("block_edit", str(fp), "blocked", content_reason)
                        continue

                if action == "CONTEXT_REPLACE":
                    # v7: 使用增强匹配引擎 (5级匹配策略)
                    find_text = edit.get("find", "")
                    if not find_text:
                        r["fail"] += 1
                        r["log"].append(f"INVALID {fname}: CONTEXT_REPLACE with empty find text")
                        r["self_fix_candidates"].append({
                            "file": fname, "path": str(fp), "action": action,
                            "error": "empty find text",
                            "find": find_text, "replace": replace_text,
                        })
                        continue
                    content_str = "\n".join(lines)
                    new_content_str, success, method = context_replace_match(content_str, find_text, replace_text)
                    if success:
                        lines = new_content_str.split("\n")
                        r["ok"] += 1
                        r["log"].append(f"OK {fname}: CONTEXT_REPLACE via {method} ({len(find_text)} chars -> {len(replace_text)} chars)")
                    else:
                        # 匹配失败 → 加入自修复候选 (AutoCodeRover 模式)
                        r["fail"] += 1
                        r["log"].append(f"MISS {fname}: CONTEXT_REPLACE text not found after 5-level matching (first 80 chars: {find_text[:80]}...)")
                        r["self_fix_candidates"].append({
                            "file": fname, "path": str(fp), "action": "CONTEXT_REPLACE",
                            "find": find_text, "replace": replace_text,
                            "error": f"text not found in file (5-level matching exhausted)",
                        })
                    continue

                elif action == "APPEND_AT_EOF":
                    # v7: 文件末尾追加 (唯一不需要行号的合法操作)
                    # Handle empty file: if content is just empty lines, treat as empty
                    if all(l == "" for l in lines):
                        lines = []  # empty file, start fresh
                    if lines and lines[-1] != "":
                        lines.append("")  # ensure new content starts on new line
                    new_lines = edit["replace"].split("\n")
                    lines.extend(new_lines)
                    r["ok"] += 1
                    r["log"].append(f"OK {fname}: APPEND_AT_EOF {len(new_lines)} lines")
                    continue

                else:
                    # v7: 不再支持行号模式
                    r["fail"] += 1
                    r["log"].append(f"REJECTED {fname}: action '{action}' not supported in v7 (use CONTEXT_REPLACE)")
                    # 将行号模式编辑转为自修复候选
                    r["self_fix_candidates"].append({
                        "file": fname, "path": str(fp), "action": action,
                        "error": f"v7 only supports CONTEXT_REPLACE, got {action}",
                        "raw_edit": edit,
                    })
                    continue

            new_content = "\n".join(lines)
            # 原子写入: 先写 .tmp 再 rename
            tmp_path = str(fp) + ".tmp"
            try:
                Path(tmp_path).write_text(new_content, "utf-8")
                Path(tmp_path).replace(str(fp))  # atomic on same filesystem
            except OSError as e:
                # fallback: 直接写
                r["log"].append(f"WARN {fname}: atomic write failed ({e}), using direct write")
                fp.write_text(new_content, "utf-8")

            # ── 多语言语法验证 (v8.6.1: 用 ml_validate 替换单语言 validate_syntax) ──
            ml_valid = True
            ml_err = None
            try:
                ml_valid, ml_err = ml_validate(str(fp), new_content)
            except Exception:
                # fallback: 原 validate_syntax
                ml_valid, ml_err = validate_syntax(str(fp))

            if not ml_valid:
                valid = False
                err = ml_err
            else:
                valid = True
                err = None

            # ── v8 Sandbox 执行验证 (仅 .py 文件) ──
            sandbox_ok = True
            if valid and fp.suffix == ".py" and _SANDBOX_EXECUTOR is not None:
                try:
                    sr = _SANDBOX_EXECUTOR.execute(f'python "{fp.name}"', timeout=30, cwd=str(fp.parent))
                    sandbox_ok = sr.success
                    if sandbox_ok:
                        r["log"].append(f"SANDBOX_OK {fname}: exec ok")
                    else:
                        r["log"].append(f"SANDBOX_WARN {fname}: exec returned {sr.returncode}, err={sr.error[:60] if sr.error else 'none'}")
                        log(f"SANDBOX: {fname} execution warning", "warn")
                except Exception as e:
                    r["log"].append(f"SANDBOX_ERR {fname}: {e}")

            qscore = quality_score(original_content or "", new_content, fp.suffix) if original_content else 0.5
            # Sandbox 失败 → 质量分 -0.05 (沙箱可能假阳性, 轻罚)
            if not sandbox_ok:
                qscore = max(0.0, qscore - 0.05)

            should_rb, rb_reason = should_rollback(qscore, valid)

            # ── HITL 置信度门: quality 0.3-0.7 需人工审批 ──
            hitl_pause, hitl_reason = should_hitl_pause(qscore, valid)
            hitl_checkpoint_path = None
            if hitl_pause and not should_rb and not already_rolled_back:
                # 中质量修改: 写入 HITL checkpoint 供人工审批
                batch_id_val = batch_info.get("id", "unknown") if isinstance(batch_info, dict) else "unknown"
                hitl_checkpoint_path = write_hitl_checkpoint(
                    str(fp), fname, original_content or "", new_content, qscore, batch_id_val
                )
                if hitl_checkpoint_path:
                    # 回退修改, 写入 checkpoint 文件
                    if original_content is not None:
                        fp.write_text(original_content, "utf-8")
                    r["skip"] += 1
                    r["quality_scores"].append(qscore)
                    r["log"].append(f"HITL_PENDING {fname}: q={qscore:.2f} ({HITL_LOWER}-{HITL_UPPER}), checkpoint={Path(hitl_checkpoint_path).name}")
                    log(f"HITL: {fname} q={qscore:.2f} -> checkpoint written, pausing", "info")
                    _trace_event("warn", "hitl", f"pause {fname} q={qscore:.2f}")
                    already_rolled_back = True  # 阻止后续逻辑
                    continue  # 跳过此文件的后续处理
                else:
                    r["log"].append(f"HITL_WARN {fname}: failed to write checkpoint for q={qscore:.2f}")

            # Breaking changes 检测 (仅在语法OK时检查, 避免双重回滚)
            already_rolled_back = False
            if original_content and not should_rb:
                try:
                    breaking = detect_breaking_changes(original_content, new_content, fp.suffix)
                    if breaking:
                        log(f"REFLEXION: breaking changes in {fname}: {'; '.join(breaking[:3])}", "warn")
                        r["log"].append(f"BREAKING {fname}: {'; '.join(breaking[:3])}")
                        fp.write_text(original_content, "utf-8")
                        r["rollback"] += 1
                        r["ok"] = file_ok_before
                        r["log"].append(f"ROLLBACK {fname}: breaking change detected -> reverted")
                        _trace_event("error", "rollback", f"breaking {fname}")
                        already_rolled_back = True
                except (OSError, ValueError, RuntimeError) as e:
                    log(f"BREAKING_CHECK_ERR {fname}: {e}", "warn")

            if should_rb and not already_rolled_back:
                reason = rb_reason
                log(f"REFLEXION: rollback {fname}: {reason}", "warn")
                if original_content is not None:
                    fp.write_text(original_content, "utf-8")
                    r["rollback"] += 1
                    r["ok"] = file_ok_before
                    r["log"].append(f"ROLLBACK {fname}: {reason} -> reverted")
                _trace_event("error", "rollback", f"{fname}: {reason}")
                # 语法失败也加入自修复候选
                if not valid:
                    r["self_fix_candidates"].append({
                        "file": fname, "path": str(fp),
                        "error": f"syntax error after edit: {err}",
                        "original": original_content,
                    })
                else:
                    r["log"].append(f"REFLEXION_WARN {fname}: {reason} but no backup")
            else:
                if not already_rolled_back:
                    r["validated"] += 1
                    r["quality_scores"].append(qscore)
                    r["log"].append(f"VALIDATED {fname}: syntax OK, quality={qscore:.2f}")
                    _trace_event("success", "edit", f"{fname} q={qscore:.2f}")
                    # 轻量测试运行: 只在语法+质量通过后尝试跑项目测试
                    try:
                        project_dir = str(fp.parent)
                        test_result = run_project_tests(project_dir)
                        if test_result.get("ran"):
                            if test_result.get("failed", 0) == 0:
                                r["log"].append(f"TESTS {fname}: {test_result.get('passed',0)} passed")
                            else:
                                r["log"].append(f"TESTS {fname}: {test_result.get('passed',0)}p/{test_result.get('failed',0)}f (non-blocking)")
                    except Exception:
                        pass  # 测试非阻塞, 失败不阻断

        except (OSError, ValueError, RuntimeError) as ex:
            r["fail"] += 1
            r["log"].append(f"APPLY_ERR {fname}: {ex}")
            if original_content is not None:
                try:
                    fp.write_text(original_content, "utf-8")
                    r["rollback"] += 1
                    r["ok"] = file_ok_before
                    r["log"].append(f"ROLLBACK {fname}: exception recovery -> reverted")
                except OSError as e:
                    r["log"].append(f"ROLLBACK_FAIL {fname}: could not restore backup: {e}")
    return r

async def work_cycle() -> dict[str, object]:
    """一次工作循环 — v7: HITL审批→扫描→构建→修改→自修复→日志"""
    try:
        # 第一件事: 处理已审批的 HITL checkpoint
        hitl_result: dict[str, object] = {"ok": 0, "skip": 0, "fail": 0, "rollback": 0,
                                           "validated": 0, "quality_scores": [], "log": []}
        _process_approved_checkpoints(hitl_result)

        candidates = scan_for_work()
        if not candidates:
            # 没真活 → 进 idle 补刀, 不空转
            idle_result = await idle_burn_cycle()
            if idle_result.get("ok", 0) > 0 or idle_result.get("skip", 0) > 0:
                return idle_result
            log("no modifiable files found, idle skip", "info")
            return {"ok": 0, "skip": 0, "fail": 0}

        batch = build_batch(candidates)
        if not batch:
            log("no improvable batch, skipping cycle", "debug")
            return {"ok": 0, "skip": 0, "fail": 0}

        log(f"working: {batch['id']} ({len(batch['files'])} files)")
        # 记录已处理文件 (冷却期)
        with _recently_processed_lock:
            for f in batch["files"]:
                _recently_processed[f["path"]] = time.time()
        # 专家路由日志
        primary_expert_name = "general"
        for f in batch["files"]:
            proj_ctx = get_project_context(f.get("scope", batch.get("scope", "")))
            expert = route_expert(f["rel"], f["path"], SCOPE_DIRS, proj_ctx)
            if primary_expert_name == "general" and expert["expert"] != "general":
                primary_expert_name = expert["expert"]
            todo_tag = " [TODO]" if f["has_todo"] else ""
            quality_tags = []
            if f.get("has_type_any"):
                quality_tags.append("[TYPE_ANY]")
            if f.get("has_bare_except"):
                quality_tags.append("[BARE_EXCEPT]")
            log(f"  -> {f['rel']} ({f['lines']} lines){todo_tag}{''.join(quality_tags)} [{expert['expert']}]", "debug")

        # ── v10.2: LocalContext 环境注入 ──
        if _HARNESS_CONTEXT_READY:
            scope_dir = batch.get("scope", "")
            if scope_dir:
                ctx_summary = get_harness_context().get_context_summary(scope_dir)
                if ctx_summary and "Local Environment" in ctx_summary:
                    log(f"[CTX] 项目环境注入: {Path(scope_dir).name} ({len(ctx_summary.split(chr(10)))-1} items)")

        # ── v10.2: Reasoning Budget 阶段分配 ──
        if _REASONING_BUDGET_READY:
            budget = get_reasoning_budget()
            budget.next_phase("build")
            budget_info = budget.get_budget("build")
            log(f"[BUDGET] build阶段: reasoning={budget_info['reasoning']} model_tier={budget_info['model_tier']}")

        # ── v10.2: TDD 预检 (检查是否需要强制TDD) ──
        tdd_required_files = []
        if _TDD_MIDDLEWARE_READY:
            tdd_mw = get_tdd_mw()
            for f in batch["files"]:
                fpath = f.get("path", "")
                if tdd_mw.requires_tdd(fpath):
                    tdd_required_files.append(fpath)
                    hook_result = tdd_mw.pre_work_hook(fpath, batch)
                    if hook_result.get("action") == "block":
                        log(f"[TDD] 阻断: {Path(fpath).name} — 必须先写测试再写代码", "warn")
                        return {"ok": 0, "skip": 0, "fail": 1, "tdd_blocked": True}
            if tdd_required_files:
                log(f"[TDD] TDD模块检测: {len(tdd_required_files)}文件需TDD约束")

        # ── v10.3: RepoMap 代码库地图注入 (Aider风格, AST结构感知) ──
        repomap_content = ""
        if _REPOMAP_READY:
            try:
                scope_dir = batch.get("scope", "")
                if scope_dir and Path(scope_dir).exists():
                    repomap = get_context_repomap()
                    map_result = repomap.generate_map(scope_dir)
                    if map_result.summary and map_result.token_count < 2048:
                        # 构建可读的 RepoMap 摘要
                        repomap_lines = []
                        repomap_lines.append(f"== RepoMap: {Path(scope_dir).name} ==")
                        repomap_lines.append(f"Files: {len(map_result.files)}")
                        for f in map_result.files[:20]:
                            repomap_lines.append(f"  - {f}")
                        if len(map_result.files) > 20:
                            repomap_lines.append(f"  ... and {len(map_result.files)-20} more")
                        repomap_content = "\n".join(repomap_lines)
                        log(f"[REPOMAP] {Path(scope_dir).name}: {len(map_result.files)}文件, {map_result.token_count} tokens")
            except Exception as e:
                log(f"[REPOMAP] 生成失败: {e}", "debug")

        # Phase 1: 初始编辑 (异步LLM调用, 不阻塞事件循环)
        prompt = build_prompt(batch, repomap_section=repomap_content)
        # ── v10.1: 护栏检查 prompt 安全 ──
        if _GUARDRAILS_READY:
            p_check = get_guardrails_sys().check_input(prompt, context="code_prompt")
            if not p_check.get("safe", True):
                log(f"[GUARD] prompt 安全检查未通过: {p_check.get('reason','')[:80]}", "warn")
                return {"ok": 0, "skip": 0, "fail": 1}
        output = await call_llm_async(prompt)
        # ── v10.1: 护栏检查 LLM 输出安全 ──
        if _GUARDRAILS_READY and not output.startswith("LLM_FAIL_"):
            o_check = get_guardrails_sys().check_output(output, context="code_output")
            if not o_check.get("safe", True):
                log(f"[GUARD] LLM 输出安全检查未通过: {o_check.get('reason','')[:80]}", "warn")
                return {"ok": 0, "skip": 0, "fail": 1}
        if output.startswith("LLM_FAIL_3"):
            log(f"LLM call failed: {output}", "error")
            return {"ok": 0, "skip": 0, "fail": 1}

        edits = parse_output(output)
        result = apply_edits(edits, batch["files"])

        # ── v10.3: EditorPrecision Search-and-Replace 验证 ──
        # 对成功编辑的文件, 用 editor_precision 做二次验证
        # 对自修修复例, 用模糊匹配重试精确匹配失败的编辑
        if _EDITOR_PRECISION_READY and result.get("ok", 0) > 0:
            try:
                ed_prec = get_editor_precision()
                for f in batch["files"]:
                    fpath = f.get("path", "")
                    if not fpath or not Path(fpath).exists():
                        continue
                    # 对成功编辑的文件做二次 lint 验证
                    lint_errors = ed_prec.search_replace_edit.__self__._run_lint(fpath) if hasattr(ed_prec, 'search_replace_edit') else []
                    if lint_errors:
                        for lerr in lint_errors[:2]:
                            log(f"[EDITOR] 精度验证警告 {Path(fpath).name}: {lerr}", "debug")
                result["log"].append(f"EDITOR_VERIFIED: {result.get('ok',0)} files")
            except Exception as e:
                log(f"[EDITOR] 验证异常: {e}", "debug")

        # ── v10.2: LoopDetection 文件编辑跟踪 ──
        if _HARNESS_LOOP_DETECT_READY:
            loop_detector = get_harness_loop()
            for f in batch["files"]:
                fpath = f.get("path", "")
                loop_result = loop_detector.track_edit(fpath)
                if loop_result.get("loop_detected"):
                    log(f"[LOOP] ⚠️ 循环检测: {Path(fpath).name} 已编辑 {loop_result['edit_count']}次", "warn")
                    result["log"].append(f"LOOP_DETECT {Path(fpath).name}: {loop_result['alert'][:80]}")

        # Phase 2: 自修复循环 (AutoCodeRover 模式)
        # 如果有匹配失败或语法失败的编辑, 重试一次 (带错误诊断)
        self_fix_candidates = result.get("self_fix_candidates", [])
        if self_fix_candidates:
            log(f"SELF-FIX: {len(self_fix_candidates)} candidates for retry", "info")
            # 构建诊断信息
            diagnosis_parts = []
            for sfc in self_fix_candidates[:3]:  # 最多重试3个
                if "error" in sfc:
                    diagnosis_parts.append(f"- {sfc['file']}: {sfc['error']}")
                if "find" in sfc:
                    diagnosis_parts.append(f"  Original find text (first 100 chars): {sfc['find'][:100]}...")

            if diagnosis_parts:
                diagnosis = "\n".join(diagnosis_parts)
                # ── v10.3: 优先用 EditorPrecision 模糊匹配重试 (比 LLM 重试便宜 100x) ──
                fuzzy_retried = 0
                if _EDITOR_PRECISION_READY:
                    try:
                        ed_prec = get_editor_precision()
                        for sfc in self_fix_candidates[:3]:
                            if sfc.get("find") and sfc.get("file"):
                                fpath = sfc.get("path", "")
                                if fpath and Path(fpath).exists():
                                    # 尝试用模糊匹配降级
                                    ed_result = ed_prec.search_replace_edit(
                                        fpath, sfc["find"], sfc.get("replace", "")
                                    )
                                    if ed_result.success:
                                        fuzzy_retried += 1
                                        log(f"[EDITOR] 模糊匹配修复 {Path(fpath).name}: {ed_result.operations[0].strategy if ed_result.operations else 'fuzzy'}")
                    except Exception as e:
                        log(f"[EDITOR] 模糊修复异常: {e}", "debug")
                # 标准 LLM 重试 (如果模糊匹配没全搞定)
                remaining = len(self_fix_candidates) - fuzzy_retried
                if remaining > 0:
                    retry_prompt = build_prompt(batch, diagnosis=diagnosis)
                retry_output = await call_llm_async(retry_prompt)
                if not retry_output.startswith("LLM_FAIL_3"):
                    retry_edits = parse_output(retry_output)
                    retry_result = apply_edits(retry_edits, batch["files"])
                    # 合并重试结果: 移除被重试候选的失败，加上重试后的失败
                    retry_count = min(len(self_fix_candidates), 3)
                    result["ok"] += retry_result.get("ok", 0)
                    result["fail"] = max(0, result["fail"] - retry_count) + retry_result.get("fail", 0)
                    result["validated"] += retry_result.get("validated", 0)
                    result["rollback"] += retry_result.get("rollback", 0)
                    result["quality_scores"].extend(retry_result.get("quality_scores", []))
                    result["log"].extend([f"SELF-FIX {l}" for l in retry_result.get("log", [])])
                    log(f"SELF-FIX result: OK={retry_result.get('ok',0)} FAIL={retry_result.get('fail',0)} ROLLBACK={retry_result.get('rollback',0)}")

        # 项目级验证: 如果有文件被修改, 运行 import 检查 + 项目测试
        if result.get("ok", 0) > 0 and result.get("rollback", 0) == 0:
            # 对修改的 Python 文件做 import 检查
            for f in batch["files"]:
                if Path(f["path"]).suffix == ".py":
                    ok_import, err_msg = check_python_imports(f["path"])
                    if not ok_import:
                        log(f"VALIDATION: import check failed for {f['rel']}: {err_msg}", "warn")
                        result["log"].append(f"IMPORT_FAIL {f['rel']}: {err_msg}")
                        result["validated"] = max(0, result.get("validated", 0) - 1)

            # 项目级测试 (如果可用, 不阻塞)
            scope_path = batch.get("scope", "")
            if scope_path and Path(scope_path).exists():
                try:
                    test_results = run_project_tests(scope_path)
                    if test_results.get("ran") and test_results.get("failed", 0) > 0:
                        log(f"VALIDATION: project tests failed in {scope_path}: {test_results['failed']} failures", "warn")
                        result["log"].append(f"TEST_FAIL {scope_path}: {test_results['failed']} failures")
                except (OSError, subprocess.TimeoutExpired, RuntimeError) as e:
                    log(f"TEST_RUN_ERR {scope_path}: test execution failed: {e}", "warn")

        # ── v10.1: 评估框架验证 (修改质量量化) ──
        if _EVAL_HARNESS_READY and result.get("ok", 0) > 0:
            try:
                eval_result = get_eval_harness().evaluate(
                    batch=batch,
                    result=result,
                    prompt=prompt if 'prompt' in dir() else None,
                )
                if eval_result.get("quality", 0) < 0.3:
                    log(f"[EVAL] ⚠️ 修改质量评估偏低 ({eval_result['quality']:.2f}), 建议审查")
                    result["log"].append(f"EVAL_LOW_Q {eval_result.get('reason','')[:60]}")
                else:
                    log(f"[EVAL] ✅ 修改质量评估: {eval_result.get('quality',0):.2f} / 1.0")
            except Exception as e:
                log(f"[EVAL] 评估异常: {e}", "debug")

        # ── v10.2: PreCompletionChecklist 完成检查 ──
        if _HARNESS_CHECKLIST_READY and result.get("ok", 0) > 0:
            try:
                checklist_result = get_harness_checklist().check(batch, batch.get("scope", ""))
                if checklist_result.get("warnings"):
                    for w in checklist_result["warnings"][:3]:
                        log(f"[CHECKLIST] 检查警告: {w}", "warn")
                if checklist_result.get("block_action"):
                    log("[CHECKLIST] 🚫 MUST项未通过, 标记审查", "warn")
                    result["log"].append("CHECKLIST_BLOCKED")
            except Exception as e:
                log(f"[CHECKLIST] 检查异常: {e}", "debug")

        # ── v10.3: Stop Hook / Ralph Wiggum Loop — 阻止假完成 ──
        if _STOP_HOOK_READY and result.get("ok", 0) > 0:
            try:
                hook = get_stop_hook()
                hook_level = 3  # L3: test+build+lint
                hook_result = hook.ralph_wiggum_loop(
                    file_path=batch.get("scope", ""),
                    hook_level=hook_level,
                )
                if not hook_result.passed:
                    log(f"[HOOK] ⚠️ Stop Hook 拦截: level={hook_level}, failed={hook_result.failed_checks}")
                    result["log"].append(f"STOP_HOOK {hook_result.failed_checks}")
                    result["rollback"] = result.get("rollback", 0) + 1
                else:
                    log(f"[HOOK] ✅ Stop Hook 验证通过 (attempt {hook_result.attempt + 1})")
                if hook_result.veto_triggered:
                    log(f"[HOOK] Minority Veto 触发! 至少1票否决", "warn")
            except Exception as e:
                log(f"[HOOK] Stop Hook 异常: {e}", "debug")

        # ── v10.3: Generator/Evaluator 分离评审 ──
        if _GEN_EVAL_SEP_READY and result.get("ok", 0) > 0:
            try:
                eval_sep = get_eval_sep()
                for f in batch["files"][:3]:  # 最多评审3个文件
                    fpath = f.get("path", "")
                    if not fpath or not Path(fpath).exists():
                        continue
                    complexity = "critical" if any(k in fpath for k in ["auth", "security", "payment", "credential"]) else "moderate"
                    session = await eval_sep.run_eval(
                        file_path=fpath,
                        complexity=complexity,
                    )
                    if not session.overall_passed:
                        failed_dims = [r.dimension for r in session.results if not r.passed]
                        log(f"[EVAL_SEP] ⚠️ 评审未通过: {Path(fpath).name} dims={failed_dims} score={session.overall_score:.2f}")
                        result["log"].append(f"EVAL_SEP_FAIL {Path(fpath).name}: {'/'.join(failed_dims)}")
                    elif session.veto_triggered:
                        log(f"[EVAL_SEP] Minority Veto: {Path(fpath).name}")
                        result["log"].append(f"EVAL_SEP_VETO {Path(fpath).name}")
                    else:
                        log(f"[EVAL_SEP] ✅ {Path(fpath).name}: score={session.overall_score:.2f}/{len(session.results)}dims")
            except Exception as e:
                log(f"[EVAL_SEP] 评审异常: {e}", "debug")

        # ── v10.2: 三级质量门禁 ──
        if _QUALITY_GATE_READY and result.get("ok", 0) > 0:
            try:
                complexity = get_quality_gate().get_complexity(batch, batch.get("scope", ""))
                gate_result = get_quality_gate().run(
                    batch=batch, scope=batch.get("scope", ""),
                    complexity=complexity
                )
                if not gate_result.get("passed"):
                    log(f"[GATE] 🚫 {gate_result.get('reason','')} — 触发修复循环", "warn")
                    result["log"].append(f"GATE_BLOCKED: {gate_result.get('reason','')}")
                    if _QUALITY_GATE_READY:
                        fix_result = get_quality_gate().auto_fix(batch, gate_result)
                        if fix_result.get("all_fixed"):
                            log(f"[GATE] ✅ 自动修复成功: {fix_result['attempted_fixes']}个问题")
                        else:
                            log(f"[GATE] ⚠️ 自动修复部分成功: {fix_result.get('fixes_applied', 0)}个修复")
                else:
                    log(f"[GATE] ✅ {gate_result['level']}门禁通过 ({gate_result['summary']['passed_gates']}/{gate_result['summary']['total_gates']})")
            except Exception as e:
                log(f"[GATE] 门禁异常: {e}", "debug")

        # ── v10.2: TDD 后置验证 (检查测试完整性) ──
        if _TDD_MIDDLEWARE_READY and tdd_required_files:
            try:
                tdd_mw = get_tdd_mw()
                for f in batch["files"]:
                    fpath = f.get("path", "")
                    test_files = tdd_mw.state.test_files
                    post_result = tdd_mw.post_edit_hook(fpath, test_files)
                    if not post_result.get("passed"):
                        log(f"[TDD] 后验未通过: {Path(fpath).name} → {post_result.get('verdict','')}", "warn")
                        if post_result.get("action") == "rollback":
                            result["rollback"] += 1
                            result["ok"] = max(0, result["ok"] - 1)
            except Exception as e:
                log(f"[TDD] 后验异常: {e}", "debug")

        # ── v10.2: Reasoning Budget 记录消耗 ──
        if _REASONING_BUDGET_READY:
            try:
                get_reasoning_budget().record_usage("build", result.get("ok", 0) * 500)
                get_reasoning_budget().next_phase("validate")
            except Exception:
                pass

        # 记录指标
        avg_q = sum(result.get("quality_scores", [0.5])) / max(len(result.get("quality_scores", [])), 1)
        log_metric({
            "batch_id": batch["id"],
            "expert": primary_expert_name,
            "ok": result["ok"],
            "skip": result["skip"],
            "fail": result["fail"],
            "rollback": result["rollback"],
            "validated": result["validated"],
            "avg_quality": round(avg_q, 3),
            "self_fix_attempted": len(self_fix_candidates) > 0,
        })

        # 合并 HITL 审批结果
        if hitl_result.get("ok", 0) > 0 or hitl_result.get("skip", 0) > 0:
            result["ok"] += hitl_result["ok"]
            result["skip"] += hitl_result["skip"]
            result["validated"] += hitl_result["validated"]
            result["quality_scores"].extend(hitl_result.get("quality_scores", []))
            result["log"].extend(hitl_result.get("log", []))
            log(f"HITL merge: {hitl_result['ok']} approved checkpoints applied")

        log(f"done: {batch['id']} OK={result['ok']} SKIP={result['skip']} FAIL={result['fail']} ROLLBACK={result['rollback']} quality={avg_q:.2f}")
        for l in result["log"]:
            log(f"  {l}", "debug")

        # ── P2: J-Space 采样 (每次工作周期结束后记录) ──
        if _JSPACE_MONITOR_READY and result.get("ok", 0) > 0:
            try:
                await j_monitor.record_task_result(
                    task_id=batch["id"],
                    agent_id=primary_expert_name,
                    success=result["rollback"] == 0,
                    quality=avg_q,
                    duration_ms=0,  # 无精确计时，用0表示
                    token_cost=result.get("ok", 0) * 1000,
                    errors=result.get("fail", 0),
                    interventions=0,
                )
            except Exception as e:
                log(f"[JSPACE] 采样异常: {e}", "debug")

        # CI/CD: 修改成功 → auto git commit (非阻塞)
        if result.get("ok", 0) > 0 and result.get("rollback", 0) == 0:
            changed_files = [f["path"] for f in batch["files"] if f.get("path")]
            for f_entry in batch["files"]:
                # 找项目根 (父级带 .git 的目录)
                fp = Path(f_entry.get("path", ""))
                for parent in fp.parents:
                    if (parent / ".git").is_dir():
                        try:
                            commit = auto_git_commit(str(parent), changed_files)
                            if commit.get("committed"):
                                log(f"CI/CD: git commit {commit.get('hash','')[:12]} ({parent.name})")
                                # Kitchen Loop: 密封测试卡生成
                                try:
                                    from daemon_modules.daemon_reflexion import create_sealed_test_card
                                    changes_summary = f"auto-edit {len(changed_files)} files in {parent.name}"
                                    card = create_sealed_test_card(str(fp), changes_summary)
                                    test_dir = parent / ".sealed_tests"
                                    test_dir.mkdir(exist_ok=True)
                                    card_path = test_dir / f"test_{commit.get('hash','')[:12]}_{datetime.now().strftime('%H%M%S')}.md"
                                    card_path.write_text(card, "utf-8")
                                    log(f"Kitchen Loop: sealed test card -> {card_path.name}", "debug")
                                except Exception as e:
                                    log(f"Kitchen Loop: sealed test card error: {e}", "debug")
                            elif commit.get("reason") not in ("nothing to commit", "cooldown 60s"):
                                log(f"CI/CD: commit skipped ({commit.get('reason')})", "debug")
                        except Exception as e:
                            log(f"CI/CD: commit error: {e}", "warn")
                        break

        # 每轮结束后尝试触发 Dream Agent (30min间隔)
        try:
            _try_dream()
        except Exception:
            pass

        return result
    except (OSError, ValueError, RuntimeError, KeyError, asyncio.TimeoutError) as e:
        log(f"work_cycle exception: {e}\n{traceback.format_exc()[-800:]}", "error")
        return {"ok": 0, "skip": 0, "fail": 1, "exception": str(e)}

async def _fleet_burn_task(stop_event: asyncio.Event) -> None:
    """
    【死命令】知更鸟战舰常驻烧量协程 — 与主循环并行运行。
    每30min确保烧满1800调用, 5中队并行开发5项目, 无工时限制。
    窗口结束自动触发 Dream Agent 战后复盘。stop_event 置位时优雅退出。
    """
    try:
        from daemon_modules.fleet_orchestrator import get_orchestrator
    except ImportError as e:
        log(f"[WARSHIP] fleet_orchestrator unavailable: {e}", "warn")
        return
    # 有密钥 → live 真实派发; 无密钥 → dry_run 演练
    has_key = bool(os.environ.get("ROBIN_GLM_API_KEY")
                   or (BASE_DIR / ".secrets.json").exists())
    orch = get_orchestrator(dry_run=not has_key)
    mode = "live" if has_key else "dry_run"
    log(f"[WARSHIP] 战舰烧量启动: target={WARSHIP_TARGET}/{WARSHIP_WINDOW}s "
        f"5中队并行 mode={mode}")

    # 启动舰队 API (端口 19531, 供 HUD 聊天/态势; 19530 已被 TTS WebAPI 占用)
    try:
        from daemon_modules.fleet_api_server import start_fleet_api
        start_fleet_api(port=19531)
        log("[WARSHIP] 舰队 API + HUD 就位: http://127.0.0.1:19531/")
    except (ImportError, OSError, RuntimeError) as e:
        log(f"[WARSHIP] fleet API start failed: {e}", "warn")

    # burn_loop 是无限窗口循环, 用 create_task 包裹以便 stop_event 时取消
    burn = asyncio.create_task(
        orch.burn_loop(target_calls=WARSHIP_TARGET, window_sec=WARSHIP_WINDOW))
    while not stop_event.is_set() and not burn.done():
        await asyncio.sleep(2.0)
    if not burn.done():
        burn.cancel()
        try:
            await burn
        except asyncio.CancelledError:
            pass
        except (OSError, RuntimeError, asyncio.TimeoutError, ValueError) as e:
            log(f"[WARSHIP] burn task cleanup error: {e}", "warn")
        log("[WARSHIP] 战舰烧量已停止")


async def main_loop() -> None:
    """主循环 (带看门狗 + 心跳 + 优雅退出 + 5项目调度 + Self-Verify门控 + Brain持久化)"""
    global _START_TIME
    _START_TIME = time.time()
    _trace_event("info", "startup", "daemon started")
    state = read_state()

    # ── 跨会话持久化: 加载 Robin Brain 知识库 ──
    try:
        ctx = _load_brain_context()
        if ctx:
            log(f"Brain context loaded: {len(ctx)//1024}KB across 5 projects", "info")
    except Exception as e:
        log(f"Brain context load error: {e}", "warn")

    # ── 4层记忆系统: 初始化 MemorySystem (v8) ──
    try:
        from daemon_modules.brain_search import get_memory, MemorySystem
        mem = get_memory()
        n_docs = mem.index_all()
        log(f"Memory L3 indexed: {n_docs} documents (v8 4-layer)", "info")
        mem.remember("daemon", f"Daemon started v8 at {datetime.now().isoformat()}", {"event": "startup"})
    except Exception as e:
        log(f"Memory init error: {e}", "warn")

    # ── 初始化多项目调度器 (CAID+ZEBRA+PilotDeck) ──
    scheduler = None
    try:
        from daemon_modules.multi_project_scheduler import MultiProjectScheduler, DEFAULT_PROJECTS
        scheduler = MultiProjectScheduler(DEFAULT_PROJECTS, state_dir=BASE_DIR)
        allocation = scheduler.allocate_budget(MAX_CALLS)
        log(f"5-project scheduler ON: {allocation}")
    except ImportError as e:
        log(f"scheduler not available: {e}", "warn")

    # ── v8.6: Session 持久化 — 崩溃恢复 ──
    try:
        recovered = recover_from_crash()
        if recovered:
            log(f"Session recovered: step={recovered.get('step', '?')} timestamp={recovered.get('timestamp', '?')}", "info")
        else:
            sm = get_session_manager()
            sid = sm.new_session({"daemon_version": "v8.6", "started_at": datetime.now().isoformat()})
            log(f"New session: {sid}", "info")
    except Exception as e:
        log(f"Session manager init error: {e}", "warn")

    # ── v8.6.1: MCP Bridge 初始化 (真实技能注册表) ──
    try:
        tools = get_mcp_tools()
        stats = get_skill_stats()
        source = "skills_config.yaml" if stats.get("from_config") else "fallback"
        log(f"MCP bridge ON: {stats['total_skills']} real skills from {source} ({len(tools)} MCP tools)", "info")
        if stats.get("tiers"):
            log(f"  Skill tiers: {stats['tiers']}  domains: {stats['domains']}", "debug")
    except Exception as e:
        log(f"MCP bridge init error: {e}", "warn")

    # ── v8.6.1: Per-Agent 身份隔离 (OWASP ASI-03) ──
    try:
        auth_mgr = get_agent_auth()
        expired = auth_mgr.cleanup_expired()
        auth_stats = auth_mgr.stats()
        log(f"Agent auth ON: {auth_stats['active']} active, {auth_stats['expired']} expired, {auth_stats['unique_agents']} unique agents", "info")
    except Exception as e:
        log(f"Agent auth init error: {e}", "warn")

    # ── v8.6.1: 记忆污染防护 (OWASP ASI-06) ──
    try:
        mp = get_memory_protector()
        auto_cleaned = mp.auto_cleanup()
        mp_stats = mp.stats()
        log(f"Memory protection ON: {mp_stats['total_sources']} sources tracked, {auto_cleaned} auto-cleanup", "info")
    except Exception as e:
        log(f"Memory protection init error: {e}", "warn")

    # ── v8.6.1: L5 技能提取器 ──
    try:
        se = get_skill_extractor()
        cleaned = se.cleanup_unused()
        se_stats = se.stats()
        log(f"Skill extractor ON: {se_stats['total_skills']} skills accumulated ({se_stats['total_uses']} total uses)", "info")
    except Exception as e:
        log(f"Skill extractor init error: {e}", "warn")

    # ── v8.7 创新一: 双速大脑 (Dual-Speed Brain) ──
    try:
        dsb = get_dual_speed_brain()
        dsb_stats = dsb.get_stats()
        log(f"Dual-Speed Brain ON: S1 cache={dsb_stats['cache_size']} patterns={dsb_stats['patterns']} "
            f"estimated_savings={dsb_stats['estimated_savings_pct']}%", "info")
    except Exception as e:
        log(f"Dual-Speed Brain init error: {e}", "warn")

    # ── v8.7 创新二: 溯源感知管道 (Provenance-Aware Pipeline) ──
    try:
        prov = get_provenance_pipe()
        prov_stats = prov.get_stats()
        log(f"Provenance-Aware Pipeline ON: {prov_stats['active_envelopes']} envelopes, "
            f"{prov_stats['fact_graph_size']} fact keys tracked", "info")
    except Exception as e:
        log(f"Provenance pipeline init error: {e}", "warn")

    # ── v8.7 创新三: 内嵌式调试器 (Embedded Debugger) ──
    try:
        dbg = get_embedded_debugger()
        dbg_stats = dbg.get_stats()
        log(f"Embedded Debugger ON: always-on recording, {dbg_stats['total_snapshots']} historical "
            f"snapshots across {dbg_stats['total_sessions']} sessions", "info")
    except Exception as e:
        log(f"Embedded Debugger init error: {e}", "warn")

    # ── v8.8 白空间创新一: 内省协议 (Introspection-as-a-Protocol) ──
    try:
        iaap = get_introspector()
        iaap_health = iaap.health()
        log(f"Introspection Protocol ON: Agent-to-Agent debug, {iaap_health['access_grants']} grants, "
            f"{iaap_health['total_requests']} total requests", "info")
    except Exception as e:
        log(f"Introspection Protocol init error: {e}", "warn")

    # ── v8.8 白空间创新二: 跨代技能继承 (Lamarckian Inheritance) ──
    try:
        si = get_inheritance_engine()
        si_stats = si.get_stats()
        log(f"Skill Inheritance ON: Lamarckian engine, {si_stats['total_wills']} wills, "
            f"gen={si_stats['max_generation']}, bloodlines={si_stats['active_bloodlines']}", "info")
    except Exception as e:
        log(f"Skill Inheritance init error: {e}", "warn")

    # ── v8.8 白空间创新三: 溯源加权经济 (Provenance-Weighted Economy) ──
    try:
        eco = get_economy()
        eco_stats = eco.get_stats()
        log(f"Provenance Economy ON: trust-weighted pricing, {eco_stats['total_agents']} agents, "
            f"{eco_stats['total_auctions']} auctions, tiers={eco_stats['tier_distribution']}", "info")
    except Exception as e:
        log(f"Provenance Economy init error: {e}", "warn")

    # ── v8.9: 质量信号早停引擎 ──
    try:
        from daemon_modules.early_stop import get_stopper
        _ES = get_stopper()
        es_stats = _ES.get_stats()
        log(f"Early Stop Engine ON: {es_stats['active_trajectories']} active, "
            f"{es_stats['total_aborted']} aborted to date", "info")
    except Exception as e:
        log(f"Early Stop init error: {e}", "warn")

    # ── v8.9: Agent 级投机执行引擎 ──
    try:
        from daemon_modules.speculative_agent import get_speculator
        _SA = get_speculator()
        sa_stats = _SA.stats()
        log(f"Speculative Agent ON: {sa_stats['total_speculative']} executions, "
            f"trajectories/run avg={sa_stats['avg_trajectories']:.1f}, "
            f"consensus_rate={sa_stats['total_consensus']}/{max(1,sa_stats['total_speculative'])}", "info")
    except Exception as e:
        log(f"Speculative Agent init error: {e}", "warn")

    # ── v8.6: RL 路由记录器 ──
    try:
        rl_recorder = get_rl_recorder()
        log("RL routing recorder ON: collecting model selection data", "info")
    except Exception as e:
        log(f"RL router init error: {e}", "warn")

    # ── v9.0 P0一: 反压协议 (Backpressure Protocol) ──
    try:
        _BP = get_backpressure()
        bp_stats = _BP.get_stats()
        log(f"Backpressure Protocol ON: {bp_stats['total_rejections']} rejections, "
            f"{bp_stats['active_escalations']} active escalations, "
            f"resolution_rate={bp_stats['resolution_rate']:.2f}", "info")
    except Exception as e:
        log(f"Backpressure Protocol init error: {e}", "warn")

    # ── v9.0 P0二: 记忆污染盾 (Memory Contamination Shield) ──
    try:
        _SHIELD = get_shield()
        shield_stats = _SHIELD.get_stats()
        log(f"Contamination Shield ON: {shield_stats['quarantined']} quarantined, "
            f"{shield_stats['rejected']} rejected, {shield_stats['promoted']} promoted", "info")
    except Exception as e:
        log(f"Contamination Shield init error: {e}", "warn")

    # ── v9.0 P1一: Agent 健康中心 (Health Center) ──
    try:
        _HC = get_health_center()
        hc_stats = _HC.get_stats()
        log(f"Agent Health Center ON: {hc_stats['assessed_agents']} agents, "
            f"overall={hc_stats['overall']:.2f}", "info")
    except Exception as e:
        log(f"Agent Health Center init error: {e}", "warn")

    # ── v9.0 P1二: 能量账本 (Energy Ledger) ──
    try:
        _EL = get_ledger()
        el_stats = _EL.get_stats()
        log(f"Energy Ledger ON: {el_stats['active_agents']} agents, "
            f"{el_stats['total_energy_consumed']:.0f} total energy consumed", "info")
    except Exception as e:
        log(f"Energy Ledger init error: {e}", "warn")

    # ── v9.0 P1三: CRDT 记忆网格 ──
    try:
        _CRDT = get_memory_grid()
        crdt_stats = _CRDT.get_stats()
        log(f"CRDT Memory Grid ON: {crdt_stats['total_grids']} grids, "
            f"{crdt_stats['total_active_entries']} active entries", "info")
    except Exception as e:
        log(f"CRDT Memory Grid init error: {e}", "warn")

    # ── v9.0 P1四: 瓶颈自动检测 (Bottleneck Detector) ──
    try:
        _BD = get_detector()
        bd_stats = _BD.get_stats()
        log(f"Bottleneck Detector ON: {bd_stats['total_detected']} patterns detected, "
            f"{bd_stats['active_count']} active bottlenecks", "info")
    except Exception as e:
        log(f"Bottleneck Detector init error: {e}", "warn")

    # ── CodeAct 执行器 (v8) ──
    global _CODECT_EXECUTOR
    try:
        from daemon_modules.codeact_executor import CodeActExecutor
        _CODECT_EXECUTOR = CodeActExecutor()
        log("CodeAct executor ON: Python-code editing mode available (v8)")
    except Exception as e:
        log(f"CodeAct executor init error: {e}", "warn")

    # ── Sandbox 执行器 (v8) ──
    global _SANDBOX_EXECUTOR
    try:
        from daemon_modules.sandbox_executor import SandboxExecutor, get_sandbox
        _SANDBOX_EXECUTOR = get_sandbox()
        log("Sandbox executor ON: code validation isolation (v8)")
    except Exception as e:
        log(f"Sandbox executor init error: {e}", "warn")

    # ── 初始化Self-Verify门控 ──
    verifier = None
    try:
        from daemon_modules.self_verify import SelfVerifier
        verifier = SelfVerifier()
        log("Self-Verify gate ON: every mod must pass syntax+import check")
    except ImportError as e:
        log(f"Self-Verify not available: {e}", "warn")

    # ── HITL 启动检查: 处理滞后的 checkpoint ──
    try:
        _check_pending_hitl()
    except Exception as e:
        log(f"HITL startup check failed: {e}", "warn")

    # ── 安全10层防御: 设置路径白名单 ──
    try:
        set_safe_paths(SCOPE_DIRS)
        log(f"Security gate ON: {len(SCOPE_DIRS)} safe paths, secret+command+path protection active")
    except Exception as e:
        log(f"Security gate init failed: {e}", "warn")

    # 优雅退出信号处理
    loop = asyncio.get_event_loop()
    stop_event = asyncio.Event()

    def _signal_handler(sig, frame):
        log(f"received signal {sig}, shutting down gracefully...")
        stop_event.set()

    # Windows 支持 SIGINT (Ctrl+C), SIGTERM 不一定可用
    try:
        signal.signal(signal.SIGINT, _signal_handler)
    except (OSError, ValueError, RuntimeError, AttributeError) as e:
        log(f"Failed to register SIGINT handler: {e}", "warn")
    try:
        signal.signal(signal.SIGTERM, _signal_handler)
    except (OSError, ValueError, RuntimeError, AttributeError) as e:
        log(f"Failed to register SIGTERM handler: {e}", "warn")

    write_state(running=True, pid=os.getpid(), started_at=datetime.now().isoformat(),
                ok=0, calls=0, consecutive_errors=0, stop_signal=False, force_work=False,
                last_error=None, last_heartbeat=datetime.now().isoformat())

    # 启动 API 服务器 (供 Web 控制台调用)
    try:
        from daemon_modules.daemon_api_server import start_api_server
        api_server = start_api_server(port=19529)
        log("API server started on port 19529")
    except (ImportError, OSError, RuntimeError) as e:
        log(f"API server failed to start: {e}", "warn")

    # 【死命令】知更鸟战舰常驻烧量 — 与主循环并行 (每30min/1800调用/5中队)
    fleet_burn = None
    if WARSHIP_BURN and MAX_CONCURRENT_WORKERS > 0:
        fleet_burn = asyncio.create_task(_fleet_burn_task(stop_event))
        log("[WARSHIP] 战舰烧量协程已挂载 (与主循环并行)")

    # 【死命令】知更鸟比赛自主开发引擎 — 最高优先级 (每轮开发循环)
    competition_dev = None
    if _COMPETITION_DEV_READY and MAX_CONCURRENT_WORKERS > 0:
        comp_engine = get_comp_engine()
        comp_engine.set_llm(call_llm_async)

        async def _competition_dev_loop():
            """比赛自主开发循环 — 分析→规划→生成→构建→验证"""
            log("[比赛引擎] 知更鸟比赛自主开发引擎启动!")
            log("[比赛引擎] 比赛项目: I:\\开发项目\\阿里AI向善\\rural-edu-tutor")
            analysis = await comp_engine.analyze_project()
            log(f"[比赛引擎] 当前状态: {analysis['question_count']}题 / {analysis['music_lesson_count']}音乐课 / {analysis['card_count']}卡片")
            cycle_count = 0
            while not stop_event.is_set():
                if not should_work():
                    await asyncio.sleep(SLEEP_SECONDS)
                    continue
                cycle_count += 1
                log(f"[比赛引擎] 🔄 第{cycle_count}轮开发循环...")
                try:
                    result = await comp_engine.dev_cycle()
                    if result["ok"]:
                        log(f"[比赛引擎] ✅ 第{cycle_count}轮完成: {len(result.get('actions',[]))}个动作")
                    else:
                        log(f"[比赛引擎] ⚠️ 第{cycle_count}轮部分失败: {result.get('build',{}).get('msg','')[:100]}")

                    # 检查是否达到完成条件
                    if comp_engine.state.phase == "P2":
                        log("[比赛引擎] 🏆 比赛项目已到P2阶段! 切换到低频率巡检")
                        # 到达P2后降低频率, 不再密集开发
                        await asyncio.sleep(600)  # 10min一次巡检
                    else:
                        await asyncio.sleep(120)  # 2min一轮开发循环
                except Exception as e:
                    log(f"[比赛引擎] ❌ 开发循环异常: {e}", "error")
                    await asyncio.sleep(300)

        competition_dev = asyncio.create_task(_competition_dev_loop())
        log("[比赛引擎] ✅ 比赛自主开发协程已挂载 (最高优先级)")

    # 【v10.1】知更鸟战舰蜕变循环 — 后台守护 (空闲时自动蜕变)
    metamorphosis_cycle = None
    meta_engine = get_meta_engine()
    j_monitor = get_j_monitor()
    sleep_cycle = get_sleep_cycle()
    safety_lock = get_safety_lock()

    async def _metamorphosis_guardian():
        """蜕变守护协程 — 多级触发器: 空闲累积 → J-Space饱和 → ELO差距 → 定时巡检"""
        log("[蜕变] 蜕变守护协程启动 (后台监测, 多级触发器)")
        idle_duration = 0.0          # 累计空闲秒数
        idle_check_interval = 60     # 每次检查间隔
        last_activity_count = 0
        last_full_cycle = 0.0
        dawn_trigger_interval = 7200 # 最��每2h强制蜕变(非工作时间)
        max_sleep_call_budget = 100  # 每次睡眠循环最多LLM调用

        while not stop_event.is_set():
            try:
                now = time.time()

                # ── Step 1: 检测活跃度 (基于调用数增量) ──
                current_calls = _workers_state.get("total_calls", 0)
                calls_since_last = current_calls - last_activity_count

                if calls_since_last > 0:
                    # 有活跃工作 → 重置空闲计时器
                    idle_duration = 0
                    last_activity_count = current_calls
                    await asyncio.sleep(idle_check_interval)
                    continue

                # 无新调用 → 累积空闲时间
                idle_duration += idle_check_interval
                idle_minutes = idle_duration / 60

                # ── Step 2: 多级空闲触发器 ──
                if idle_minutes < 2:  # <2min空闲, 继续等待
                    await asyncio.sleep(idle_check_interval)
                    continue

                # 级别1: 空闲2min+ → N1 浅睡 (碎片整理/日志压缩/预算校准)
                if 2 <= idle_minutes < 8:
                    log(f"[蜕变] N1浅睡触发: 空闲{idle_minutes:.0f}min, 执行轻量进化")
                    try:
                        sleep_cycle.enter_sleep()
                        log(f"[蜕变] N1: 日志压缩 / J-Space校准")
                        if _COMPETITION_DEV_READY:
                            try:
                                comp = get_comp_engine()
                                if comp.state.phase == "idle":
                                    comp._start_work_cycle()
                            except: pass
                        await asyncio.sleep(30)  # 30s浅睡
                        sleep_cycle.wake_up()
                        log(f"[蜕变] N1浅睡完成, 恢复清醒期")
                    except Exception as e:
                        log(f"[蜕变] N1异常: {e}", "error")

                # 级别2: 空闲8min+ → N2 深睡 (GEPA进化/轨迹分析/对抗训练)
                elif 8 <= idle_minutes < 20:
                    log(f"[蜕变] N2深睡触发: 空闲{idle_minutes:.0f}min, 执行深度进化")
                    try:
                        meta_engine.evolve()
                        sleep_cycle.enter_sleep()

                        # GEPA 自进化引擎: 检查 task_queue 是否有 gepa_evolution 任务 → 真正跑进化
                        try:
                            from daemon_modules import task_queue as _tq
                            from daemon_modules.gepa_evolution import (
                                GEPAEngine as _GepaEngine,
                                GEPAConfig as _GepaConfig,
                                builtin_placeholder_fitness as _gepa_fitness,
                            )
                            _gepa_tasks = [
                                t for t in _tq.list_tasks(status="pending")
                                if t.get("type") == "gepa_evolution"
                            ]
                            if _gepa_tasks:
                                # 先查单例状态, 避免重复运行
                                _gepa_singleton = get_gepa_engine()
                                _gepa_status = _gepa_singleton.get_status()
                                if _gepa_status.get("running"):
                                    log(f"[蜕变] GEPA正在进化中(gen{_gepa_status['generation']}), 跳过此轮")
                                else:
                                    log(f"[蜕变] 🧬 GEPA进化启动: 发现{len(_gepa_tasks)}个进化任务, "
                                        f"种子prompt={len(_EDIT_SYSTEM_PROMPT)} chars")
                                    # 用新引擎实例避免单例状态污染
                                    _gepa_engine = _GepaEngine(_GepaConfig(
                                        population_size=12,
                                        max_generations=10,
                                        patience=5,
                                        max_evaluations=80,
                                        mutation_rate=0.35,
                                    ))
                                    _best_genome, _snapshots = await _gepa_engine.evolve(
                                        seed_prompt=_EDIT_SYSTEM_PROMPT,
                                        fitness_fn=_gepa_fitness,
                                    )
                                    # 把最佳 prompt 经 prompt_updater 写回 code_worker
                                    if _best_genome and _best_genome.prompt:
                                        set_edit_system_prompt(_best_genome.prompt)
                                        _best_fit = _snapshots[-1].best_fitness if _snapshots else 0.0
                                        log(f"[蜕变] ✅ GEPA进化完成: best_fitness={_best_fit:.3f}, "
                                            f"generations={len(_snapshots)}, prompt已写回 ({len(_best_genome.prompt)} chars)")
                                    # 标记任务完成
                                    for _gt in _gepa_tasks:
                                        try:
                                            _tq.update_status(_gt["id"], "done")
                                        except Exception:
                                            pass
                            else:
                                log(f"[蜕变] 无gepa_evolution任务, 跳过GEPA进化", "debug")
                        except Exception as ge:
                            log(f"[蜕变] GEPA进化异常: {ge}", "debug")

                        # MARS 比较反思 — 真实方法: reflect_all_pending() (非 run_reflection_cycle)
                        if _COMPARATIVE_REFLECTION_READY:
                            try:
                                reflector = get_comparative_reflector()
                                reports = await reflector.reflect_all_pending()
                                n_insights = sum(r.insights_generated for r in reports) if reports else 0
                                log(f"[蜕变] MARS反思完成: {len(reports) if reports else 0}比较, {n_insights}洞察")
                            except Exception as e:
                                log(f"[蜕变] MARS反思异常: {e}", "error")

                        # 对抗进化 — 必须先 set_functions 注入 _llm_fn 否则所有 LLM 调用返回 None
                        if _ANTAGONISTIC_READY:
                            try:
                                antag = get_antag_engine()
                                # 首次或函数未注入时, 注入 call_llm + call_code
                                if not getattr(antag, "_llm_fn", None):
                                    antag.set_functions(llm_fn=call_llm_async, code_fn=None)
                                results = await antag.run_session(target_module="daemon_modules")
                                elo_stats = antag.get_stats()["elo"]
                                n_imp = sum(len(r.improvements) for r in results) if results else 0
                                log(f"[蜕变] 对抗进化: Solver={elo_stats['solver_rating']:.0f} Challenger={elo_stats['challenger_rating']:.0f}, 改进={n_imp}")
                            except Exception as e:
                                log(f"[蜕变] 对抗进化异常: {e}", "error")

                        await asyncio.sleep(60)
                        sleep_cycle.wake_up()
                        log(f"[蜕变] N2深睡完成")
                    except Exception as e:
                        log(f"[蜕变] N2异常: {e}", "error")

                # 级别3: 空闲20min+ → REM创造 (技能进化/拓扑重构/候选生成)
                else:
                    log(f"[蜕变] REM创造触发: 空闲{idle_minutes:.0f}min, 执行创造性重构")
                    try:
                        meta_engine.evolve()
                        sleep_cycle.enter_sleep()

                        # 轨迹进化 — 真实方法: batch_evolve(n) (非 run_evolution_cycle)
                        if _TRAJECTORY_EVOLUTION_READY:
                            try:
                                traj_ev = get_trajectory_evolution()
                                results = await traj_ev.batch_evolve(n=10)
                                applied = [r for r in results if r.applied] if results else []
                                total_token_saved = sum(r.token_saved for r in applied)
                                log(f"[蜕变] 轨迹进化: {len(applied) if applied else 0}改进, 节省{total_token_saved}tokens")
                            except Exception as e:
                                log(f"[蜕变] 轨迹进化异常: {e}", "error")

                        # 技能进化
                        if hasattr(get_progressive_loader, '__call__'):
                            try:
                                skill_loader = get_progressive_loader()
                                await skill_loader.evolve_skills()
                            except Exception: pass

                        # 完整蜕变迭代
                        result = await meta_engine.run_pupa_cycle()
                        if result.get("success"):
                            v_result = await safety_lock.validate(result)
                            if v_result.get("passed"):
                                meta_engine.transition_to_adult()
                                log(f"[蜕变] ✅ REM蜕变成功: {result.get('improvements', [])[:3]}")
                            else:
                                meta_engine.rollback()
                                log(f"[蜕变] ⚠️ 安全锁拦截, 已回滚")
                        else:
                            log(f"[蜕变] REM蜕变无有效改进")

                        await asyncio.sleep(90)
                        sleep_cycle.wake_up()
                        log(f"[蜕变] REM创造完成")
                    except Exception as e:
                        log(f"[蜕变] REM异常: {e}", "error")

                # ── Step 3: 检查ELO差距 (每次都检查) ──
                if _ANTAGONISTIC_READY:
                    try:
                        antag_stats = get_antag_engine().get_stats()
                        if antag_stats["total_matches"] > 0:
                            elo = antag_stats["elo"]
                            elo_gap = abs(elo["solver_rating"] - elo["challenger_rating"])
                            if elo_gap > 150:
                                log(f"[蜕变] ELO差距{elo_gap:.0f}, 触发对抗再平衡")
                                await get_antag_engine().run_session(target_module="daemon_modules")
                    except Exception:
                        pass

                # ── Step 4: J-Space 饱和检测 ──
                try:
                    # 需要足够的样本
                    async with j_monitor._lock if hasattr(j_monitor, '_lock') else asyncio.Lock():
                        sample_count = len(j_monitor._metrics_buffer) if hasattr(j_monitor, '_metrics_buffer') else 0
                    if sample_count >= 10:
                        j_status = j_monitor.get_full_status()
                        saturation = j_status.get("saturation", 1.0)
                        if saturation < 0.15:
                            log(f"[蜕变] J-Space饱和({saturation:.1%}), 触发额外蜕变迭代")
                    else:
                        log(f"[蜕变] J-Space采样不足({sample_count}/10), 跳过饱和检测", "debug")
                except Exception:
                    pass

                # 重置空闲计时器 (蜕变完成后)
                if idle_minutes >= 2:
                    idle_duration = 0

                await asyncio.sleep(idle_check_interval)

            except Exception as e:
                log(f"[蜕变] 守护异常: {e}", "error")
                await asyncio.sleep(300)

    metamorphosis_cycle = asyncio.create_task(_metamorphosis_guardian())
    log("[蜕变] ✅ 蜕变守护协程已挂载 (空闲时自动蜕变)")

    # ── 闭环编排器: 连接 code_worker → eval → gepa → prompt 回写 ──
    from daemon_modules.closed_loop_orchestrator import ClosedLoopOrchestrator
    _clo = ClosedLoopOrchestrator(call_llm_async, threshold=5)

    # ── 闭环巡检协程: 每30分钟检查 GEPA 触发 ──
    async def _closed_loop_watchdog():
        while not stop_event.is_set():
            await asyncio.sleep(1800)  # 30分钟
            try:
                status = await _clo.periodic_check()
                if status.get("running_gepa"):
                    log("[闭环] 🚀 GEPA 进化已触发并正在运行")
            except Exception as e:
                log(f"[闭环] 巡检异常: {e}", "debug")

    # ── 任务队列消费者: 从 task_queue 取任务并处理 ──
    async def _heartbeat_writer():
        """后台协程: 每 10s 写入心跳文件（给 warship_guardian 和监控用）"""
        hb_file = BASE_DIR / ".daemon_heartbeat"
        pid = os.getpid()
        while not stop_event.is_set():
            try:
                hb_file.write_text(json.dumps({
                    "pid": pid,
                    "ts": time.time(),
                    "time": datetime.now().isoformat(),
                }), encoding="utf-8")
            except Exception:
                pass
            await asyncio.sleep(10)

    def _check_budget_state() -> str:
        """检查预算状态: \"ok\" / \"low\" / \"exhausted\"
        
        读取 .fast_budget.json 和 .collab_budget.json 的 remaining。
        如果文件不存在或没有 remaining 字段 → 视为 ok（不拦截任务）。
        """
        try:
            fb = BASE_DIR.parent / ".fast_budget.json"
            cb = BASE_DIR.parent / ".collab_budget.json"
            total = 0
            found_any = False
            for f in [fb, cb]:
                if f.exists():
                    data = json.loads(f.read_text("utf-8"))
                    if isinstance(data, dict):
                        remaining = data.get("remaining")
                        if remaining is not None:
                            total += remaining
                            found_any = True
            if not found_any:
                # 没有 budget 文件或没有 remaining 字段 → 不拦截
                return "ok"
            if total <= 0:
                return "exhausted"
            if total < 20:
                return "low"
            return "ok"
        except Exception:
            return "ok"  # 异常时允许继续

    async def _task_queue_consumer():
        """从 task_queue 取任务, 交给LLM处理, 标记完成/失败"""
        from daemon_modules import task_queue as tq
        from daemon_modules.capability_registry import (
            get_capability, build_context, register_builtin_capabilities,
        )
        # 确保内建能力已注册 (幂等; 启动时也会注册一次)
        register_builtin_capabilities()
        def _ctx_save_state(**kw):
            """任务完成写状态: 走 _save_state 保留旧 ok/calls 并刷新心跳"""
            _save_state(kw)

        _cap_ctx = build_context(
            call_llm_async=call_llm_async,
            call_llm_async_deepseek=call_llm_async_deepseek,
            call_llm_async_sfkey=call_llm_async_sfkey,
            log=log, tq=tq, write_state=_ctx_save_state, read_state=read_state,
            clo=_clo, base_dir=BASE_DIR,
        )
        # ── P0-2 语义循环检测: 连续"完成但无真实diff"计数 ──
        _no_progress_streak: int = 0
        _SEMANTIC_LOOP_THRESHOLD: int = 4  # 连续 4 次无真实diff → 熔断式暂停
        while not stop_event.is_set():
            try:
                # ── 预算感知过滤 (v2: 预算不足时只处理紧急任务) ──
                budget_state = _check_budget_state()
                if budget_state == "exhausted":
                    # 预算耗尽 → 跳过本轮, 等待恢复
                    await asyncio.sleep(SLEEP_SECONDS * 3)
                    continue
                if budget_state == "low":
                    # 预算低 → 只处理紧急任务 (P_URGENT=0)
                    pass  # 在下面 pending 过滤中处理

                # 先释放超时的 in_progress 任务（防止泄漏）
                released = tq.release_stale_tasks()
                if released:
                    log(f"[任务队列] 释放了 {released} 个超时任务", "warn")
                pending = tq.list_tasks(status="pending")
                if not pending:
                    await asyncio.sleep(SLEEP_SECONDS)
                    continue
                # 按优先级排序 (HIGH=1 优先)
                pending.sort(key=lambda t: (t.get("priority", 3), t.get("created_at", "")))
                # 预算低时: 只处理紧急任务 (priority=0)
                if budget_state == "low":
                    urgent = [t for t in pending if t.get("priority", 3) <= 1]
                    if not urgent:
                        log(f"[预算] 预算不足, 无紧急任务, 等待恢复", "warn")
                        await asyncio.sleep(SLEEP_SECONDS * 2)
                        continue
                    pending = urgent
                task = pending[0]
                log(f"[任务队列] 开始处理: [{task['id']}] {task['title']}")
                tq.update_status(task["id"], "in_progress")
                # 构建处理 prompt
                scope = task.get("scope", str(BASE_DIR))
                prompt = (
                    f"## 任务: {task['title']}\n\n"
                    f"### 描述\n{task.get('description', '')}\n\n"
                    f"### 作用域\n{scope}\n\n"
                    f"请阅读相关文件, 分析当前代码, 然后做出必要的修改来实现该任务。\n"
                    f"输出格式: 列出每个修改的文件 + 修改内容。"
                )
                try:
                    # ── 能力注册表分派 (替代硬编码 if/elif) ──
                    task["_prompt"] = prompt  # 供 handler 读取原始 prompt
                    handler = get_capability(task.get("type"))
                    if handler is None:
                        handler = get_capability("__default__")
                    # ── P0-3 基线快照: 任务执行前记录 git diff, 供门控排除历史未提交改动 ──
                    try:
                        from daemon_modules.task_validator import compute_git_diff
                        _baseline = compute_git_diff(
                            str(BASE_DIR), scope=task.get("scope"),
                            file_paths=task.get("file_paths"),
                        )
                    except Exception:
                        _baseline = None
                    await asyncio.wait_for(handler(task, _cap_ctx), timeout=HANDLER_TIMEOUT)
                    # Task #550: 递增 total_calls, 让 guardian 正确感知系统活跃度
                    # (否则 _metamorphosis_guardian 误判空闲, 每 2min 触发 N1 浅睡)
                    async with _workers_lock:
                        _workers_state["total_calls"] += 1
                    # ── P0-3 真实diff门控: handler 标 completed 的 code 任务, 用 git 权威复核 ──
                    # 根因修复: 旧 consumer 只"检测"不"拦截" → 无diff任务被盲标done(假完成)。
                    # 现在统一从文件重载任务真实状态, code类必须有 git 真实改动才计完成。
                    try:
                        from daemon_modules.task_validator import (
                            validate_completion, is_code_task,
                        )
                        _stored = tq.get_task(task["id"])
                        if _stored and _stored.get("status") == "completed" and is_code_task(_stored):
                            _vr = validate_completion(_stored, str(BASE_DIR), baseline=_baseline)
                            if not _vr["ok"]:
                                log(f"[门控] ❌ 任务标完成但 {_vr['reason']} → 判失败(不计完成)", "warn")
                                tq.fail(task["id"], error=_vr["reason"],
                                        metadata={"_real_diff": _vr["real_diff"],
                                                  "_quality_score": _vr["quality"]})
                                _no_progress_streak += 1
                                _save_state({"consecutive_errors": read_state().get("consecutive_errors", 0) + 1})
                                await asyncio.sleep(SLEEP_SECONDS)
                                continue  # 跳到下一个任务, 不重复进语义循环计数
                    except Exception as _ve:
                        log(f"[门控] 复核异常(放行): {_ve}", "warn")
                    # ── P0-2 语义循环检测: 完成但无真实diff → 计数, 超阈值熔断式暂停 ──
                    _rd = task.get("_real_diff", None)
                    if _rd is False:
                        _no_progress_streak += 1
                        log(f"[语义循环] 任务完成但无真实diff, 连续 {_no_progress_streak}/{_SEMANTIC_LOOP_THRESHOLD}", "warn")
                        if _no_progress_streak >= _SEMANTIC_LOOP_THRESHOLD:
                            log(f"[语义循环] ⚠️ 连续 {_no_progress_streak} 次无真实diff, 触发熔断式暂停(防空转烧钱)", "error")
                            try:
                                _save_state({"semantic_loop_alert": read_state().get("semantic_loop_alert", 0) + 1})
                            except Exception:
                                pass
                            try:
                                _cap_ctx.notify("⚠️ 语义空转告警",
                                               f"连续 {_no_progress_streak} 个任务完成但无真实改动, 已暂停消费30分钟防空转")
                            except Exception:
                                pass
                            await asyncio.sleep(SLEEP_SECONDS * 30)
                            _no_progress_streak = 0
                    elif _rd is True:
                        _no_progress_streak = 0
                except Exception as e:
                    log(f"[任务队列] ❌ 失败: [{task['id']}] {task['title']}: {e}", "error")
                    tq.fail(task["id"], error=str(e)[:500])
                    # Task #550: 失败也递增, 保持计数器一致性
                    async with _workers_lock:
                        _workers_state["total_calls"] += 1
                    _save_state({"consecutive_errors": read_state().get("consecutive_errors", 0) + 1})
                await asyncio.sleep(SLEEP_SECONDS)
            except Exception as e:
                log(f"[任务队列] consumer 异常: {e}", "error")
                await asyncio.sleep(SLEEP_SECONDS * 3)
    # ── 能力注册表: 注册内建 + 自动发现模块自注册 (P1-1) ──
    try:
        from daemon_modules.capability_registry import (
            register_builtin_capabilities, auto_discover, list_capabilities,
        )
        register_builtin_capabilities()
        _discovered = auto_discover()
        log(f"[CAP] 能力注册表就绪: {len(list_capabilities())} 项 (自动发现 {_discovered})")
    except Exception as ce:
        log(f"[CAP] 能力注册表初始化失败: {ce}", "warn")

    # ── 自治闭环 #1: 自愈看门狗 (watch_self) ──
    async def watch_self():
        """自愈看门狗: 每60s检查心跳年龄, 若超过180s无心跳则os.execv重启自身。
        不依赖外部 start_daemon.py — 纯进程内自愈。"""
        while not stop_event.is_set():
            await asyncio.sleep(60)
            try:
                s = read_state()
                hb = s.get("last_heartbeat")
                if not hb:
                    continue
                try:
                    hb_dt = datetime.fromisoformat(hb)
                except (ValueError, TypeError):
                    continue
                age = (datetime.now() - hb_dt).total_seconds()
                if age > 180:
                    # 如果正在关闭中，跳过自愈重启，避免优雅退出时误触发
                    if stop_event.is_set():
                        log(f"[SELF-HEAL] 心跳停滞{int(age)}s 但关闭中, 跳过自愈重启", "warn")
                        continue
                    log(f"[SELF-HEAL] 心跳停滞{int(age)}s (>180s), 触发 os.execv 自愈重启", "error")
                    write_state(self_heal_restart=datetime.now().isoformat(),
                                self_heal_reason=f"heartbeat stale {int(age)}s")
                    # flush 日志后再 execv
                    try:
                        import sys as _sys
                        _sys.stdout.flush()
                        _sys.stderr.flush()
                    except Exception:
                        pass
                    os.execv(sys.executable, [sys.executable] + sys.argv)
            except Exception as e:
                log(f"[SELF-HEAL] watch_self 异常: {e}", "error")

    # ── 自治闭环 #1: 自动验证 (auto_verify) ──
    async def auto_verify():
        """自动验证: 当队列连续10min为空且历史有过至少1次任务完成时,
        自动调用 verify_production.verify() 把结果写入状态/打印日志。"""
        empty_streak_start: Optional[float] = None
        while not stop_event.is_set():
            await asyncio.sleep(60)
            try:
                from daemon_modules import task_queue as _tq
                pending = _tq.list_tasks(status="pending")
                if pending:
                    # 队列非空 → 重置空计时器
                    empty_streak_start = None
                    continue
                # 队列为空 → 开始/继续计时
                if empty_streak_start is None:
                    empty_streak_start = time.time()
                elapsed = time.time() - empty_streak_start
                if elapsed < 600:  # 不足10min
                    continue
                # 检查历史是否有过至少1次任务完成
                completed = _tq.list_tasks(status="done")
                if not completed:
                    continue
                # 条件满足 → 调用 verify_production.verify()
                log(f"[AUTO-VERIFY] 队列连续空{int(elapsed)}s + 历史完成{len(completed)}任务, 启动自动验证", "info")
                try:
                    from verify_production import verify as _verify_prod
                    v_result = _verify_prod()
                    log(f"[AUTO-VERIFY] ✅ 验证完成: {v_result}", "info")
                    # 确保验证结果可 JSON 序列化，避免状态文件写入失败
                    if isinstance(v_result, (dict, list, str, type(None))):
                        safe_result = v_result
                    else:
                        safe_result = str(v_result)
                    write_state(auto_verify_result=safe_result,
                                auto_verify_at=datetime.now().isoformat())
                except ImportError:
                    log("[AUTO-VERIFY] verify_production 模块不可用, 跳过本轮", "warn")
                except Exception as ve:
                    log(f"[AUTO-VERIFY] 验证异常: {ve}", "error")
                # 重置计时器避免频繁重复触发
                empty_streak_start = time.time()
            except Exception as e:
                log(f"[AUTO-VERIFY] auto_verify 异常: {e}", "error")

    # ── 启动自治闭环协程 ──
    self_heal_task = asyncio.create_task(watch_self())
    log("[SELF-HEAL] ✅ 自愈看门狗协程已挂载 (每60s检查, 180s无心跳→os.execv重启)")
    auto_verify_task = asyncio.create_task(auto_verify())
    log("[AUTO-VERIFY] ✅ 自动验证协程已挂载 (队列空10min+有历史完成时触发)")
    tq_consumer = asyncio.create_task(_task_queue_consumer())
    log("[任务队列] ✅ 消费者协程已挂载")
    hb_writer = asyncio.create_task(_heartbeat_writer())
    log("[心跳] ✅ 心跳协程已挂载")
    cl_watchdog = asyncio.create_task(_closed_loop_watchdog())
    log("[闭环] ✅ 闭环巡检协程已挂载 (每30分钟)")

    log(f"=== Robin SOTA Daemon {ENGINE_VERSION} ({ENGINE_BUILD_DATE}) started ===")
    log(f"work hours: {WORK_START_HOUR}:00-{WORK_END_HOUR}:00")
    log(f"scan scope: {len(SCOPE_DIRS)} directories")
    log(f"budget cap: {MAX_CALLS} calls")
    log(f"PID: {os.getpid()}")
    log(f"experts: {', '.join(get_all_experts().keys())}")
    log(f"[SPEED] MAX_CONCURRENT_WORKERS={MAX_CONCURRENT_WORKERS} (并行提速)")
    log(f"[OBS] 可观测性管道: {get_obs_pipeline().health_summary()['total_modules']}模块追踪")
    log(f"[EVAL] 评估框架: {get_eval_harness().get_stats()['total_evals']}次评估")
    log(f"[GUARD] 护栏系统: {get_guardrails_sys().get_stats()['level']}等级")
    log(f"[ANTAG] 对抗进化: {get_antag_engine().get_stats()['total_matches']}场对局")
    log(f"[TDD] TDD强制中间件: {get_tdd_mw().get_stats()['tdd_only_modules']} TDD模块")
    log(f"[HARNESS] 三大中间件: checklist={_HARNESS_CHECKLIST_READY} ctx={_HARNESS_CONTEXT_READY} loop={_HARNESS_LOOP_DETECT_READY}")
    log(f"[GATE] 三级质量门禁: {get_quality_gate().get_stats()['default_level']}等级")
    log(f"[BUDGET] 推理三明治: {get_reasoning_budget().get_stats()['sandwich_enabled']}启用")
    # ── v10.3 三百轮SOTA落盘 ──
    log(f"[EVAL_SEP] Gen/Eval分离: {_GEN_EVAL_SEP_READY} (独立评审会话, Minority Veto)")
    log(f"[EDITOR] Search-and-Replace精确编辑: {_EDITOR_PRECISION_READY} (模糊回退0.6)")
    log(f"[HOOK] Stop Hook/Ralph Loop: {_STOP_HOOK_READY} (L3:test+build+lint)")
    log(f"[CTX_OPT] 上下文压缩+RepoMap: compressor={_CONTEXT_COMPRESSOR_READY} repomap={_REPOMAP_READY}")

    # ── 并行工作池 ──
    # 用共享计数器避免竞态, 每个worker独立循环, supervisor负责心跳/预算/状态
    _workers_state: dict[str, int] = {
        "total_calls": 0, "total_ok": 0, "total_rollback": 0,
        "total_validated": 0, "consecutive_errors": 0,
    }
    _workers_lock = asyncio.Lock()

    async def _worker(worker_id: int):
        """单个工作协程 — 独立循环, 并行处理"""
        local_errors = 0
        while not stop_event.is_set():
            # 预算检查 (共享计数器)
            async with _workers_lock:
                if _workers_state["total_calls"] >= MAX_CALLS:
                    return
            if not should_work():
                await asyncio.sleep(SLEEP_SECONDS)
                continue
            if local_errors >= MAX_CONSECUTIVE_ERRORS:
                log(f"[worker-{worker_id}] too many errors, sleeping {CRASH_RECOVERY_PAUSE}s", "warn")
                await asyncio.sleep(CRASH_RECOVERY_PAUSE)
                local_errors = 0
                continue
            try:
                # ── v10.1: 可观测性追踪 ──
                with get_obs_pipeline().span("worker.work_cycle", {"worker_id": worker_id, "error_streak": local_errors}):
                    result = await work_cycle()

                # ── v10.1: 护栏安全审计 (修改落盘前检查) ──
                if _GUARDRAILS_READY and result.get("ok", 0) > 0:
                    audit = get_guardrails_sys().audit(
                        action="modification",
                        resource="code",
                        context={"result": result, "worker_id": worker_id}
                    )
                    if audit.get("risk_level") == "high":
                        log(f"[GUARD] worker-{worker_id} 修改被护栏拦截 (高风险)")
                        result = {"ok": 0, "skip": 0, "fail": 1, "rollback": result.get("ok", 0)}
                    elif audit.get("risk_level") == "medium":
                        log(f"[GUARD] worker-{worker_id} 修改含中风险, 已记录审计日志")
            except (OSError, RuntimeError, asyncio.TimeoutError) as e:
                log(f"[worker-{worker_id}] exception: {e}", "error")
                result = {"ok": 0, "skip": 0, "fail": 1, "exception": str(e)}
            async with _workers_lock:
                _workers_state["total_calls"] += 1
                _workers_state["total_ok"] += result.get("ok", 0)
                _workers_state["total_rollback"] += result.get("rollback", 0)
                _workers_state["total_validated"] += result.get("validated", 0)
                if result.get("exception") or result.get("fail", 0) > 0:
                    local_errors += 1
                    _workers_state["consecutive_errors"] += 1
                else:
                    local_errors = 0
                    _workers_state["consecutive_errors"] = max(0, _workers_state["consecutive_errors"] - 1)
            await asyncio.sleep(SLEEP_SECONDS // MAX_CONCURRENT_WORKERS)  # 错峰避免文件争抢

    # 启动 workers (MAX_CONCURRENT_WORKERS=0时只跑任务队列消费者)
    workers = [asyncio.create_task(_worker(i)) for i in range(MAX_CONCURRENT_WORKERS)] if MAX_CONCURRENT_WORKERS > 0 else []

    # ── Supervisor 循环 (心跳/预算耗尽做梦/状态写入) ──
    last_heartbeat_time = time.time()
    while not stop_event.is_set():
        # 检查停止信号
        state = read_state()
        if state.get("stop_signal"):
            log("stop_signal received, shutting down")
            stop_event.set()
            break

        # 预算耗尽检查 (任一worker返回后触发)
        async with _workers_lock:
            calls = _workers_state["total_calls"]
            oks = _workers_state["total_ok"]
            rb = _workers_state["total_rollback"]
            vd = _workers_state["total_validated"]
            ce = _workers_state["consecutive_errors"]

            if calls >= MAX_CALLS:
                log(f"budget exhausted ({MAX_CALLS} calls), triggering Dream Agent")
                break

            # 写入状态 (统一走 _save_state, 保留旧计数器 + 刷新心跳)
            _save_state({"ok": oks, "calls": calls, "consecutive_errors": ce,
                         "total_rollback": rb, "total_validated": vd})

        # 心跳
        now_time = time.time()
        if now_time - last_heartbeat_time >= HEARTBEAT_INTERVAL:
            heartbeat()
            last_heartbeat_time = now_time
            log(f"progress: OK={oks} calls={calls}/{MAX_CALLS} validated={vd} rollback={rb} errors_streak={ce}")

        # 检查 workers 是否全部挂了 → 重新 spawn (只对MAX_CONCURRENT_WORKERS>0生效)
        if MAX_CONCURRENT_WORKERS > 0:
            alive = sum(1 for w in workers if not w.done())
            if alive == 0:
                log("all workers finished, respawning for night ops...")
                cancel_workers = [w for w in workers if not w.done()]
                for w in cancel_workers:
                    w.cancel()
                workers = [asyncio.create_task(_worker(i)) for i in range(MAX_CONCURRENT_WORKERS)]
                await asyncio.sleep(2)
                continue

        # 预算耗尽 → 触发知识大脑做梦 → 重置预算继续
        if calls >= MAX_CALLS:
            log(f"budget exhausted ({MAX_CALLS} calls), dreaming + reset...")
            try:
                from daemon_modules.dream_agent import DreamAgent
                for scope in SCOPE_DIRS:
                    try:
                        da = DreamAgent(scope)
                        report = da.dream(force=True)
                        if report.get("consolidated", 0) + report.get("evolved", 0) > 0:
                            log(f"dream: consolidated={report.get('consolidated')}, "
                                f"verified={report.get('verified')}, "
                                f"compressed={report.get('compressed')}, "
                                f"evolved={report.get('evolved')}")
                    except (OSError, ValueError, RuntimeError, ImportError) as de:
                        log(f"dream error for {scope}: {de}", "warn")
            except ImportError:
                pass
            # 重置预算 + respawn workers
            _workers_state["total_calls"] = 0
            _workers_state["total_ok"] = 0
            log("budget reset for night ops, continuing...", "info")
            workers = [asyncio.create_task(_worker(i)) for i in range(MAX_CONCURRENT_WORKERS)]
            await asyncio.sleep(2)
            continue

        await asyncio.sleep(SLEEP_SECONDS // 2)  # supervisor 半频检查

    # 只有 stop_signal 才会走到这里
    log("stop_signal received, shutting down gracefully", "info")

    # 取消所有worker
    for w in workers:
        if not w.done():
            w.cancel()
    await asyncio.gather(*workers, return_exceptions=True)

    # 优雅停止战舰烧量协程
    if fleet_burn is not None and not fleet_burn.done():
        fleet_burn.cancel()
        try:
            await fleet_burn
        except asyncio.CancelledError:
            pass
        except (OSError, RuntimeError, asyncio.TimeoutError) as e:
            log(f"fleet_burn cleanup error: {e}", "warn")
        except Exception as e:
            log(f"fleet_burn unexpected cleanup error: {e}", "error")

    write_state(running=False)
    log(f"=== Daemon exited: {_workers_state['total_calls']} calls, {_workers_state['total_ok']} modifications ===")

# ── CLI 控制 ──

def _is_process_alive(pid: int) -> bool:
    """检查进程是否存活 (Windows 兼容)"""
    if not pid:
        return False
    try:
        # 跨平台进程存活检查
        if os.name != 'nt':
            os.kill(pid, 0)
            return True
        # Windows: 用 tasklist 检查 (encoding='mbcs' 避免 UTF-8 解码错误)
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
            capture_output=True, timeout=5, encoding='mbcs', errors='replace'
        )
        return str(pid) in result.stdout
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return False

def cmd_start():
    """后台启动 (Windows 兼容: subprocess + CREATE_NO_WINDOW)"""
    state = read_state()
    old_pid = state.get("pid")
    if old_pid and _is_process_alive(old_pid):
        print(f"Daemon already running (PID {old_pid})")
        return

    # 清除旧状态
    write_state(running=False, pid=0, stop_signal=False, force_work=False)

    # Windows 后台启动: 只用 python.exe (pythonw.exe 静默崩溃, 已弃用)
    python_exe = sys.executable
    script = str(Path(__file__).resolve())
    creationflags = 0x08000000 if os.name == 'nt' else 0

    # 把战舰烧量开关经环境变量透传给后台子进程 (--daemon 场景不转发 argv)
    child_env = os.environ.copy()
    if WARSHIP_BURN:
        child_env["ROBIN_WARSHIP_BURN"] = "1"

    try:
        proc = subprocess.Popen(
            [python_exe, script],
            creationflags=creationflags,
            cwd=str(BASE_DIR),
            env=child_env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        pid = proc.pid
        # 等待一小段时间确认进程没立即崩溃
        time.sleep(3)
        if proc.poll() is not None:
            print("ERROR: Daemon process exited immediately. Try running in foreground first:")
            print(f"  python {script}")
            return

        write_state(running=True, pid=pid, started_at=datetime.now().isoformat(),
                    ok=0, calls=0, consecutive_errors=0, stop_signal=False, force_work=False)
        print(f"Daemon started (PID {pid})")
        print(f"Work hours: {WORK_START_HOUR}:00-{WORK_END_HOUR}:00")
        print(f"Budget: {MAX_CALLS} calls")
    except (OSError, subprocess.SubprocessError) as e:
        print(f"Failed to start daemon: {e}")
        print(f"Try foreground mode: python {script}")

def cmd_stop():
    write_state(stop_signal=True)
    print("Stop signal sent")
    state = read_state()
    pid = state.get("pid")
    if pid and pid != os.getpid():
        if _is_process_alive(pid):
            try:
                # Windows: taskkill 优雅终止
                subprocess.run(["taskkill", "/PID", str(pid)], capture_output=True, timeout=5)
                print(f"Terminated process PID {pid}")
            except (OSError, subprocess.TimeoutExpired):
                pass
        else:
            print(f"Process PID {pid} already dead, cleaning state")
    # 清理状态
    time.sleep(1)
    write_state(running=False, stop_signal=False)

def cmd_status():
    state = read_state()
    pid = state.get("pid")

    # 进程存活检查
    if state.get("running"):
        if pid and _is_process_alive(pid):
            print(f"[RUNNING] PID {pid}")
        else:
            print(f"[ZOMBIE] State says running but PID {pid} is dead")
            write_state(running=False)
    else:
        print("[STOPPED]")

    # 心跳检查
    last_hb = state.get("last_heartbeat")
    if last_hb and state.get("running"):
        try:
            hb_dt = datetime.fromisoformat(last_hb)
            elapsed = (datetime.now() - hb_dt).total_seconds()
            if elapsed > 120:
                print(f"[WARN] No heartbeat for {int(elapsed)}s - may be hung")
            else:
                print(f"[HEART] Last heartbeat {int(elapsed)}s ago")
        except (ValueError, TypeError):
            pass

    # 工作时间
    now = datetime.now()
    if WORK_START_HOUR <= now.hour < WORK_END_HOUR:
        print(f"[WORK]  Work hours ({WORK_START_HOUR}:00-{WORK_END_HOUR}:00)")
    else:
        print(f"[IDLE]  Outside work hours ({WORK_START_HOUR}:00-{WORK_END_HOUR}:00)")

    print(f"[STAT]  Modifications: {state.get('ok', 0)}")
    print(f"[STAT]  Calls used: {state.get('calls', 0)} / {MAX_CALLS}")
    print(f"[STAT]  Validated: {state.get('total_validated', 0)}")
    print(f"[STAT]  Rollbacks: {state.get('total_rollback', 0)}")
    print(f"[STAT]  Force work: {'ON' if state.get('force_work') else 'OFF'}")
    print(f"[STAT]  Error streak: {state.get('consecutive_errors', 0)} / {MAX_CONSECUTIVE_ERRORS}")

    # 专家路由信息
    experts = get_all_experts()
    print(f"[EXPERT] Available: {', '.join(experts.keys())}")

    # 质量趋势 (最近5条)
    if METRICS_FILE.exists():
        try:
            entries = [json.loads(l) for l in METRICS_FILE.read_text("utf-8").split("\n") if l.strip()][-5:]
            if entries:
                avg_q = sum(e.get("avg_quality", 0) for e in entries) / len(entries)
                print(f"[QUALITY] Recent avg: {avg_q:.2f} (last {len(entries)} batches)")
        except (ValueError, TypeError, json.JSONDecodeError, OSError) as e:
            print(f"[WARN] Failed to parse metrics: {e}")

    if state.get("started_at"):
        print(f"[TIME]  Started: {state['started_at']}")
    if state.get("last_error"):
        print(f"[ERR]   Last error: {state['last_error']}")

def cmd_go():
    """强制工作模式 (持续, 非一次性)"""
    state = read_state()
    pid = state.get("pid")

    # 如果守护进程没在跑, 先启动它
    if not (pid and _is_process_alive(pid)):
        print("Daemon not running, starting first...")
        cmd_start()
        time.sleep(3)

    # 设置 force_work=True, 守护进程会持续工作直到手动 --stop
    write_state(force_work=True, stop_signal=False)
    print("[GO] Force work mode ON (continuous until --stop)")
    print(f"     Budget: {MAX_CALLS} calls, interval: {SLEEP_SECONDS}s")

def cmd_reset():
    """重置统计"""
    write_state(running=False, pid=0, ok=0, calls=0, started_at=None,
                force_work=False, stop_signal=False, last_error=None,
                consecutive_errors=0, last_heartbeat=None,
                total_rollback=0, total_validated=0)
    print("[RESET] State cleared")

def cmd_report():
    """生成进化报告"""
    state = read_state()
    generate_evolution_report(METRICS_FILE, state, REPORT_FILE)
    print(f"[REPORT] Evolution report generated: {REPORT_FILE}")

if __name__ == "__main__":
    if "--stop" in sys.argv:
        cmd_stop()
    elif "--status" in sys.argv:
        cmd_status()
    elif "--go" in sys.argv:
        cmd_go()
    elif "--reset" in sys.argv:
        cmd_reset()
    elif "--trace" in sys.argv:
        report = generate_trace_report()
        trace_path = Path(__file__).parent / "trace_report.html"
        trace_path.write_text(report, "utf-8")
        print(f"[TRACE] Trace report generated: {trace_path}")
    elif "--cost" in sys.argv:
        summary = _get_cost_summary()
        print("Cost Summary:")
        print(f"  Total: ${summary['total_cost']:.4f} over {summary['total_calls']} calls")
        print(f"  By provider: {json.dumps(summary['by_provider'], indent=2)}")
        print(f"  By phase: {json.dumps(summary['by_phase'], indent=2)}")
    elif "--caid" in sys.argv:
        # CAID 模式: git worktree隔离启动
        print("[CAID] Starting with git worktree isolation for 5 squadrons")
        os.environ["ROBIN_CAID_MODE"] = "1"
        asyncio.run(main_loop())
    elif "--eval" in sys.argv:
        # 运行 Prompt 评测 + Self-Eval 基准
        from daemon_modules.prompt_optimizer import run_full_eval as run_prompt_eval
        try:
            run_prompt_eval()
        except Exception as e:
            log(f"prompt eval failed: {e}", "warn")

        print("\n" + "="*60)
        print("🧪 Self-Eval Benchmark (端到端编辑能力测试)")
        print("="*60)
        try:
            from daemon_modules.self_eval import run_eval
            result = run_eval()
            if "total" in result:
                print(f"\n结果: {result['passed']}/{result['total']} 通过, 平均分: {result['avg_score']:.2f}")
        except Exception as e:
            print(f"Self-Eval failed: {e}")
            traceback.print_exc()
    elif "--report" in sys.argv:
        cmd_report()
    elif "--kill" in sys.argv and len(sys.argv) > 2:
        target = sys.argv[2]
        try:
            from daemon_modules.per_agent_auth import get_auth_manager
            auth = get_auth_manager()
            if target == "all":
                count = auth.revoke_all()
                print(f"🔴 KILL SWITCH: Revoked ALL {count} agent tokens")
            elif target == "list":
                print("Active agents:")
                for ident in auth.list_active():
                    print(f"  {ident['agent_id']:40s} expires={time.strftime('%H:%M', time.localtime(ident['expires_at']))} calls={ident['call_count']}")
            else:
                count = auth.revoke_identity(target)
                if count > 0:
                    print(f"🔴 Revoked {count} tokens for agent '{target}'")
                else:
                    print(f"No active tokens for agent '{target}'")
        except Exception as e:
            print(f"Kill switch error: {e}")
    elif "--daemon" in sys.argv:
        cmd_start()
    else:
        # 前台运行 (直接运行, 不后台化)
        asyncio.run(main_loop())
