#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""常驻调度器：每 3 小时触发一次 heartbeat + sonnet 注册重试。（关机不触发，由 Hermes 运行时驱动）"""
import subprocess, time, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = "C:/Python312/python.exe"
HB = HERE / "heartbeat.py"
REG = HERE / "sonnet_register.py"
LOG = HERE / "heartbeat.scheduler.log"
INTERVAL = 3 * 3600


def run(cmd, label):
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    try:
        r = subprocess.run([PY, str(cmd)], capture_output=True, text=True, cwd=str(HERE), timeout=150)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {label} exit={r.returncode}\n" + r.stdout + r.stderr)
    except Exception as e:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {label} EXC {e}\n")


while True:
    run(HB, "heartbeat")
    run(REG, "sonnet_register")
    time.sleep(INTERVAL)
