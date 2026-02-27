from __future__ import annotations

from services.orchestrator.src.mission.models import StepV2, ValidationV2


class ValidatorAgent:
    def validate(self, step: StepV2) -> ValidationV2:
        if step.output.get("status") == "ok":
            return ValidationV2(passed=True, reason="step succeeded")
        return ValidationV2(passed=False, reason="step failed", repair_suggestion="retry with fallback runtime")
