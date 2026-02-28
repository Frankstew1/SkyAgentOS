from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AgentSpec:
    role: str
    model: str
    capability: str


SPECIALISTS = [
    AgentSpec(role="manager", model="manager", capability="deep-reasoning"),
    AgentSpec(role="planner", model="planner", capability="planning"),
    AgentSpec(role="vision_executor", model="vision_executor", capability="web-automation"),
    AgentSpec(role="desktop_executor", model="local_reflector", capability="desktop-computer-use"),
    AgentSpec(role="validator", model="local_reflector", capability="fast-json-validation"),
    AgentSpec(role="extractor", model="local_reflector", capability="artifact-structuring"),
]
