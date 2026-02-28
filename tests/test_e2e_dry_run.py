import os
import sqlite3
from pathlib import Path

from skyagentos.models.schemas import Mission
from skyagentos.runtime.orchestrator import Orchestrator


def test_e2e_dry_run_persists_executor_and_validator_steps(tmp_path: Path):
    os.environ["SKYAGENT_DRY_RUN"] = "true"
    db = tmp_path / "demo.db"
    orchestrator = Orchestrator(
        db_path=db,
        litellm_base_url="http://litellm:4000",
        litellm_key="dev",
        skyvern_url="http://skyvern:8000",
    )
    mission = Mission(id="m1", objective="Research test objective", max_steps=2)
    result = orchestrator.run_mission(mission)
    assert result["state"] in {"COMPLETED", "HUMAN_REVIEW", "FAILED"}

    with sqlite3.connect(db) as conn:
        roles = [r[0] for r in conn.execute("SELECT role FROM steps").fetchall()]
    assert any(r.endswith("_executor") for r in roles)
    assert "validator" in roles
