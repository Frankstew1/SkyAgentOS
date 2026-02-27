from skyagentos.models.schemas import RunState
from skyagentos.runtime.state_machine import transition


def test_happy_path_transitions():
    s = RunState.CREATED
    s = transition(s, RunState.PLANNED)
    s = transition(s, RunState.EXECUTING)
    s = transition(s, RunState.VALIDATING)
    s = transition(s, RunState.COMPLETED)
    assert s == RunState.COMPLETED
