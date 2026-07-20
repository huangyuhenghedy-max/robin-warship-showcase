#!/usr/bin/env python3
"""
知更鸟舰队 HUD 简化版
=====================
5 层指挥链实时态势展示:
  L0 旗舰 Robin Flagship
  └ L1 战术航母 Carrier
    └ L2 巡洋舰 Cruiser
      └ L3 驱逐舰 Destroyer
        └ L4 侦察无人机 Recon Drone

演示能力:
  · 指挥链拓扑可视化 (5 层)
  · 周期注入故障 → 自愈守护自动恢复
  · 与 CodeWorker / Self-Heal 模块协同
"""

import os
import sys
import time
import random

# ─── ANSI 配色 ───
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


# ─── 5 层指挥链结构 ───
FLEET = {
    "L0":   dict(name="Robin Flagship",   role="Supreme",  icon="\u2605", children=["L1-A", "L1-B"]),
    "L1-A": dict(name="Carrier Alpha",    role="Tactical", icon="\u25B2", children=["L2-A", "L2-B"]),
    "L1-B": dict(name="Carrier Beta",     role="Tactical", icon="\u25B2", children=["L2-C"]),
    "L2-A": dict(name="Cruiser Aurora",   role="Patrol",   icon="\u25C6", children=["L3-A"]),
    "L2-B": dict(name="Cruiser Beacon",   role="Patrol",   icon="\u25C6", children=["L3-B"]),
    "L2-C": dict(name="Cruiser Comet",    role="Patrol",   icon="\u25C6", children=["L3-C"]),
    "L3-A": dict(name="Destroyer Echo",   role="Strike",   icon="\u25A0", children=["L4-A"]),
    "L3-B": dict(name="Destroyer Falcon", role="Strike",   icon="\u25A0", children=["L4-B"]),
    "L3-C": dict(name="Destroyer Gale",   role="Strike",   icon="\u25A0", children=[]),
    "L4-A": dict(name="Recon Drone \u03B1", role="Scout",  icon="\u25CF", children=[]),
    "L4-B": dict(name="Recon Drone \u03B2", role="Scout",  icon="\u25CF", children=[]),
}

# 节点实时状态
STATE = {}


def init_state():
    for nid in FLEET:
        STATE[nid] = {"health": 100, "status": "ONLINE"}


def color_for(status, health):
    if status == "CRASH":
        return RED
    if status == "DEGRADED" or health < 50:
        return YELLOW
    return GREEN


def health_bar(health, color):
    full = int(round(health / 100 * 10))
    return color + ("\u2588" * full) + ("\u2591" * (10 - full)) + RESET


def render_topology(events=None):
    print(f"\n  {BOLD}Command Chain Topology:{RESET}")
    print(f"  {DIM}" + "-" * 56 + RESET)

    def walk(nid, depth=0):
        node = FLEET[nid]
        st = STATE.get(nid, {})
        indent = "    " * depth
        connector = "\u2514\u2500 " if depth > 0 else ""
        health = st.get("health", 100)
        status = st.get("status", "?")
        c = color_for(status, health)
        bar = health_bar(health, c)
        print(f"  {indent}{connector}{node['icon']} "
              f"{BOLD}{nid:<6}{RESET} "
              f"{node['name']:<22} "
              f"{bar} "
              f"{c}{health:3d}%{RESET} "
              f"{c}{status:<8}{RESET}")
        for child in node["children"]:
            walk(child, depth + 1)

    walk("L0")

    if events:
        print()
        for e in events:
            print(f"  {e}")


def render_header(tick):
    print("\n" + "=" * 64)
    print(f"  {BOLD}ROBIN WARSHIP HUD{RESET}  "
          f"{DIM}5-Layer Command Chain{RESET}  "
          f"tick={tick:03d}  {time.strftime('%H:%M:%S')}")
    print("=" * 64)


def render_summary():
    total = len(FLEET)
    online = sum(1 for s in STATE.values() if s["status"] == "ONLINE")
    crashed = sum(1 for s in STATE.values() if s["status"] == "CRASH")
    degraded = sum(1 for s in STATE.values() if s["status"] == "DEGRADED")
    print(f"\n  {BOLD}Fleet Status:{RESET}  "
          f"{GREEN}{online} online{RESET} / "
          f"{YELLOW}{degraded} degraded{RESET} / "
          f"{RED}{crashed} crashed{RESET}  "
          f"of {total} units")


def inject_failure():
    """随机击毁一个非旗舰节点"""
    candidates = [n for n in FLEET if n != "L0"]
    if not candidates:
        return None
    target = random.choice(candidates)
    STATE[target]["status"] = "CRASH"
    STATE[target]["health"] = 0
    return target


def self_heal():
    """自愈守护:恢复所有异常节点"""
    healed = []
    for nid, st in STATE.items():
        if st["status"] in ("CRASH", "DEGRADED"):
            st["status"] = "ONLINE"
            st["health"] = 100
            healed.append(nid)
    return healed


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def run_demo(ticks=10, fps=1.2):
    init_state()
    clear_screen()

    for tick in range(1, ticks + 1):
        clear_screen()
        render_header(tick)

        events = []

        # tick 4: 注入故障
        if tick == 4:
            tgt = inject_failure()
            if tgt:
                events.append(
                    f"{RED}\u26A1 [{tick:03d}] ALERT: {tgt} "
                    f"({FLEET[tgt]['name']}) lost contact!{RESET}"
                )
                events.append(
                    f"{YELLOW}     Guardian detecting anomaly...{RESET}"
                )

        # tick 5: 进一步劣化
        if tick == 5:
            tgt2 = inject_failure()
            if tgt2:
                events.append(
                    f"{RED}\u26A1 [{tick:03d}] ALERT: {tgt2} "
                    f"({FLEET[tgt2]['name']}) also lost!{RESET}"
                )

        # tick 7: 自愈守护启动
        if tick == 7:
            events.append(
                f"{CYAN}\u2139 [{tick:03d}] Self-Heal Guardian engaged.{RESET}"
            )
            healed = self_heal()
            for nid in healed:
                events.append(
                    f"{GREEN}\u2714 [{tick:03d}] SELF-HEAL: {nid} "
                    f"({FLEET[nid]['name']}) restored.{RESET}"
                )

        render_topology(events)
        render_summary()

        print(f"\n  {DIM}Ctrl+C to exit \u00B7 refresh in {fps:.1f}s{RESET}")
        time.sleep(fps)

    print(f"\n  {BOLD}Demo complete.{RESET}")


if __name__ == "__main__":
    print("\nROBIN WARSHIP HUD Demo - 5-Layer Command Chain")
    print("-" * 60)
    print("Press Enter to start (auto-starts in non-interactive mode)...")
    try:
        input()
    except (EOFError, KeyboardInterrupt):
        pass
    try:
        run_demo()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Demo interrupted by user.{RESET}")
        sys.exit(0)