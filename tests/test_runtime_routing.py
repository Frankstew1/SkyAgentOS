from pathlib import Path

from skyagentos.models.schemas import Mission
from skyagentos.runtime.orchestrator import Orchestrator


def test_runtime_selection_prefers_desktop_metadata(tmp_path: Path):
    orch = Orchestrator(tmp_path / "r.db", "http://litellm:4000", "dev", "http://skyvern:8000")
    m = Mission(id="m1", objective="research", metadata={"runtime": "desktop"})
    assert orch._select_runtime(m) == "desktop"


def test_runtime_selection_infers_desktop_from_objective(tmp_path: Path):
    orch = Orchestrator(tmp_path / "r2.db", "http://litellm:4000", "dev", "http://skyvern:8000")
    m = Mission(id="m2", objective="Open Excel and update spreadsheet totals")
    assert orch._select_runtime(m) == "desktop"
