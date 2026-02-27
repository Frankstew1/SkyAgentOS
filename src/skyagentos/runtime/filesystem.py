from __future__ import annotations

import json
import os
from pathlib import Path


class AgentFilesystem:
    """Logical agent filesystem semantics for per-run data isolation."""

    def __init__(self, root: str | None = None):
        self.root = Path(root or os.getenv("AGENT_FS_ROOT", "agentfs"))
        self.root.mkdir(parents=True, exist_ok=True)

    def init_run(self, run_id: str) -> dict[str, Path]:
        base = self.root / "missions" / run_id
        paths = {
            "base": base,
            "inputs": base / "inputs",
            "outputs": base / "outputs",
            "artifacts": base / "artifacts",
            "logs": base / "logs",
            "evals": base / "evals",
            "memory": base / "memory",
        }
        for p in paths.values():
            p.mkdir(parents=True, exist_ok=True)
        return paths

    def write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
