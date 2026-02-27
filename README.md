# SkyAgentOS
## The Operating System for Autonomous AI Agents

SkyAgentOS now runs as a **multi-runtime agent OS**:
- **Web runtime** via Skyvern
- **Desktop runtime** via a local computer-use daemon
- **Workspace runtime** via MCP/shared filesystem semantics

It includes a planner→executor→validator loop, persistent queueing, run controls (pause/resume), memory retrieval, model routing, and telemetry.

## Major upgrades in this revision
- Added a **desktop computer-use runtime** (`desktop-daemon`) and `DesktopTool`.
- Orchestrator now **selects runtime per step** (`browser` / `desktop` / `workspace`) from mission metadata or objective hints.
- Added **agent filesystem semantics** (`/missions/<run_id>/{inputs,outputs,artifacts,logs,evals,memory}`).
- Added **human takeover controls** via API:
  - `POST /runs/{run_id}/pause`
  - `POST /runs/{run_id}/resume`
  - `GET /runs/{run_id}`
- Kept Skyvern API path aligned (prompt-first + optional `x-api-key`) and self-hosted compose with Postgres + `DATABASE_STRING`.
- Added benchmark command: `python main_orchestrator.py benchmark`.

---

## Runtime Architecture

**Control plane**
- OpenClaw trigger skill → `POST /missions` on orchestrator API
- Operator controls → pause/resume/status endpoints

**Execution plane**
- Browser executor: Skyvern
- Desktop executor: local desktop daemon
- Workspace operations: MCP/shared storage

**State plane**
- SQLite tables: missions, runs, steps, artifacts, queue_jobs, telemetry, episodic_memory, semantic_memory, run_controls
- Per-run logical filesystem under `AGENT_FS_ROOT` (default `agentfs`)

**Observability plane**
- OTLP -> Collector -> Prometheus -> Grafana
- App-level metrics emitted as telemetry records for runtime call latency, validator latency, and error counts.

---

## Quick start

```bash
cp .env.example .env
docker compose up -d --build
```

### Run one mission (CLI)
```bash
PYTHONPATH=src SKYAGENT_DRY_RUN=true python main_orchestrator.py run --template web_research
```

### Run desktop mission
```bash
PYTHONPATH=src SKYAGENT_DRY_RUN=true python main_orchestrator.py run --template desktop_ops --runtime desktop
```

### Start API
```bash
PYTHONPATH=src python main_orchestrator.py serve
```

### Create mission via API
```bash
curl -X POST http://localhost:8787/missions \
  -H 'content-type: application/json' \
  -d '{"objective":"Organize local PDF files","metadata":{"runtime":"desktop"}}'
```

### Pause/Resume run
```bash
curl -X POST http://localhost:8787/runs/<run_id>/pause
curl -X POST http://localhost:8787/runs/<run_id>/resume
curl http://localhost:8787/runs/<run_id>
```

### Run benchmark/eval harness
```bash
PYTHONPATH=src SKYAGENT_DRY_RUN=true python main_orchestrator.py benchmark
```

---

## Mission templates
- `web_research`
- `desktop_ops`
- `invoice_processing`

Defined in `src/skyagentos/templates/missions.json`.

---

## Tests
```bash
PYTHONPATH=src pytest -q
```

Includes API ingress, run control semantics, runtime routing, queue persistence, Skyvern payload normalization, and dry-run end-to-end coverage.
