from services.orchestrator.src.mission.models import MissionState
from services.orchestrator.src.runtime.state_machine import transition


def test_v2_happy_lifecycle():
    s = MissionState.CREATED
    s = transition(s, MissionState.QUEUED)
    s = transition(s, MissionState.PLANNING)
    s = transition(s, MissionState.READY)
    s = transition(s, MissionState.EXECUTING)
    s = transition(s, MissionState.VALIDATING)
    s = transition(s, MissionState.COMPLETED)
    assert s == MissionState.COMPLETED
