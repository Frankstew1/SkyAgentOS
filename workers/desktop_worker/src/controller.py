from __future__ import annotations


class DesktopController:
    def execute(self, action: str, payload: dict) -> dict:
        return {
            "status": "ok",
            "runtime": "desktop",
            "action": action,
            "before_screenshot": "desktop_before.png",
            "after_screenshot": "desktop_after.png",
            "target": payload.get("objective", "unknown"),
            "confidence": 0.9,
        }
