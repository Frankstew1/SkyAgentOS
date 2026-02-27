from __future__ import annotations

import json
import os
from pathlib import Path
from urllib import request

from skyagentos.models.schemas import Artifact


class DesktopTool:
    def __init__(self, base_url: str, artifact_dir: Path):
        self.base_url = base_url.rstrip("/")
        self.artifact_dir = artifact_dir
        self.artifact_dir.mkdir(parents=True, exist_ok=True)

    def execute(self, run_id: str, step_id: str, action: str, payload: dict) -> tuple[dict, Artifact]:
        body = {"action": action, "payload": payload}
        if os.getenv("SKYAGENT_DRY_RUN", "false").lower() == "true":
            result = {"status": "ok", "runtime": "desktop", "action": action, "result": "simulated"}
        else:
            req = request.Request(
                f"{self.base_url}/execute",
                data=json.dumps(body).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read().decode("utf-8"))

        path = self.artifact_dir / f"{run_id}_{step_id}_desktop.json"
        path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        artifact = Artifact(
            id=f"artifact-{step_id}",
            run_id=run_id,
            step_id=step_id,
            kind="desktop_trace",
            path=str(path),
            content_type="application/json",
            checksum=str(path.stat().st_size),
        )
        return result, artifact
