from __future__ import annotations

import json
from pathlib import Path


class ArtifactStore:
    def __init__(self, root: str = "artifacts"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def write(self, mission_id: str, step_id: str, payload: dict) -> str:
        path = self.root / mission_id / f"{step_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return str(path)
