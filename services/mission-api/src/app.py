"""Mission API stub: create/pause/resume/cancel/list missions."""

from __future__ import annotations


def capabilities() -> dict:
    return {
        "service": "mission-api",
        "endpoints": ["POST /missions", "POST /runs/{id}/pause", "POST /runs/{id}/resume", "POST /runs/{id}/cancel", "GET /missions"],
    }
