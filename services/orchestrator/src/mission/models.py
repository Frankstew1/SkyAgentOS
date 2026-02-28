from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class MissionState(str, Enum):
    CREATED = "CREATED"
    QUEUED = "QUEUED"
    PLANNING = "PLANNING"
    READY = "READY"
    EXECUTING = "EXECUTING"
    VALIDATING = "VALIDATING"
    RETRYING = "RETRYING"
    WAITING_FOR_HUMAN = "WAITING_FOR_HUMAN"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"


@dataclass
class MissionV2:
    mission_id: str
    objective: str
    project_id: str = "default"
    policy_profile: str = "Safe Research"
    runtime_preferences: list[str] = field(
        default_factory=lambda: ["browser", "desktop", "workspace", "tools"]
    )
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class StepV2:
    step_id: str
    mission_id: str
    runtime: str
    action: str
    input: dict[str, Any] = field(default_factory=dict)
    output: dict[str, Any] = field(default_factory=dict)
    attempt: int = 1
    state: str = "pending"


@dataclass
class ValidationV2:
    passed: bool
    reason: str
    repair_suggestion: str = ""
