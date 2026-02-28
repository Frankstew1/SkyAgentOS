from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any
from urllib import request

from skyagentos.models.schemas import Artifact


class SkyvernTool:
    """Skyvern API client aligned to run-task contract (prompt-first payload)."""

    def __init__(self, base_url: str, artifact_dir: Path):
        self.base_url = base_url.rstrip("/")
        self.task_endpoint = os.getenv("SKYVERN_TASK_ENDPOINT", "/api/v1/tasks")
        self.api_key = os.getenv("SKYVERN_API_KEY", "")
        self.artifact_dir = artifact_dir
        self.artifact_dir.mkdir(parents=True, exist_ok=True)

    def execute(self, run_id: str, step_id: str, payload: dict[str, Any]) -> tuple[dict[str, Any], Artifact]:
        """Execute task with documented fields: prompt (+ compatible optional params)."""
        normalized = {
            "prompt": payload.get("prompt") or payload.get("goal") or "",
            "url": payload.get("url"),
            "engine": payload.get("engine"),
            "metadata": payload.get("metadata", {}),
        }
        normalized = {k: v for k, v in normalized.items() if v not in (None, "")}

        if os.getenv("SKYAGENT_DRY_RUN", "false").lower() == "true":
            result = {
                "status": "ok",
                "run_id": f"dry-{step_id}",
                "task_id": f"dry-task-{step_id}",
                "summary": "Simulated Skyvern run for demo/testing",
                "evidence": ["https://example.com"],
                "request": normalized,
            }
        else:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["x-api-key"] = self.api_key
            req = request.Request(
                f"{self.base_url}{self.task_endpoint}",
                data=json.dumps(normalized).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with request.urlopen(req, timeout=180) as resp:
                result = json.loads(resp.read().decode("utf-8"))

        artifact_path = self.artifact_dir / f"{run_id}_{step_id}_skyvern.json"
        artifact_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        digest = hashlib.sha256(artifact_path.read_bytes()).hexdigest()

        artifact = Artifact(
            id=f"artifact-{step_id}",
            run_id=run_id,
            step_id=step_id,
            kind="browser_trace",
            path=str(artifact_path),
            content_type="application/json",
            checksum=digest,
        )
        return result, artifact
