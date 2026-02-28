from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class JsonModel:
    def model_dump(self) -> dict[str, Any]:
        return asdict(self)

    def model_dump_json(self) -> str:
        return json.dumps(self.model_dump())

    @classmethod
    def model_validate_json(cls, raw: str):
        return cls(**json.loads(raw))


class RunState(str, Enum):
    CREATED = "CREATED"
    PLANNED = "PLANNED"
    EXECUTING = "EXECUTING"
    VALIDATING = "VALIDATING"
    RETRYING = "RETRYING"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ErrorType(str, Enum):
    TOOL_ERROR = "tool_error"
    NETWORK_ERROR = "network_error"
    RATE_LIMITED = "rate_limited"
    VALIDATION_ERROR = "validation_error"
    POLICY_BLOCKED = "policy_blocked"
    BUDGET_EXCEEDED = "budget_exceeded"
    UNKNOWN = "unknown"


@dataclass
class Mission(JsonModel):
    id: str
    objective: str
    domain: str = "general"
    permissions: list[str] = field(
        default_factory=lambda: [
            "web.browse",
            "workspace.read",
            "workspace.write",
            "desktop.control",
        ]
    )
    budget_usd: float = 2.0
    max_steps: int = 8
    template: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class Run(JsonModel):
    id: str
    mission_id: str
    state: RunState = RunState.CREATED
    attempt: int = 0
    cost_usd: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class Step(JsonModel):
    id: str
    run_id: str
    role: str
    action: str
    input: dict[str, Any] = field(default_factory=dict)
    output: dict[str, Any] = field(default_factory=dict)
    state: str = "pending"
    duration_ms: int = 0
    error_type: ErrorType | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class Artifact(JsonModel):
    id: str
    run_id: str
    step_id: str
    kind: str
    path: str
    content_type: str
    checksum: str
    provenance: str = "generated"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class ValidationResult(JsonModel):
    passed: bool = False
    reason: str = ""
    next_action: str = ""


@dataclass
class TelemetryEvent(JsonModel):
    run_id: str
    step_id: str
    name: str
    value: float
    tags: dict[str, str] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
