from __future__ import annotations

from skyagentos.models.schemas import RunState

TRANSITIONS: dict[RunState, set[RunState]] = {
    RunState.CREATED: {RunState.PLANNED, RunState.FAILED},
    RunState.PLANNED: {RunState.EXECUTING, RunState.FAILED},
    RunState.EXECUTING: {RunState.VALIDATING, RunState.RETRYING, RunState.FAILED},
    RunState.VALIDATING: {
        RunState.COMPLETED,
        RunState.RETRYING,
        RunState.HUMAN_REVIEW,
        RunState.FAILED,
    },
    RunState.RETRYING: {RunState.EXECUTING, RunState.HUMAN_REVIEW, RunState.FAILED},
    RunState.HUMAN_REVIEW: {RunState.EXECUTING, RunState.FAILED, RunState.COMPLETED},
    RunState.COMPLETED: set(),
    RunState.FAILED: set(),
}


def can_transition(current: RunState, nxt: RunState) -> bool:
    return nxt in TRANSITIONS[current]


def transition(current: RunState, nxt: RunState) -> RunState:
    if not can_transition(current, nxt):
        raise ValueError(f"Invalid run transition {current} -> {nxt}")
    return nxt
