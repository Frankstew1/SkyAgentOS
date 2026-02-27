from __future__ import annotations


def execute(op: str, path: str) -> dict:
    return {"status": "ok", "runtime": "file", "operation": op, "path": path}
