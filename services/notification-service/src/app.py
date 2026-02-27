"""Notification service stub: push run updates to channels."""

from __future__ import annotations


def channels() -> list[str]:
    return ["websocket", "telegram", "whatsapp", "email"]
