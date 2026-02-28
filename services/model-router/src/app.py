"""Model router stub: provider abstraction and budget controls."""

from __future__ import annotations


def roles() -> dict:
    return {
        "router-small-local": "classification",
        "planner-strong": "decomposition",
        "validator-json": "strict-json",
        "reflector-local": "repair",
    }
