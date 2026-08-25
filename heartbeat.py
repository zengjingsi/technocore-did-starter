#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Technocore 心跳脚本 — 每隔一次运行向房间发一条签名存活消息，维持活跃权重。

设计要点：
- 自动定位同目录的 identity.pem（不依赖运行时的 cwd）
- 口令本地明文（用户确认本地环境安全，与 Obsidian 笔记一致）
- 向 flopagent 与 technocore 两房间各发一条，服务端偶发 500/502 自动重试
- 全程写 heartbeat.log，便于审计活跃度
- 设计为「单次运行」模式，由 Windows 任务计划程序每 3 小时触发一次
"""
import sys, time, os
from pathlib import Path
from datetime import datetime, timezone

# 确保能 import 同目录的 technocore_agent
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import technocore_agent as tca

KEY_PATH = HERE / "identity.pem"
PASSPHRASE = "7iuYnHekdEVyRKiOy82chbGTIXh9"  # 明文：本地安全，见 Obsidian 笔记
ROOMS = ["flopagent", "technocore"]          # 自定义房间 + 官方房间
LOG_PATH = HERE / "heartbeat.log"
MAX_RETRY = 4


def log(msg: str) -> None:
    line = f"{datetime.now(timezone.utc).isoformat()} {msg}"
    print(line, flush=True)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def main() -> int:
    try:
        key = tca.load_identity(KEY_PATH, passphrase=PASSPHRASE.encode("utf-8"), allow_prompt=False)
        did = tca.did_from_private_key(key)
    except Exception as e:
        log(f"LOAD_FAIL {type(e).__name__}: {e}")
        return 1

    ts = int(time.time())
    text = f"heartbeat {ts} DID {did} alive @ zengjingsi/technocore-did-starter"

    results = []
    for room in ROOMS:
        ok = False
        for attempt in range(1, MAX_RETRY + 1):
            try:
                resp = tca.post_signed_message(key, room, text)
                seq = (resp.get("posted") or {}).get("seq")
                log(f"OK {room} seq={seq}")
                results.append(f"{room}:{seq}")
                ok = True
                break
            except Exception as e:
                log(f"RETRY {room} attempt {attempt}/{MAX_RETRY}: {str(e)[:80]}")
                time.sleep(5)
        if not ok:
            log(f"FAIL {room} after {MAX_RETRY} retries")

    log(f"DONE posted={results}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
