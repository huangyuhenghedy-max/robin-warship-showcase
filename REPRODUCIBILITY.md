# 可复现性声明 · Reproducibility Statement

## 项目信息

| 项目 | 内容 |
|:----|:------|
| **项目名称** | 知更鸟战舰 · Robin Fleet |
| **版本** | v0.1.0 (Alpha) |
| **提交日期** | 2026-07-20 |
| **代码仓库** | https://github.com/huangyuhenghedy-max/robin-warship-showcase |
| **开源协议** | Apache 2.0 |
| **所属赛道** | 无界应用 · Boundless Agents (GOAI世界人工智能开源大赛) |

## 环境依赖

### 硬件要求
- CPU: x86_64 架构，4核以上推荐
- 内存: 8GB 以上推荐
- 磁盘: 5GB 可用空间
- 网络: 需访问 OpenAI 兼容 API 端点

### 软件环境
- 操作系统: Windows 10/11, Ubuntu 20.04+, macOS 12+
- Python: 3.10 ~ 3.12
- Node.js: 18+ (前端 Demo 可选)

### Python 依赖
```
flask>=3.0
requests>=2.31
openai>=1.0
pydantic>=2.0
pyyaml>=6.0
```

### API 密钥配置
系统需要一个 OpenAI 兼容的 LLM API 端点。配置文件位于 `server/.secrets.json`：

```json
{
  "llm_fast": {
    "api_key": "your-api-key",
    "base_url": "https://open.bigmodel.cn/api/coding/paas/v4",
    "model": "glm-4-flash"
  },
  "llm_codingplan": {
    "api_key": "your-api-key",
    "base_url": "https://open.bigmodel.cn/api/paas/v4"
  }
}
```

系统默认使用 GLM-4-Flash (免费，128K上下文)，也可适配任何 OpenAI 兼容端点 (DeepSeek / Qwen / GPT)。

## 快速复现步骤

### 1. 克隆仓库
```bash
git clone https://github.com/huangyuhenghedy-max/robin-warship-showcase.git
cd robin-warship-showcase
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置 API 密钥
```bash
cp config/secrets.template.json server/.secrets.json
# 编辑 server/.secrets.json，填入你的 API Key
```

### 4. 启动系统
```bash
python -m server.l6_daemon_v5 --go
```

### 5. 打开 HUD 指挥面板
浏览器打开 `http://localhost:19530/fleet-hud`

### 6. 启动演练场景
在 HUD 面板点击 `启动暴雨内涝演练`，观察 5 层指挥链自动执行。

## 随机种子

为确保结果可复现，系统中使用以下固定随机种子：
- Python random: `seed=42`
- NumPy random: `seed=42`（如使用）
- LLM 采样温度: `temperature=0.3`（快速任务） / `0.7`（创意任务）

## 验证清单

| 验证项 | 预期结果 | 验证命令 |
|:------|:--------|:---------|
| 守护进程启动 | `PID xxxx, status: running` | `python -m server.l6_daemon_v5 --status` |
| API 连通性 | `✅ API OK` | `python -m server.check_api` |
| HUD 面板 | 浏览器可访问 | `curl http://localhost:19530/fleet-hud` |
| 演练场景触发 | 控制台显示5层链执行日志 | 观察 HUD 事件流 |

## 已知限制

1. 当前为 Alpha 版本，部分模块处于开发阶段
2. 全功能运行需要有效的 OpenAI 兼容 API Key
3. 前端 Live2D 模块需要 WebGL 支持的浏览器
4. 城市治理场景的 GIS 数据为模拟数据，非真实市政数据

---

*本声明符合 GOAI 世界人工智能开源大赛 · 无界应用赛道的可复现性要求。*
