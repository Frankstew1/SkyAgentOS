from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from uuid import uuid4

from skyagentos.memory.store import MemoryStore
from skyagentos.models.schemas import Mission
from skyagentos.runtime.orchestrator import Orchestrator


def _store() -> MemoryStore:
    s = MemoryStore(Path(os.getenv("MEMORY_DB_PATH", "/data/memory/skyagentos.db")))
    s.init()
    return s


class MissionHandler(BaseHTTPRequestHandler):
    def _json(self, code: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith("/runs/"):
            run_id = self.path.split("/")[2]
            run = _store().get_run_payload(run_id)
            if not run:
                return self._json(404, {"error": "run not found"})
            return self._json(200, {"run": run, "control": _store().get_run_control(run_id)})
        return self._json(404, {"error": "not found"})

    def do_POST(self):
        if self.path == "/missions":
            return self._create_mission()
        if self.path.startswith("/runs/") and self.path.endswith("/pause"):
            run_id = self.path.split("/")[2]
            _store().set_run_control(run_id, "paused")
            return self._json(200, {"run_id": run_id, "status": "paused"})
        if self.path.startswith("/runs/") and self.path.endswith("/resume"):
            run_id = self.path.split("/")[2]
            _store().set_run_control(run_id, "active")
            return self._json(200, {"run_id": run_id, "status": "active"})
        return self._json(404, {"error": "not found"})

    def _create_mission(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        payload = json.loads(raw)

        objective = payload.get("objective") or "Run default SkyAgentOS mission"
        mission = Mission(
            id=f"mission-{uuid4().hex[:8]}",
            objective=objective,
            domain=payload.get("domain", os.getenv("SKYAGENT_DOMAIN", "general")),
            permissions=payload.get(
                "permissions",
                ["web.browse", "workspace.read", "workspace.write", "desktop.control"],
            ),
            budget_usd=float(payload.get("budget_usd", os.getenv("SKYAGENT_BUDGET_USD", "2.0"))),
            max_steps=int(payload.get("max_steps", os.getenv("MAX_SELF_CORRECTIONS", "3"))),
            metadata=payload.get("metadata", {}),
        )
        orchestrator = Orchestrator(
            db_path=Path(os.getenv("MEMORY_DB_PATH", "/data/memory/skyagentos.db")),
            litellm_base_url=os.getenv("LITELLM_BASE_URL", "http://litellm:4000"),
            litellm_key=os.getenv("LITELLM_MASTER_KEY", "skyagentos-dev-key"),
            skyvern_url=os.getenv("SKYVERN_BASE_URL", "http://skyvern:8000"),
        )
        result = orchestrator.run_mission(mission)
        self._json(200, {"mission_id": mission.id, "result": result})


def run_server() -> None:
    host = os.getenv("ORCHESTRATOR_HOST", "0.0.0.0")
    port = int(os.getenv("ORCHESTRATOR_PORT", "8787"))
    server = ThreadingHTTPServer((host, port), MissionHandler)
    print(f"orchestrator-api listening on {host}:{port}")
    server.serve_forever()
