import json
import os
import threading
import time
from urllib import request

from skyagentos.api.server import run_server


def _post(url: str, payload: dict | None = None) -> dict:
    req = request.Request(
        url,
        data=json.dumps(payload or {}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get(url: str) -> dict:
    with request.urlopen(url, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def test_api_server_accepts_mission_and_run_controls(tmp_path):
    os.environ["SKYAGENT_DRY_RUN"] = "true"
    os.environ["ORCHESTRATOR_HOST"] = "127.0.0.1"
    os.environ["ORCHESTRATOR_PORT"] = "18787"
    os.environ["MEMORY_DB_PATH"] = str(tmp_path / "api.db")

    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    time.sleep(0.25)

    created = _post("http://127.0.0.1:18787/missions", {"objective": "API mission"})
    assert "result" in created
    run_id = created["result"]["run_id"]

    paused = _post(f"http://127.0.0.1:18787/runs/{run_id}/pause")
    assert paused["status"] == "paused"

    resumed = _post(f"http://127.0.0.1:18787/runs/{run_id}/resume")
    assert resumed["status"] == "active"

    status = _get(f"http://127.0.0.1:18787/runs/{run_id}")
    assert status["control"] == "active"
