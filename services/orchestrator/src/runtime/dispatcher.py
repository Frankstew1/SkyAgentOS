from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from services.orchestrator.src.mission.models import StepV2


class RuntimeClient(Protocol):
    def execute(self, action: str, payload: dict) -> dict: ...


@dataclass
class Dispatcher:
    browser_worker: RuntimeClient
    desktop_worker: RuntimeClient
    workspace_worker: RuntimeClient
    tool_worker: RuntimeClient

    def dispatch(self, step: StepV2) -> dict:
        if step.runtime == "browser":
            return self.browser_worker.execute(step.action, step.input)
        if step.runtime == "desktop":
            return self.desktop_worker.execute(step.action, step.input)
        if step.runtime == "workspace":
            return self.workspace_worker.execute(step.action, step.input)
        if step.runtime == "tools":
            return self.tool_worker.execute(step.action, step.input)
        raise ValueError(f"unknown runtime: {step.runtime}")
