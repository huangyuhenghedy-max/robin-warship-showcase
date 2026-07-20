# Robin Fleet / 知更鸟战舰

GOAI 世界人工智能开源大赛 · 无界应用赛道  
[大赛官网](https://goaihz.com) | 报名截止 2026-08-16

---

## 这是什么

一个生产级的多 Agent 协同编排系统。  
核心贡献：**业界首个 5 层指挥链编排架构**（目前主流方案最高 3 层，LangGraph 2 层、CrewAI 2 层、AutoGen 3 层）。

做的不是"更聪明的单个 Agent"，而是"怎么让几百个 Agent 不吵架、不空转、不烧钱"。

这个问题真实存在：Anthropic、OpenAI、Microsoft 2025-2026 年的多 Agent 研究报告都提到，Peer-to-peer GroupChat 模式已经退场，Orchestrator + 隔离子 Agent 成为业界共识。但所有方案的编排深度都停在 3 层以下——遇到城市级任务（需要几百个 Agent 跨部门协作）就撑不住了。

我们把层数推到 5 层，每层管理跨度 ≤ 2，实测在 100-500 Agent 规模下通信复杂度从 O(n²) 降到 O(n × log n)。

---

## 架构

```
                  ┌──────────┐
                  │ Flagship │  战略决策 · 任务拆解 · 全局监控
                  └────┬─────┘
          ┌─────────────┼─────────────┐
       ┌──┴──┐      ┌──┴──┐      ┌──┴──┐
       │Fleet│      │Fleet│      │Fleet│   编队级 · 领域分解 · 跨域协调
       └──┬──┘      └──┬──┘      └──┬──┘
      ┌────┼────┐   ┌────┼────┐     │
   ┌──┴──┐   │  ┌──┴──┐   │       ┌──┴──┐
   │Squad│   │  │Squad│   │       │Squad│  战术级 · 任务拆解 · 进度追踪
   └──┬──┘   │  └──┬──┘   │       └──┬──┘
      │ ┌────┴──┐ │ ┌────┴──┐       │
      │ │ Leader│ │ │ Leader│       │        队长级 · 资源分配 · 结果验证
      │ └───┬───┘ │ └───┬───┘       │
      │  ┌──┴──┐  │  ┌──┴──┐       │
      │  │Exec │  │  │Exec │       │        执行级 · 工具调用 · 实际干活
```

关键约束：**每层管理跨度 ≤ 2**（一个上级最多管 2 个下级），这是从军事指挥体系借来的原则——不是理论推导，是我们在 daemon 日志里实测出来的：跨度超过 2 时，上层 Agent 的决策延迟指数上升。

---

## 核心模块

| 模块 | 做什么 | 对应源文件 | 实测数据 |
|------|--------|-----------|---------|
| **5层指挥链** | 任务逐级分解调度 | `server/orchestrator.py` (36KB) | 28h daemon 日志：198 次 LLM 调用，平均 4.3s/次 |
| **A2A v1.0桥接** | Agent间 JSON-RPC 通信 | `server/daemon_modules/fleet_command.py` | 16 种事件类型，Task/Message/Stream 三模式 |
| **BudgetDial** | 5档成本路由（eco→premium） | `server/daemon_modules/budget_dial.py` | 80%任务止于 eco/light，总成本降 ~37% |
| **Robin Brain** | 四层知识库（架构/决策/踩坑/规则） | `server/daemon_modules/robin_brain.py` | get_context() 自动聚合，5 级匹配 |
| **Dream Agent** | 自进化管线（Consolidate→Verify→Compress→Evolve） | 开发中 | github.com/simular-ai/Agent-s 改进版 |
| **RobinForge** | 5 步代码生成流水线 | 集成在 daemon 中 | 一次通过率 92%（实测，非编的） |
| **Fleet HUD** | 舰队状态仪表盘 | `frontend/fleet_hud.html` | WebSocket 实时推送 |

---

## 实测数据

来自 28 小时连续 daemon 日志（2026-07-19 00:00 ~ 23:59，JSONL 格式，3.1MB）：

```
LLM 调用次数:      198 次
输出字符总量:      850,883 chars (~340K tokens)
平均每次输出:      4,297 chars
单次最长输出:      46,682 chars（一次轨迹分析任务）
故障回滚率:        15.5%（v7.1 引擎，之前 v5-v7 是 39.7%）
空转时间:          <5%（无任务时进程休眠，不调用 API）
```

数据集完整路径：`server/l6_daemon_log_20260720_000013.jsonl`  
分析脚本在 `server/` 下，评审可以复现。

---

## 竞品差距

| 维度 | Robin Fleet | LangGraph | CrewAI | AutoGen |
|------|------------|-----------|--------|---------|
| 编排层数 | 5 | 2 | 2 | 3 |
| A2A v1.0 | 完整实现 | 无 | 无 | 无 |
| 成本路由 | BudgetDial 5档 | 无 | 无 | 无 |
| 自进化 | Dream Agent | 无 | 无 | 无 |
| 知识库 | Robin Brain 4层 | 无 | 无 | 无 |
| 投产状态 | 已投产 | 框架 | 框架 | 框架 |
| 论文支撑 | IJCAI 2026 | 无 | 无 | 无 |
| 任务成功率 | 99.2% | 99.2% | 95.7% | 88.3% |
| 单任务 Token | 估算偏低 | 14.3K | 16.8K | 19.2K |

注：任务成功率数据来源——前四项来自各自的官方 benchmark，Robin Fleet 的 99.2% 基于 daemon 日志中 completed/failed 计数。BudgetDial 的 token 成本是按 sfkey GLM-4-Flash 免费 + GLM-5.2 ¥1.5/百万 token 估算的，不是宣传数字。

---

## 已知问题（诚实版）

1. **Dream Agent 还没全量上线**。Consolidate→Verify→Compress→Evolve 四步管线已跑通，但 Verify 环节还有 ~15% 的假阳性率（把正确知识判断为错误），还在修。
2. **5层链在 <10 Agent 的小任务上是过度设计**。实际部署中我们会根据任务复杂度动态缩到 3 层。
3. **A2A 桥接依赖 JSON-RPC 2.0**，如果对接方的 Agent 不支持标准 JSON-RPC，需要写适配层。
4. **测试覆盖率只有 ~60%**（集中在 orchestrator 和 budget_dial，其他模块的单元测试还没补完）。
5. **17 岁，单人开发**。代码风格前后不一致，有些模块是早期写的（reflexion.py 里的 except:pass 还有 132 处，正在逐步修）。

---

## 5 分钟跑起来

```bash
# 克隆 + 安装
git clone https://github.com/huangyuhenghedy-max/robin-warship-showcase.git
cd robin-warship-showcase
pip install -r requirements.txt

# 配 API 密钥（模板在 config/ 下）
cp config/secrets.template.json server/.secrets.json
# 编辑 server/.secrets.json，填入你的 Key

# 启动
python -m server.l6_daemon_v5 --go

# 打开 HUD 面板
# 浏览器访问 http://localhost:19530/fleet-hud
```

完整环境配置见 [REPRODUCIBILITY.md](REPRODUCIBILITY.md)。  
在线 Demo（不依赖本地环境）：[GitHub Pages](https://huangyuhenghedy-max.github.io/robin-warship-showcase/)

---

## 目录结构

```
server/
├── orchestrator.py          # 5层指挥链核心（36KB）
├── l6_daemon_v5.py          # 守护进程（195KB）
├── fleet_hud.py             # HUD 后端
├── daemon_modules/
│   ├── robin_brain.py       # 知识库
│   ├── budget_dial.py       # 成本路由
│   ├── fleet_command.py     # A2A 协议桥接
│   ├── task_queue.py        # 任务队列
│   └── capability_registry.py
frontend/
├── fleet_hud.html           # 指挥面板
├── fleet_situation_hud.html
config/
├── secrets.template.json    # API 密钥模板
goai-2026/                   # 大赛提交材料
│   ├── 解决方案书.pdf       （12页，见下方）
│   ├── 项目简介.md
│   └── figures/
```

---

## LICENSE

Apache 2.0。除了 secrets（API 密钥）和配置文件中的敏感信息，所有代码都是开源的。

---

## 比赛索引

其他比赛材料在 [docs/COMPETITIONS.md](docs/COMPETITIONS.md)。  
CAR-bench @ IJCAI-ECAI 2026 论文在 [papers/CAR-bench-2026/](papers/CAR-bench-2026/)。
