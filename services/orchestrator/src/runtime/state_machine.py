from __future__ import annotations

from services.orchestrator.src.mission.models import MissionState

ALLOWED: dict[MissionState, set[MissionState]] = {
    MissionState.CREATED: {MissionState.QUEUED, MissionState.CANCELED},
    MissionState.QUEUED: {MissionState.PLANNING, MissionState.CANCELED, MissionState.FAILED},
    MissionState.PLANNING: {
        MissionState.READY,
        MissionState.FAILED,
        MissionState.WAITING_FOR_HUMAN,
    },
    MissionState.READY: {MissionState.EXECUTING, MissionState.CANCELED},
    MissionState.EXECUTING: {
        MissionState.VALIDATING,
        MissionState.RETRYING,
        MissionState.FAILED,
        MissionState.WAITING_FOR_HUMAN,
    },
    MissionState.VALIDATING: {
        MissionState.COMPLETED,
        MissionState.RETRYING,
        MissionState.FAILED,
        MissionState.WAITING_FOR_HUMAN,
    },
    MissionState.RETRYING: {
        MissionState.EXECUTING,
        MissionState.WAITING_FOR_HUMAN,
        MissionState.FAILED,
    },
    MissionState.WAITING_FOR_HUMAN: {
        MissionState.EXECUTING,
        MissionState.CANCELED,
        MissionState.FAILED,
        MissionState.COMPLETED,
    },
    MissionState.COMPLETED: set(),
    MissionState.FAILED: set(),
    MissionState.CANCELED: set(),
}


def transition(current: MissionState, nxt: MissionState) -> MissionState:
    if nxt not in ALLOWED[current]:
        raise ValueError(f"invalid transition {current} -> {nxt}")
    return nxt
