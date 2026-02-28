from __future__ import annotations


class BrowserSessionManager:
    def execute(self, action: str, payload: dict) -> dict:
        return {
            "status": "ok",
            "runtime": "browser",
            "action": action,
            "dom_snapshot": "dom.json",
            "har": "network.har",
            "target": payload.get("objective", "unknown"),
        }
