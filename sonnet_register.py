#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sonnet-2 writer/voter registration retrier.

Referee currently returns 'identity: verified pre-start evidence required' for all
(unverified archive). Rule says: retry after evidence reaches the referee.
This module is called by the heartbeat scheduler every cycle; it re-signs the
same registration (stable request_id) until an accepted receipt appears.

Per rules: identical retry request_id returns the original receipt; keep it stable.
"""
import json, time, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import technocore_agent as tca

KEY_PATH = HERE / "identity.pem"
PW = "7iuYnHekdEVyRKiOy82chbGTIXh9"
ROOM = "mb-sonnet-2-registration"
REF = "did:key:z6MkowHQwsx9xr84WbWN3YCnKutyBnBXkT1ChKY4uEAAMzte"
REQUEST_ID = "zengjingsi-register-1"
DID = "did:key:z6MkuXQQJ1D2QAqKDfAosPYRyeVW8daob9LGoCZJPUpfjoDK"


def already_accepted() -> bool:
    """Check if referee has issued an accepted receipt for our DID/request_id."""
    try:
        r = tca.read_room(ROOM, limit=200)
        for m in r.get("messages", []):
            if REF in str(m.get("from", "")):
                t = str(m.get("text", ""))
                if REQUEST_ID in t or DID in t:
                    try:
                        o = json.loads(t)
                        if o.get("reason") in ("accepted", "ok", "registered"):
                            return True
                    except Exception:
                        pass
    except Exception:
        pass
    return False


def register_once() -> None:
    reg = {
        "type": "sonnet.register.v1",
        "contest_id": "sonnet-2",
        "role": "voter",
        "request_id": REQUEST_ID,
    }
    text = json.dumps(reg, ensure_ascii=False, separators=(",", ":"))
    key = tca.load_identity(KEY_PATH, passphrase=PW.encode("utf-8"), allow_prompt=False)
    for attempt in range(4):
        try:
            r = tca.post_signed_message(key, ROOM, text)
            print(f"[register] posted seq={(r.get('posted') or {}).get('seq')}")
            return
        except Exception as e:
            print(f"[register] attempt {attempt+1} err: {str(e)[:70]}")
            time.sleep(5)


def main() -> None:
    if already_accepted():
        print("[register] already accepted — skip")
        return
    register_once()


if __name__ == "__main__":
    main()
