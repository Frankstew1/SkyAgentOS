"""SkyAgentOS orchestrator.

Implements a CrewAI-powered ResearchCrew with sequential planner -> executor ->
validator loops, AutoGPT-style self-correction, and shared SQLite memory.
"""

from __future__ import annotations

import json
import os
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from crewai import Agent, Crew, Process, Task
from crewai.llm import LLM
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

MEMORY_DB_PATH = Path(os.getenv("MEMORY_DB_PATH", "/data/memory/skyagentos.db"))
LITELLM_BASE_URL = os.getenv("LITELLM_BASE_URL", "http://litellm:4000")
SKYVERN_BASE_URL = os.getenv("SKYVERN_BASE_URL", "http://skyvern:8000")
MAX_SELF_CORRECTIONS = int(os.getenv("MAX_SELF_CORRECTIONS", "3"))


class SkyvernPayload(BaseModel):
    goal: str = Field(..., description="Clear web automation objective")
    url: str | None = Field(default=None, description="Optional starting URL")
    success_criteria: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ValidationResult(BaseModel):
    passed: bool = Field(default=False)
    reason: str = Field(default="")
    next_action: str = Field(default="")


class SkyvernTool(BaseTool):
    name: str = "skyvern_executor"
    description: str = "Execute a structured browser task against Skyvern API"

    def _run(self, payload: str) -> str:
        parsed = SkyvernPayload.model_validate_json(payload)
        response = requests.post(
            f"{SKYVERN_BASE_URL}/api/v1/tasks",
            json={
                "goal": parsed.goal,
                "url": parsed.url,
                "success_criteria": parsed.success_criteria,
                "metadata": parsed.metadata,
                "llm_model": "vision_executor",
            },
            timeout=180,
        )
        response.raise_for_status()
        return json.dumps(response.json())


@dataclass
class MemoryStore:
    db_path: Path

    def init(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS run_journal (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  run_id TEXT NOT NULL,
                  stage TEXT NOT NULL,
                  payload TEXT NOT NULL,
                  created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS vector_memory (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  namespace TEXT NOT NULL,
                  key TEXT NOT NULL,
                  value TEXT NOT NULL,
                  embedding TEXT,
                  created_at TEXT NOT NULL
                )
                """
            )

    def append_journal(self, run_id: str, stage: str, payload: dict[str, Any]) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO run_journal (run_id, stage, payload, created_at) VALUES (?, ?, ?, ?)",
                (run_id, stage, json.dumps(payload), datetime.now(timezone.utc).isoformat()),
            )


def mk_llm(model_name: str) -> LLM:
    return LLM(
        model=model_name,
        base_url=f"{LITELLM_BASE_URL}/v1",
        api_key=os.getenv("LITELLM_MASTER_KEY", "skyagentos-dev-key"),
        temperature=0.2,
    )


def parse_validation_json(raw: str) -> ValidationResult:
    try:
        return ValidationResult.model_validate_json(raw)
    except Exception:
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            return ValidationResult.model_validate_json(raw[start : end + 1])
        return ValidationResult(passed=False, reason="Validator output was not JSON", next_action="Retry")


def build_research_crew() -> Crew:
    manager = Agent(
        role="Manager",
        goal="Oversee quality and coordinate the crew.",
        backstory=(
            "High-reasoning manager authenticated with OpenAI/Codex CLI-linked "
            "credentials for escalation decisions."
        ),
        llm=mk_llm("manager"),
        allow_delegation=True,
        verbose=True,
    )

    planner = Agent(
        role="Planner",
        goal="Build an actionable plan and success criteria.",
        llm=mk_llm("planner"),
        verbose=True,
    )

    executor = Agent(
        role="Vision Executor",
        goal="Execute web tasks with the Skyvern tool.",
        llm=mk_llm("vision_executor"),
        tools=[SkyvernTool()],
        verbose=True,
    )

    validator = Agent(
        role="Validator",
        goal="Validate outputs and produce deterministic correction signals.",
        llm=mk_llm("local_reflector"),
        verbose=True,
    )

    return Crew(
        agents=[manager, planner, executor, validator],
        process=Process.sequential,
        verbose=True,
    )


def run(objective: str) -> dict[str, Any]:
    run_id = f"run-{int(time.time())}"
    memory = MemoryStore(MEMORY_DB_PATH)
    memory.init()

    crew = build_research_crew()
    memory.append_journal(run_id, "objective", {"objective": objective})

    plan_task = Task(
        description=f"Create a concise plan and numbered success criteria for: {objective}",
        expected_output="Plan text with measurable success criteria.",
        agent=crew.agents[1],
    )

    plan_text = str(crew.kickoff(tasks=[plan_task]))
    memory.append_journal(run_id, "plan", {"text": plan_text})

    current_objective = objective
    final_status: dict[str, Any] = {"run_id": run_id, "status": "needs_review"}

    for iteration in range(1, MAX_SELF_CORRECTIONS + 1):
        execute_task = Task(
            description=(
                "Use skyvern_executor with JSON payload. "
                f"Goal: {current_objective}. Include success criteria from plan: {plan_text}"
            ),
            expected_output="Skyvern execution JSON output.",
            agent=crew.agents[2],
        )

        validate_task = Task(
            description=(
                "Evaluate execution. Return strict JSON only with keys: "
                "passed (bool), reason (str), next_action (str)."
            ),
            expected_output='{"passed": true|false, "reason": "...", "next_action": "..."}',
            agent=crew.agents[3],
            context=[execute_task],
        )

        validation_raw = str(crew.kickoff(tasks=[execute_task, validate_task]))
        validation = parse_validation_json(validation_raw)

        memory.append_journal(
            run_id,
            f"iteration_{iteration}",
            {
                "objective": current_objective,
                "validation": validation.model_dump(),
                "raw": validation_raw,
            },
        )

        if validation.passed:
            final_status = {
                "run_id": run_id,
                "status": "completed",
                "iterations": iteration,
                "validation": validation.model_dump(),
            }
            break

        current_objective = (
            f"{objective}\nSelf-correction {iteration}: "
            f"{validation.next_action or validation.reason or 'Refine approach and retry.'}"
        )

    memory.append_journal(run_id, "final", final_status)
    return final_status


if __name__ == "__main__":
    objective = os.getenv(
        "SKYAGENT_OBJECTIVE",
        "Research cloud GPU pricing trends and produce a sourced summary",
    )
    print(json.dumps(run(objective), indent=2))
