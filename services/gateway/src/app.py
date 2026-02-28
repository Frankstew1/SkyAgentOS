"""Gateway stub: auth/session/rate-limit ingress boundary for SkyAgentOS."""

from __future__ import annotations


def health() -> dict:
    return {"service": "gateway", "status": "ok"}
