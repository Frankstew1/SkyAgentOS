from __future__ import annotations

from services.orchestrator.src.mission.models import MissionV2, StepV2


class PlannerAgent:
    def plan(self, mission: MissionV2) -> list[StepV2]:
        text = mission.objective.lower()
        runtime = "desktop" if any(x in text for x in ["excel", "desktop", "file", "folder", "clipboard"]) else "browser"
        return [
            StepV2(step_id=f"{mission.mission_id}-step-1", mission_id=mission.mission_id, runtime=runtime, action="execute_primary", input={"objective": mission.objective}),
            StepV2(step_id=f"{mission.mission_id}-step-2", mission_id=mission.mission_id, runtime="workspace", action="summarize_outputs", input={"format": "report"}),
        ]
