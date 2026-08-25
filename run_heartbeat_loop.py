#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""常驻调度器：每 3 小时调用一次 heartbeat.py。（关机不触发，由 Hermes 运行时驱动）"""
import subprocess, time, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
PY = "C:/Python312/python.exe"
HB = HERE / "heartbeat.py"
LOG = HERE / "heartbeat.scheduler.log"
INTERVAL = 3 * 3600
while True:
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    try:
        r = subprocess.run([PY, str(HB)], capture_output=True, text=True, cwd=str(HERE), timeout=120)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] exit={r.returncode}\n" + r.stdout + r.stderr)
    except Exception as e:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] EXC {e}\n")
    time.sleep(INTERVAL)
