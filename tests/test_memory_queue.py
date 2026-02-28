from pathlib import Path

from skyagentos.memory.store import MemoryStore


def test_queue_roundtrip(tmp_path: Path):
    db = tmp_path / "test.db"
    store = MemoryStore(db)
    store.init()
    store.enqueue("run-1", {"x": 1})
    item = store.dequeue()
    assert item is not None
    job_id, run_id, payload = item
    assert run_id == "run-1"
    assert payload["x"] == 1
    store.ack(job_id)
