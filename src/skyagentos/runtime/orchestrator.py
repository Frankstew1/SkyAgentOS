from __future__ import annotations

import json
import os
import time
from pathlib import Path
from uuid import uuid4

from skyagentos.agents.specialists import SPECIALISTS
from skyagentos.memory.retrieval import episodic_summary, semantic_rank
from skyagentos.memory.store import MemoryStore
from skyagentos.models.schemas import ErrorType, Mission, Run, RunState, Step, TelemetryEvent, ValidationResult
from skyagentos.runtime.filesystem import AgentFilesystem
from skyagentos.runtime.model_router import ModelRouter
from skyagentos.runtime.policies import check_permissions, requires_human_review
from skyagentos.runtime.retry import RetryPolicy, classify_error, retry_sleep
from skyagentos.runtime.state_machine import transition
from skyagentos.runtime.stream import StreamFn, default_stream
from skyagentos.tools.desktop_tool import DesktopTool
from skyagentos.tools.skyvern_tool import SkyvernTool


class Orchestrator:
    def __init__(self, db_path: Path, litellm_base_url: str, litellm_key: str, skyvern_url: str, stream_fn: StreamFn = default_stream):
        self.store = MemoryStore(db_path)
        self.store.init()
        self.router = ModelRouter(
            litellm_base_url,
            litellm_key,
            budget_usd=float(os.getenv("SKYAGENT_BUDGET_USD", "10.0")),
        )
        self.skyvern = SkyvernTool(skyvern_url, artifact_dir=Path("workspace_artifacts/browser"))
        self.desktop = DesktopTool(os.getenv("DESKTOP_DAEMON_URL", "http://desktop-daemon:8890"), artifact_dir=Path("workspace_artifacts/desktop"))
        self.retry = RetryPolicy(max_attempts=int(os.getenv("MAX_SELF_CORRECTIONS", "3")))
        self.stream = stream_fn
        self.fs = AgentFilesystem()

    def run_mission(self, mission: Mission) -> dict:
        run = Run(id=f"run-{uuid4().hex[:8]}", mission_id=mission.id)
        self.store.save_mission(mission)
        self.store.save_run(run)
        self.store.set_run_control(run.id, "active")
        self.store.enqueue(run.id, mission.model_dump())
        self.stream("progress", {"run_id": run.id, "state": run.state.value})

        queue_job = self.store.dequeue()
        if not queue_job:
            raise RuntimeError("queue is empty")
        job_id, _, _ = queue_job

        try:
            return self._execute_run(run, mission)
        finally:
            self.store.ack(job_id)

    def _select_runtime(self, mission: Mission) -> str:
        forced = mission.metadata.get("runtime") if mission.metadata else None
        if forced in {"browser", "desktop", "workspace"}:
            return forced
        objective = mission.objective.lower()
        desktop_hints = ["excel", "desktop", "local app", "clipboard", "file explorer", "terminal"]
        if any(h in objective for h in desktop_hints):
            return "desktop"
        return "browser"

    def _execute_run(self, run: Run, mission: Mission) -> dict:
        run_paths = self.fs.init_run(run.id)
        self.fs.write_json(run_paths["inputs"] / "mission.json", mission.model_dump())

        if requires_human_review(mission):
            run.state = RunState.HUMAN_REVIEW
            self.store.save_run(run)
            return {"run_id": run.id, "state": run.state.value, "reason": "domain requires human review"}

        runtime = self._select_runtime(mission)
        required_perm = "desktop.control" if runtime == "desktop" else "web.browse"
        check_permissions(mission, [required_perm])

        run.state = transition(run.state, RunState.PLANNED)
        self.store.save_run(run)

        episodic = self.store.read_memory("episodic_memory", mission.domain, limit=20)
        semantic = self.store.read_memory("semantic_memory", mission.domain, limit=50)
        retrieved = semantic_rank(mission.objective, semantic)[:3]

        plan_prompt = (
            f"You are planner. Runtime={runtime}. Objective: {mission.objective}\n"
            f"Prior failures summary: {episodic_summary(episodic)}\n"
            f"Relevant memory: {retrieved}\n"
            "Return concise numbered plan + success criteria."
        )
        plan = self.router.complete("planner", plan_prompt)
        self.store.push_episodic(mission.domain, f"plan:{plan[:300]}")

        run.state = transition(run.state, RunState.EXECUTING)
        self.store.save_run(run)

        for i in range(1, mission.max_steps + 1):
            if self.store.get_run_control(run.id) == "paused":
                run.state = RunState.HUMAN_REVIEW
                self.store.save_run(run)
                return {"run_id": run.id, "state": run.state.value, "reason": "paused by operator"}

            exec_step = Step(
                id=f"step-{i}-executor",
                run_id=run.id,
                role=f"{runtime}_executor",
                action=f"{runtime}.execute",
                input={"objective": mission.objective, "iteration": i, "runtime": runtime},
            )
            start = time.time()
            try:
                if runtime == "desktop":
                    result, artifact = self.desktop.execute(run.id, exec_step.id, "operate", {"prompt": mission.objective, "iteration": i})
                else:
                    payload = {
                        "prompt": mission.objective,
                        "url": mission.metadata.get("url") if mission.metadata else None,
                        "engine": os.getenv("SKYVERN_ENGINE", "browser"),
                        "metadata": {"run_id": run.id, "iteration": i, "runtime": runtime},
                    }
                    result, artifact = self.skyvern.execute(run.id, exec_step.id, payload)

                exec_step.output = result
                exec_step.state = "ok"
                exec_step.duration_ms = int((time.time() - start) * 1000)
                self.store.save_step(exec_step)
                self.store.save_artifact(artifact)
                self.fs.write_json(run_paths["artifacts"] / f"{exec_step.id}.json", result)
                self.store.save_telemetry(
                    TelemetryEvent(
                        run_id=run.id,
                        step_id=exec_step.id,
                        name=f"{runtime}_call_ms",
                        value=float(exec_step.duration_ms),
                        tags={"iteration": str(i), "run_state": run.state.value, "runtime": runtime},
                    )
                )

                run.state = transition(run.state, RunState.VALIDATING)
                self.store.save_run(run)

                val_step = Step(
                    id=f"step-{i}-validator",
                    run_id=run.id,
                    role="validator",
                    action="validate.execution",
                    input={"plan": plan, "execution_result": result, "runtime": runtime},
                )
                vstart = time.time()
                validate_prompt = (
                    "Return strict JSON only: {passed:boolean,reason:string,next_action:string}.\n"
                    f"Plan:{plan}\nRuntime:{runtime}\nExecution:{json.dumps(result)[:1800]}"
                )
                raw = self.router.complete("validator", validate_prompt)
                parsed = self._parse_validation(raw)
                val_step.output = {"raw": raw, "parsed": parsed.model_dump()}
                val_step.state = "ok"
                val_step.duration_ms = int((time.time() - vstart) * 1000)
                self.store.save_step(val_step)
                self.fs.write_json(run_paths["logs"] / f"{val_step.id}.json", val_step.output)
                self.store.save_telemetry(
                    TelemetryEvent(
                        run_id=run.id,
                        step_id=val_step.id,
                        name="validation_ms",
                        value=float(val_step.duration_ms),
                        tags={"passed": str(parsed.passed).lower(), "iteration": str(i), "runtime": runtime},
                    )
                )
                self.store.push_semantic(mission.domain, json.dumps(result)[:500], embedding_hint=f"{runtime}-result")

                if parsed.passed:
                    run.state = transition(run.state, RunState.COMPLETED)
                    self.store.save_run(run)
                    outcome = {
                        "run_id": run.id,
                        "state": run.state.value,
                        "step": i,
                        "runtime": runtime,
                        "executor_run_id": result.get("run_id") or result.get("task_id"),
                        "artifact": artifact.path,
                        "validation": parsed.model_dump(),
                    }
                    self.fs.write_json(run_paths["outputs"] / "result.json", outcome)
                    self.stream("progress", {"run_id": run.id, "state": run.state.value, "step": i, "runtime": runtime})
                    return outcome

                run.state = transition(run.state, RunState.RETRYING)
                self.store.save_run(run)
                self.store.push_episodic(mission.domain, f"failure:{parsed.reason}")
                self.stream("progress", {"run_id": run.id, "state": run.state.value, "reason": parsed.reason})

                if i >= self.retry.max_attempts:
                    run.state = transition(run.state, RunState.HUMAN_REVIEW)
                    self.store.save_run(run)
                    return {"run_id": run.id, "state": run.state.value, "reason": parsed.reason}

                run.state = transition(run.state, RunState.EXECUTING)
                self.store.save_run(run)
                retry_sleep(self.retry, i)
            except Exception as exc:
                et = classify_error(exc)
                exec_step.error_type = et
                exec_step.state = "error"
                exec_step.duration_ms = int((time.time() - start) * 1000)
                self.store.save_step(exec_step)
                self.store.save_telemetry(
                    TelemetryEvent(run_id=run.id, step_id=exec_step.id, name="step_error", value=1.0, tags={"type": et.value, "runtime": runtime})
                )
                if et == ErrorType.BUDGET_EXCEEDED or i >= self.retry.max_attempts:
                    run.state = RunState.FAILED
                    self.store.save_run(run)
                    return {"run_id": run.id, "state": run.state.value, "error": et.value}
                retry_sleep(self.retry, i)

        run.state = RunState.FAILED
        self.store.save_run(run)
        return {"run_id": run.id, "state": run.state.value, "error": "max steps exceeded"}

    @staticmethod
    def _parse_validation(raw: str) -> ValidationResult:
        try:
            return ValidationResult.model_validate_json(raw)
        except Exception:
            i, j = raw.find("{"), raw.rfind("}")
            if i >= 0 and j > i:
                try:
                    return ValidationResult.model_validate_json(raw[i : j + 1])
                except Exception:
                    pass
        return ValidationResult(passed=False, reason="validation parsing failed", next_action="retry")


def specialist_catalog() -> list[dict[str, str]]:
    return [s.__dict__ for s in SPECIALISTS]
