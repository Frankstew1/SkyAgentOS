from __future__ import annotations


def execute(action: str, payload: dict) -> dict:
    return {"status": "ok", "runtime": "tools", "action": action, "payload": payload}
