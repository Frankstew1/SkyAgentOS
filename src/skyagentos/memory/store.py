from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from skyagentos.models.schemas import Artifact, Mission, Run, Step, TelemetryEvent


class MemoryStore:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def init(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS missions (id TEXT PRIMARY KEY, payload TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, mission_id TEXT NOT NULL, state TEXT NOT NULL, payload TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS steps (id TEXT PRIMARY KEY, run_id TEXT NOT NULL, role TEXT NOT NULL, action TEXT NOT NULL, payload TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS artifacts (id TEXT PRIMARY KEY, run_id TEXT NOT NULL, step_id TEXT NOT NULL, payload TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS queue_jobs (id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL, payload TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'queued');
                CREATE TABLE IF NOT EXISTS telemetry (id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL, step_id TEXT NOT NULL, name TEXT NOT NULL, value REAL NOT NULL, tags TEXT NOT NULL, created_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS episodic_memory (id INTEGER PRIMARY KEY AUTOINCREMENT, namespace TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
                CREATE TABLE IF NOT EXISTS semantic_memory (id INTEGER PRIMARY KEY AUTOINCREMENT, namespace TEXT NOT NULL, content TEXT NOT NULL, embedding_hint TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
                CREATE TABLE IF NOT EXISTS run_controls (run_id TEXT PRIMARY KEY, status TEXT NOT NULL, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
                """
            )

    def save_mission(self, mission: Mission) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT OR REPLACE INTO missions (id,payload) VALUES (?,?)", (mission.id, mission.model_dump_json()))

    def save_run(self, run: Run) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO runs (id, mission_id, state, payload) VALUES (?,?,?,?)",
                (run.id, run.mission_id, run.state.value, run.model_dump_json()),
            )

    def get_run_payload(self, run_id: str) -> dict[str, Any] | None:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT payload FROM runs WHERE id=?", (run_id,)).fetchone()
        return json.loads(row[0]) if row else None

    def save_step(self, step: Step) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO steps (id, run_id, role, action, payload) VALUES (?,?,?,?,?)",
                (step.id, step.run_id, step.role, step.action, step.model_dump_json()),
            )

    def save_artifact(self, artifact: Artifact) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO artifacts (id, run_id, step_id, payload) VALUES (?,?,?,?)",
                (artifact.id, artifact.run_id, artifact.step_id, artifact.model_dump_json()),
            )

    def save_telemetry(self, event: TelemetryEvent) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO telemetry (run_id, step_id, name, value, tags, created_at) VALUES (?,?,?,?,?,?)",
                (event.run_id, event.step_id, event.name, event.value, json.dumps(event.tags), event.created_at),
            )

    def enqueue(self, run_id: str, payload: dict[str, Any]) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO queue_jobs (run_id, payload, state) VALUES (?,?,'queued')", (run_id, json.dumps(payload)))

    def dequeue(self) -> tuple[int, str, dict[str, Any]] | None:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT id, run_id, payload FROM queue_jobs WHERE state='queued' ORDER BY id LIMIT 1"
            ).fetchone()
            if not row:
                return None
            conn.execute("UPDATE queue_jobs SET state='processing' WHERE id=?", (row[0],))
            return row[0], row[1], json.loads(row[2])

    def ack(self, job_id: int) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE queue_jobs SET state='done' WHERE id=?", (job_id,))

    def set_run_control(self, run_id: str, status: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO run_controls (run_id, status) VALUES (?,?) ON CONFLICT(run_id) DO UPDATE SET status=excluded.status, updated_at=CURRENT_TIMESTAMP",
                (run_id, status),
            )

    def get_run_control(self, run_id: str) -> str:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT status FROM run_controls WHERE run_id=?", (run_id,)).fetchone()
        return row[0] if row else "active"

    def push_episodic(self, namespace: str, content: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO episodic_memory (namespace,content) VALUES (?,?)", (namespace, content))

    def push_semantic(self, namespace: str, content: str, embedding_hint: str = "") -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO semantic_memory (namespace,content,embedding_hint) VALUES (?,?,?)",
                (namespace, content, embedding_hint),
            )

    def read_memory(self, table: str, namespace: str, limit: int = 10) -> list[str]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                f"SELECT content FROM {table} WHERE namespace=? ORDER BY id DESC LIMIT ?",
                (namespace, limit),
            ).fetchall()
        return [r[0] for r in rows]
