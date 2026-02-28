from __future__ import annotations

from services.orchestrator.src.mission.models import ValidationV2


class ReflectorAgent:
    def reflect(self, validation: ValidationV2) -> dict:
        return {
            "failure_class": "runtime_error" if not validation.passed else "none",
            "suggestion": validation.repair_suggestion or "none",
        }
