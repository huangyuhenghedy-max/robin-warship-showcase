"""
Robin Brain — 项目知识大脑
============================

SOTA 参考:
- obsidian-knowledge-brain v4: Agent 读写 .md + [[wikilink]] + 全局原子表
- Google Code Wiki: AST + 知识图谱 + 混合检索
- AutoDocLM: 分层推理(文件级→模块级→架构级)

知更鸟差异化:
- 纯 Markdown + wikilink, 零依赖(无图数据库/向量库)
- 守护进程自动积累(决策/踩坑/规则)
- Obsidian 可视化(打开项目目录即知识图谱)
- 跨项目学习(全局原子表, 重复教训自动推广)

目录结构:
    项目目录/.robin-brain/
        decisions.md       ← 架构决策 [[wikilink]]
        pitfalls.md        ← 踩坑记录
        rules.md           ← 项目规则(从失败中学习)
        architecture.md    ← 模块结构 + Mermaid 图
        atoms.json         ← 全局原子表(跨项目通用教训)
        sessions/          ← 每次会话摘要
            2026-07-14-session.md

用法:
    from daemon_modules.robin_brain import RobinBrain

    brain = RobinBrain("I:/开发项目/自动化剪辑")
    brain.bootstrap()                    # 首次播种
    ctx = brain.get_context()            # 获取知识上下文(注入prompt)
    brain.record_decision("用FFmpeg替代moviepy", "性能提升3x")
    brain.record_pitfall("中文路径导致FFmpeg失败", "用绝对路径+UTF-8")
    brain.record_session("改进了clip_selection算法, 质量0.22→0.35")
"""
import logging

logger = logging.getLogger(__name__)


import json
import os
import time
from pathlib import Path
from typing import Optional
from datetime import datetime


class RobinBrain:
    """项目知识大脑 — 让 Agent 快速读懂项目"""

    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.brain_dir = self.project_dir / ".robin-brain"
        self.sessions_dir = self.brain_dir / "sessions"

        # 全局原子表路径(跨项目共享)
        self.global_atoms_path = Path.home() / ".robin-brain-atoms.json"

    # ── 初始化/播种 ──

    def bootstrap(self, force: bool = False) -> dict:
        """
        首次播种: 扫描项目 → 生成初始知识文件

        Args:
            force: 强制重新播种(覆盖已有)

        Returns:
            dict: {"created": [...], "skipped": [...], "errors": [...]}
        """
        result = {"created": [], "skipped": [], "errors": []}

        # 创建目录
        self.brain_dir.mkdir(exist_ok=True)
        self.sessions_dir.mkdir(exist_ok=True)

        # 1. architecture.md — 项目结构分析
        arch_path = self.brain_dir / "architecture.md"
        if force or not arch_path.exists():
            try:
                content = self._generate_architecture()
                arch_path.write_text(content, encoding="utf-8")
                result["created"].append("architecture.md")
            except Exception as e:
                result["errors"].append(f"architecture.md: {e}")
        else:
            result["skipped"].append("architecture.md")

        # 2. decisions.md — 架构决策记录
        dec_path = self.brain_dir / "decisions.md"
        if force or not dec_path.exists():
            template = self._template_decisions()
            dec_path.write_text(template, encoding="utf-8")
            result["created"].append("decisions.md")
        else:
            result["skipped"].append("decisions.md")

        # 3. pitfalls.md — 踩坑记录
        pit_path = self.brain_dir / "pitfalls.md"
        if force or not pit_path.exists():
            template = self._template_pitfalls()
            pit_path.write_text(template, encoding="utf-8")
            result["created"].append("pitfalls.md")
        else:
            result["skipped"].append("pitfalls.md")

        # 4. rules.md — 项目规则
        rules_path = self.brain_dir / "rules.md"
        if force or not rules_path.exists():
            template = self._template_rules()
            rules_path.write_text(template, encoding="utf-8")
            result["created"].append("rules.md")
        else:
            result["skipped"].append("rules.md")

        # 5. atoms.json — 全局原子表(如果不存在)
        if not self.global_atoms_path.exists():
            self.global_atoms_path.write_text(
                json.dumps({"atoms": [], "version": 1}, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            result["created"].append("~/.robin-brain-atoms.json")

        # 6. .gitignore — 不把 brain 提交到 git(可选)
        gitignore = self.brain_dir / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text("# Robin Brain 知识大脑 — 本地项目知识, 不入版本控制\n", encoding="utf-8")

        return result

    def _generate_architecture(self) -> str:
        """扫描项目目录 → 生成架构文档"""
        lines = [
            f"# {self.project_dir.name} — 项目架构",
            "",
            f"> 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "> 用 Obsidian 打开项目目录可查看知识图谱",
            "",
        ]

        # 项目描述
        readme = self._read_readme()
        if readme:
            lines.append("## 项目概述")
            lines.append("")
            lines.append(readme[:500])
            lines.append("")

        # 目录结构
        lines.append("## 目录结构")
        lines.append("")
        lines.append("```")
        tree = self._scan_tree(max_depth=3, max_items=50)
        lines.append(tree)
        lines.append("```")
        lines.append("")

        # 模块分析
        modules = self._analyze_modules()
        if modules:
            lines.append("## 核心模块")
            lines.append("")
            for mod in modules:
                lines.append(f"### [[{mod['name']}]]")
                if mod.get("desc"):
                    lines.append(f"- {mod['desc']}")
                if mod.get("files"):
                    lines.append(f"- 文件数: {mod['files']}")
                if mod.get("lang"):
                    lines.append(f"- 语言: {mod['lang']}")
                if mod.get("deps"):
                    lines.append(f"- 依赖: {', '.join(mod['deps'][:5])}")
                lines.append("")

        # Mermaid 依赖图
        mermaid = self._generate_mermaid(modules)
        if mermaid:
            lines.append("## 模块依赖图")
            lines.append("")
            lines.append("```mermaid")
            lines.append(mermaid)
            lines.append("```")
            lines.append("")

        # 技术栈
        tech = self._detect_tech_stack()
        if tech:
            lines.append("## 技术栈")
            lines.append("")
            for k, v in tech.items():
                lines.append(f"- {k}: {v}")
            lines.append("")

        # 关键文件
        key_files = self._find_key_files()
        if key_files:
            lines.append("## 关键文件")
            lines.append("")
            for f in key_files:
                lines.append(f"- [[{f}]]")
            lines.append("")

        lines.append("---")
        lines.append("*此文件由 Robin Brain 自动生成，守护进程工作时会自动更新*")

        return "\n".join(lines)

    def _scan_tree(self, max_depth: int = 3, max_items: int = 50) -> str:
        """扫描目录树(排除 node_modules/.git/__pycache__ 等)"""
        EXCLUDE = {"node_modules", ".git", "__pycache__", "dist", "build", ".venv",
                   "venv", ".robin-brain", ".workbuddy", "codex-runtimes"}

        lines = []
        count = 0

        def _walk(path: Path, prefix: str, depth: int):
            nonlocal count
            if depth > max_depth or count > max_items:
                return
            try:
                items = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name))
            except PermissionError:
                return

            for item in items:
                if item.name in EXCLUDE or item.name.startswith("."):
                    continue
                count += 1
                if count > max_items:
                    lines.append(f"{prefix}... (truncated)")
                    return
                if item.is_dir():
                    lines.append(f"{prefix}📁 {item.name}/")
                    _walk(item, prefix + "  ", depth + 1)
                else:
                    lines.append(f"{prefix}📄 {item.name}")

        _walk(self.project_dir, "", 0)
        return "\n".join(lines)

    def _analyze_modules(self) -> list:
        """分析项目模块 — v2: 正确排除 node_modules/dist/build"""
        modules = []
        EXCLUDE = {"node_modules", ".git", "__pycache__", "dist", "build", ".venv",
                   "venv", ".robin-brain", ".workbuddy", "release", "codex-runtimes", "__pycache__"}
        EXCLUDE_GLOB = {"node_modules", ".git", "__pycache__", "dist", "build",
                        ".venv", "venv", "release", "codex-runtimes", ".robin-brain", ".workbuddy"}

        def count_files_real(path: Path) -> int:
            """递归统计文件数, 排除已知目录"""
            count = 0
            try:
                for item in path.rglob("*"):
                    # 跳过排除目录
                    skip = False
                    for parent in item.parents:
                        if parent.name in EXCLUDE_GLOB:
                            skip = True
                            break
                    if skip:
                        continue
                    if item.is_file():
                        count += 1
            except:
                count = 0
            return count

        def has_any_files(path: Path, pattern: str) -> bool:
            """检查目录下是否有匹配的文件(排除排除目录)"""
            try:
                for item in path.rglob(pattern):
                    skip = False
                    for parent in item.parents:
                        if parent.name in EXCLUDE_GLOB:
                            skip = True
                            break
                    if not skip:
                        return True
            except:
                logger.warning("except:pass -> logged", exc_info=True)
            return False

        try:
            for item in sorted(self.project_dir.iterdir()):
                if item.name in EXCLUDE or item.name.startswith("."):
                    continue
                if item.is_dir():
                    mod = {"name": item.name, "files": 0, "lang": "unknown", "deps": []}
                    # 统计文件数(v2: 排除node_modules等)
                    mod["files"] = count_files_real(item)
                    # 检测语言(v2: 排除干扰目录)
                    if has_any_files(item, "*.py"):
                        mod["lang"] = "python"
                    elif has_any_files(item, "*.tsx") or has_any_files(item, "*.ts"):
                        mod["lang"] = "typescript"
                    elif has_any_files(item, "*.lua"):
                        mod["lang"] = "lua"
                    elif has_any_files(item, "*.jsx"):
                        mod["lang"] = "react"
                    elif has_any_files(item, "*.html"):
                        mod["lang"] = "html"
                    else:
                        mod["lang"] = "other"
                    # 读取描述
                    for rname in ("README.md", "__init__.py"):
                        rp = item / rname
                        if rp.exists():
                            try:
                                text = rp.read_text("utf-8", errors="replace")[:200]
                                mod["desc"] = text.split("\n")[0][:100]
                            except:
                                logger.warning("except:pass -> logged", exc_info=True)
                            break
                    # 读取依赖
                    pkg = item / "package.json"
                    if pkg.exists():
                        try:
                            data = json.loads(pkg.read_text("utf-8"))
                            mod["deps"] = list(data.get("dependencies", {}).keys())[:5]
                        except:
                            logger.warning("except:pass -> logged", exc_info=True)
                    req = item / "requirements.txt"
                    if req.exists():
                        try:
                            lines = req.read_text("utf-8", errors="replace").split("\n")
                            mod["deps"] = [l.split("==")[0].strip() for l in lines if l.strip() and not l.startswith("#")][:5]
                        except:
                            logger.warning("except:pass -> logged", exc_info=True)
                    modules.append(mod)
        except Exception as _e: logger.warning("except:pass -> logged", exc_info=True)
        return modules

    def _generate_mermaid(self, modules: list) -> str:
        """生成 Mermaid 依赖图"""
        if not modules:
            return ""
        lines = ["graph TD"]
        for mod in modules:
            name = mod["name"].replace("-", "_").replace(" ", "_")
            label = mod["name"]
            lines.append(f"    {name}[{label}]")
        # 简单依赖关系(基于 import 分析太重, 先用目录层级推断)
        return "\n".join(lines)

    def _detect_tech_stack(self) -> dict:
        """检测技术栈"""
        tech = {}
        pkg = self.project_dir / "package.json"
        if pkg.exists():
            try:
                data = json.loads(pkg.read_text("utf-8"))
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                if "react" in deps: tech["前端框架"] = "React"
                if "vue" in deps: tech["前端框架"] = "Vue"
                if "vite" in deps: tech["构建工具"] = "Vite"
                if "typescript" in deps: tech["语言"] = "TypeScript"
            except:
                logger.warning("except:pass -> logged", exc_info=True)
        req = self.project_dir / "requirements.txt"
        if req.exists():
            try:
                text = req.read_text("utf-8", errors="replace").lower()
                if "aiohttp" in text: tech["后端框架"] = "aiohttp"
                elif "fastapi" in text: tech["后端框架"] = "FastAPI"
                elif "flask" in text: tech["后端框架"] = "Flask"
                if "ffmpeg" in text: tech["媒体处理"] = "FFmpeg"
                if "opencv" in text or "cv2" in text: tech["计算机视觉"] = "OpenCV"
                tech["语言"] = "Python"
            except:
                logger.warning("except:pass -> logged", exc_info=True)
        if any(self.project_dir.rglob("*.lua")):
            tech["语言"] = "Lua (LVGL)"
        return tech

    def _find_key_files(self) -> list:
        """找到关键文件(入口/配置/核心逻辑)"""
        KEY_NAMES = {
            "server.py", "app.py", "main.py", "main.ts", "main.tsx",
            "index.ts", "index.tsx", "app.lua",
            "package.json", "requirements.txt", "pyproject.toml",
            "vite.config.ts", "vite.config.js", "tsconfig.json",
            "config.yaml", "config.json",
        }
        found = []
        try:
            for f in self.project_dir.rglob("*"):
                if f.is_file() and f.name in KEY_NAMES:
                    found.append(str(f.relative_to(self.project_dir)))
                    if len(found) >= 15:
                        break
        except:
            logger.warning("except:pass -> logged", exc_info=True)
        return sorted(found)

    def _read_readme(self) -> str:
        """读取 README"""
        for name in ("README.md", "README.txt", "readme.md"):
            rp = self.project_dir / name
            if rp.exists():
                try:
                    return rp.read_text("utf-8", errors="replace")
                except:
                    logger.warning("except:pass -> logged", exc_info=True)
        return ""

    # ── 模板 ──

    def _template_decisions(self) -> str:
        return f"""# 架构决策记录

> 记录项目中的关键技术决策，用 [[wikilink]] 互链

## 格式
- **[DECISION]** 日期 — 决策内容
  - 原因: 为什么这样做
  - 替代方案: 考虑过但没选的
  - 影响: 影响了哪些 [[模块]]

---

*此文件由 Robin Brain 自动创建，守护进程工作时会自动追加*
"""

    def _template_pitfalls(self) -> str:
        return f"""# 踩坑记录

> 记录开发中遇到的坑和解决方案，避免重复踩

## 格式
- **[PITFALL]** 日期 — 问题描述
  - 现象: 出了什么错
  - 根因: 为什么出错
  - 解决: 怎么修的
  - 规则: 提炼出的 [[规则]]

---

*此文件由 Robin Brain 自动创建，守护进程工作时会自动追加*
"""

    def _template_rules(self) -> str:
        return f"""# 项目规则

> 从失败中学习的规则，守护进程必须遵守

## 格式
- **[RULE]** 规则内容
  - 来源: [[踩坑记录]] 链接
  - 强度: MUST(必须) / SHOULD(应该) / MAY(可以)

---

*此文件由 Robin Brain 自动创建，守护进程工作时会自动追加*
"""

    # ── 知识写入 ──

    def record_decision(self, decision: str, reason: str = "", alternatives: str = "", impact: str = ""):
        """记录架构决策"""
        path = self.brain_dir / "decisions.md"
        if not path.exists():
            return
        date = datetime.now().strftime("%Y-%m-%d")
        entry = f"\n- **[DECISION]** {date} — {decision}"
        if reason:
            entry += f"\n  - 原因: {reason}"
        if alternatives:
            entry += f"\n  - 替代方案: {alternatives}"
        if impact:
            entry += f"\n  - 影响: {impact}"
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write(entry + "\n")
        except Exception as _e: logger.warning("except:pass -> logged", exc_info=True)
    def record_pitfall(self, problem: str, solution: str = "", root_cause: str = "", rule: str = ""):
        """记录踩坑"""
        path = self.brain_dir / "pitfalls.md"
        if not path.exists():
            return
        date = datetime.now().strftime("%Y-%m-%d")
        entry = f"\n- **[PITFALL]** {date} — {problem}"
        if root_cause:
            entry += f"\n  - 根因: {root_cause}"
        if solution:
            entry += f"\n  - 解决: {solution}"
        if rule:
            entry += f"\n  - 规则: [[{rule}]]"
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write(entry + "\n")
        except Exception as _e: logger.warning("except:pass -> logged", exc_info=True)
        # 如果有规则，也写入 rules.md
        if rule:
            self.record_rule(rule, source=f"[[踩坑 {date}]]")

        # 检查是否应该晋升为全局原子
        self._check_promote_to_atom(problem, solution)

    def record_rule(self, rule: str, source: str = "", strength: str = "MUST"):
        """记录项目规则"""
        path = self.brain_dir / "rules.md"
        if not path.exists():
            return
        entry = f"\n- **[RULE]** {rule} ({strength})"
        if source:
            entry += f"\n  - 来源: {source}"
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write(entry + "\n")
        except Exception as _e: logger.warning("except:pass -> logged", exc_info=True)
    def record_session(self, summary: str, files_changed: list = None, quality: float = 0):
        """记录会话摘要"""
        date = datetime.now().strftime("%Y-%m-%d")
        session_path = self.sessions_dir / f"{date}-session.md"

        entry = f"# 会话 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        entry += f"## 摘要\n{summary}\n\n"
        if files_changed:
            entry += f"## 修改文件\n"
            for f in files_changed:
                entry += f"- [[{f}]]\n"
            entry += "\n"
        if quality > 0:
            entry += f"## 质量\n{quality:.2f}\n\n"
        entry += "---\n"

        try:
            with open(session_path, "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception as _e: logger.warning("except:pass -> logged", exc_info=True)
    # ── 知识读取 ──

    def get_context(self, max_chars: int = 3000) -> str:
        """
        获取项目知识上下文(注入 prompt)

        优先级: rules > pitfalls > decisions > architecture
        """
        parts = []

        # 1. rules (最高优先级, Agent 必须遵守)
        rules_path = self.brain_dir / "rules.md"
        if rules_path.exists():
            try:
                text = rules_path.read_text("utf-8", errors="replace")
                rules = [l for l in text.split("\n") if l.strip().startswith("- **[RULE]**")]
                if rules:
                    parts.append("== PROJECT RULES (MUST follow) ==")
                    parts.extend(rules[:10])  # 最多10条
            except:
                logger.warning("except:pass -> logged", exc_info=True)

        # 2. pitfalls (避免重复踩坑)
        pit_path = self.brain_dir / "pitfalls.md"
        if pit_path.exists():
            try:
                text = pit_path.read_text("utf-8", errors="replace")
                pitfalls = [l for l in text.split("\n") if l.strip().startswith("- **[PITFALL]**")]
                if pitfalls:
                    parts.append("\n== KNOWN PITFALLS (avoid these) ==")
                    parts.extend(pitfalls[:5])  # 最近5条
            except:
                logger.warning("except:pass -> logged", exc_info=True)

        # 3. decisions (理解为什么这样设计)
        dec_path = self.brain_dir / "decisions.md"
        if dec_path.exists():
            try:
                text = dec_path.read_text("utf-8", errors="replace")
                decisions = [l for l in text.split("\n") if l.strip().startswith("- **[DECISION]**")]
                if decisions:
                    parts.append("\n== KEY DECISIONS ==")
                    parts.extend(decisions[:5])
            except:
                logger.warning("except:pass -> logged", exc_info=True)

        # 4. architecture (项目结构概览 + SOTA目标)
        arch_path = self.brain_dir / "architecture.md"
        if arch_path.exists():
            try:
                text = arch_path.read_text("utf-8", errors="replace")
                # 4a. 结构概览(前500字符)
                parts.append("\n== ARCHITECTURE ==")
                parts.append(text[:500])
                # 4b. SOTA目标(提取"SOTA目标"行, 优先级高于结构概览)
                sota_lines = []
                for line in text.split("\n"):
                    if "**SOTA目标**" in line or "SOTA目标" in line:
                        sota_lines.append(line.strip())
                if sota_lines:
                    parts.append("\n== SOTA TARGETS (aim for these) ==")
                    parts.extend(sota_lines[:8])  # 最多8条SOTA目标
                # 4c. 竞品关键数据(提取含数字的"我们差距"行)
                gap_lines = []
                for line in text.split("\n"):
                    if "我们差距" in line and any(c.isdigit() for c in line):
                        gap_lines.append(line.strip())
                if gap_lines:
                    parts.append("\n== COMPETITIVE GAPS (data-backed) ==")
                    parts.extend(gap_lines[:5])  # 最多5条数据支撑的差距
            except:
                logger.warning("except:pass -> logged", exc_info=True)

        # 5. 全局原子(跨项目通用教训)
        atoms = self._load_global_atoms()
        if atoms:
            parts.append("\n== GLOBAL LESSONS (from other projects) ==")
            for atom in atoms[:5]:
                parts.append(f"- {atom.get('pattern', '')}: {atom.get('solution', '')}")

        full = "\n".join(parts)
        if len(full) > max_chars:
            # 优先保留rules + sota_targets + gaps, 截断architecture
            full = full[:max_chars] + "\n... (truncated)"
        return full

    def get_sota_targets(self) -> list:
        """提取SOTA目标列表(用于验证改进是否达标)"""
        arch_path = self.brain_dir / "architecture.md"
        if not arch_path.exists():
            return []
        try:
            text = arch_path.read_text("utf-8", errors="replace")
            targets = []
            for line in text.split("\n"):
                if "**SOTA目标**" in line or line.strip().startswith("**SOTA目标**"):
                    targets.append(line.strip().lstrip("*").strip())
            return targets
        except:
            return []

    def record_sota_progress(self, target: str, achieved: bool, evidence: str = ""):
        """记录SOTA目标进展"""
        path = self.brain_dir / "decisions.md"
        if not path.exists():
            return
        date = datetime.now().strftime("%Y-%m-%d")
        status = "✅ ACHIEVED" if achieved else "❌ NOT YET"
        entry = f"\n- **[SOTA-CHECK]** {date} — {status}: {target}"
        if evidence:
            entry += f"\n  - 证据: {evidence}"
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write(entry + "\n")
        except Exception as _e: logger.warning("except:pass -> logged", exc_info=True)
    def has_brain(self) -> bool:
        """检查项目是否已有知识大脑"""
        return self.brain_dir.exists() and (self.brain_dir / "architecture.md").exists()

    # ── 全局原子表 ──

    def _load_global_atoms(self) -> list:
        """加载全局原子表"""
        if not self.global_atoms_path.exists():
            return []
        try:
            data = json.loads(self.global_atoms_path.read_text("utf-8"))
            return data.get("atoms", [])
        except:
            return []

    def _save_global_atoms(self, atoms: list):
        """保存全局原子表"""
        try:
            # 最多保留20个活跃原子
            active = [a for a in atoms if a.get("active", True)][:20]
            data = {"atoms": active, "version": 1, "updated": time.time()}
            tmp = self.global_atoms_path.with_suffix(".tmp")
            tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            tmp.replace(self.global_atoms_path)
        except:
            logger.warning("except:pass -> logged", exc_info=True)

    def _check_promote_to_atom(self, problem: str, solution: str):
        """检查是否应该晋升为全局原子(同一问题在2+项目出现)"""
        atoms = self._load_global_atoms()
        # 检查是否已有类似原子
        problem_key = problem.lower().strip()[:50]
        for atom in atoms:
            if atom.get("key", "").lower() == problem_key:
                atom["count"] = atom.get("count", 0) + 1
                atom["projects"] = list(set(atom.get("projects", []) + [self.project_dir.name]))
                if atom["count"] >= 2 and not atom.get("promoted"):
                    atom["promoted"] = True
                self._save_global_atoms(atoms)
                return

        # 新原子
        atoms.append({
            "key": problem_key,
            "pattern": problem[:80],
            "solution": solution[:80] if solution else "",
            "count": 1,
            "projects": [self.project_dir.name],
            "created": time.time(),
            "promoted": False,
            "active": True,
        })
        self._save_global_atoms(atoms)

    # ── 更新架构 ──

    def update_architecture(self):
        """重新扫描并更新架构文档"""
        arch_path = self.brain_dir / "architecture.md"
        try:
            content = self._generate_architecture()
            tmp = arch_path.with_suffix(".tmp")
            tmp.write_text(content, encoding="utf-8")
            tmp.replace(arch_path)
        except:
            logger.warning("except:pass -> logged", exc_info=True)

    # ── 项目状态评估 (SOTA: LLM-as-a-Judge 自验证) ──

    def generate_status(self) -> dict:
        """
        生成项目状态评估报告 — 自验证, 不自欺
        
        流程:
        1. 统计源码(排除干扰)
        2. 检测技术栈
        3. 检查构建状态
        4. 检查测试
        5. 估算完成度
        6. 标注数据可信度
        """
        EXCLUDE_GLOB = {"node_modules", ".git", "__pycache__", "dist", "build",
                        ".venv", "venv", "release", "codex-runtimes",
                        ".robin-brain", ".workbuddy", "assets"}

        status = {
            "project": self.project_dir.name,
            "updated": datetime.now().isoformat(),
            "confidence": "self-validated",  # 表明数据不是拍脑袋
            "errors": [],
        }

        # 1. 源码统计
        source_extensions = {".py", ".js", ".jsx", ".ts", ".tsx", ".lua",
                            ".css", ".html", ".vue", ".svelte"}
        source_files = []
        all_files = []
        try:
            for item in self.project_dir.rglob("*"):
                if not item.is_file():
                    continue
                skip = False
                for parent in item.parents:
                    if parent.name in EXCLUDE_GLOB:
                        skip = True
                        break
                if skip:
                    continue
                rel = str(item.relative_to(self.project_dir))
                all_files.append(rel)
                if item.suffix in source_extensions:
                    source_files.append(rel)
        except Exception as e:
            status["errors"].append(f"file_scan: {e}")

        status["source_files"] = len(source_files)
        status["total_files"] = len(all_files)
        status["source_list"] = source_files[:5]  # 样本

        # 2. 语言检测(加权)
        lang_scores = {}
        for f in source_files:
            ext = Path(f).suffix
            lang_scores[ext] = lang_scores.get(ext, 0) + 1
        total_src = max(sum(lang_scores.values()), 1)
        top_langs = sorted(lang_scores.items(), key=lambda x: -x[1])[:3]
        status["languages"] = [f"{ext} {count/total_src*100:.0f}%" for ext, count in top_langs]

        # 3. 构建状态 — 搜索子目录中的dist/
        has_pkg_json = (self.project_dir / "package.json").exists()
        has_vite = has_pkg_json and any("vite" in f for f in all_files if "node_modules" not in f)
        has_electron = has_pkg_json and any("electron" in f for f in all_files if "node_modules" not in f)
        # 递归搜索dist/
        has_dist = False
        for item in self.project_dir.rglob("dist/index.html"):
            skip = False
            for parent in item.parents:
                if parent.name in EXCLUDE_GLOB:
                    skip = True
                    break
            if not skip:
                has_dist = True
                break
        has_sqlite = any("sqlite" in f.lower() or "sql" in f.lower() for f in all_files if f.endswith(".sql"))
        has_test = any("test" in f.lower() for f in source_files)

        status["tech_stack"] = []
        if has_pkg_json:
            status["tech_stack"].append("React/JS" if has_vite else "Node")
        if has_electron:
            status["tech_stack"].append("Electron")
        if has_sqlite:
            status["tech_stack"].append("SQLite")
        if any(f.endswith(".py") for f in source_files):
            status["tech_stack"].append("Python")

        status["build_status"] = "built" if has_dist else "unbuilt"
        status["has_tests"] = has_test
        status["has_dist"] = has_dist

        # 4. 估算完成度(v2: 多层次信号)
        signals_achieved = []
        signals_total = 18

        # 基础设施层
        if (self.project_dir / "package.json").exists(): signals_achieved.append("pkg_json")
        if any(f.endswith((".jsx", ".tsx")) for f in source_files): signals_achieved.append("ui_framework")
        if any(f.endswith((".py")) for f in source_files): signals_achieved.append("backend")

        # 功能层 — 搜索子目录中的src/(支持多级项目结构)
        src_base_dirs = ["src", "server/src", "robin-agent/server", "nexus-base/src", "app"]
        found_dirs = {"engine": False, "pages": False, "components": False, "services": False, "models": False}
        for sub in src_base_dirs:
            base = self.project_dir / sub
            if not base.exists():
                continue
            for sd in ["engine", "pages", "components", "services", "models", "api", "routes", "daemon_modules"]:
                if sd in found_dirs and not found_dirs[sd]:
                    target = base / sd
                    if target.exists() and any(target.iterdir()):
                        found_dirs[sd] = True

        for sd, found in found_dirs.items():
            if found: signals_achieved.append(f"has_{sd}")

        # 检测关键基础设施
        bin_dir = self.project_dir / "node_modules" / ".bin"
        has_npm = bin_dir.exists()
        if has_npm: signals_achieved.append("has_npm")

        daemon_state = self.project_dir / "l6_daemon_state.json"
        if daemon_state.exists(): signals_achieved.append("has_daemon")

        has_vite_config = any("vite.config" in f for f in all_files)
        if has_vite_config: signals_achieved.append("has_vite_config")

        has_live2d = any("live2d" in f.lower() or "moc3" in f.lower() for f in all_files)
        if has_live2d: signals_achieved.append("live2d")

        # 数据库/存储
        if has_sqlite: signals_achieved.append("database")
        if any("auth" in f.lower() for f in source_files): signals_achieved.append("auth")

        # 质量层
        if has_dist: signals_achieved.append("built")
        if has_test: signals_achieved.append("tests")
        if has_electron: signals_achieved.append("electron_packaged")
        if self.brain_dir.exists(): signals_achieved.append("knowledge_base")

        # 规模因子: 大项目需要更多信号才能算高完成度
        size_factor = 1.0
        if len(source_files) > 100: size_factor = 0.85
        if len(source_files) > 500: size_factor = 0.7
        if len(source_files) > 2000: size_factor = 0.5

        base_pct = len(signals_achieved) / signals_total * 100 * size_factor
        # 对已构建的项目做额外加成
        if has_dist:
            base_pct = base_pct * 1.3 + 15
        # 钳制范围
        base_pct = max(min(base_pct, 95), 5)

        status["signals"] = f"{len(signals_achieved)}/{signals_total}"
        status["signals_list"] = signals_achieved
        status["completion_estimate"] = round(base_pct)
        status["confidence_note"] = f"基于{total_src}个源码文件的自动评估, 规模因子={size_factor:.2f}"

        # 5. 自验证: 检查已发布的SOTA知识是否准确
        architecture_path = self.brain_dir / "architecture.md"
        if architecture_path.exists():
            try:
                arch_text = architecture_path.read_text("utf-8", errors="replace")[:500]
                # 检查是否有明显的检测错误(语言检测)
                if "语言: python" in arch_text and any("tsx" in f or "jsx" in f for f in source_files):
                    status["warnings"] = "architecture.md语言检测有误(标成python但实际是JS), 将在下次做梦时修复"
            except:
                logger.warning("except:pass -> logged", exc_info=True)

        return status

    def write_status(self):
        """写 status.md 到知识库"""
        status = self.generate_status()
        content = f"""# {status['project']} — 项目状态评估

> 自动生成于 {status['updated']}
> 可信度: {status['confidence']} (基于实际文件扫描, 非估算)

## 概览
- 源码文件: {status['source_files']} 个
- 总文件: {status['total_files']} 个 (含配置文件/资源)
- 语言: {', '.join(status['languages'])}
- 技术栈: {', '.join(status['tech_stack'])}
- 构建状态: {'✅ 已构建' if status['has_dist'] else '❌ 未构建'}
- 测试: {'✅ 有测试' if status['has_tests'] else '❌ 无测试'}
- 完成度估算: **{status['completion_estimate']}%**
- 信号: {status.get('signals', 'N/A')}

## 说明
{status.get('confidence_note', '')}
"""
        if status.get("warnings"):
            content += f"\n## 警告\n{status['warnings']}\n"

        path = self.brain_dir / "status.md"
        try:
            tmp = path.with_suffix(".tmp")
            tmp.write_text(content, encoding="utf-8")
            tmp.replace(path)
        except:
            logger.warning("except:pass -> logged", exc_info=True)

        return status


# ── 便捷函数 ─────────────────────────────────────────────────────

def bootstrap_project(project_dir: str, force: bool = False) -> dict:
    """给项目播种知识大脑"""
    brain = RobinBrain(project_dir)
    return brain.bootstrap(force=force)


def get_project_brain_context(project_dir: str, max_chars: int = 2000) -> str:
    """获取项目知识上下文(用于注入 prompt)"""
    brain = RobinBrain(project_dir)
    if not brain.has_brain():
        return ""
    return brain.get_context(max_chars=max_chars)
