"""Scheduler stub: recurring jobs and delayed tasks."""

from __future__ import annotations


def jobs() -> list[str]:
    return ["nightly-index", "retention-cleanup", "model-health-check"]
