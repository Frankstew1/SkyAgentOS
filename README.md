# SkyAgentOS v2
## The Operating Environment for Autonomous AI Agents

SkyAgentOS v2 is a Linux-based agent platform (not a kernel OS) that unifies:
- **mission runner + orchestrator**
- **browser-use runtime**
- **desktop computer-use runtime**
- **workspace + tool runtime**
- **memory-backed planning and retries**
- **policy engine + human controls**
- **telemetry + eval harnesses**

## v2 control/execution/data plane

### Control plane
- gateway
- mission-api
- orchestrator
- scheduler
- model-router
- policy-engine
- memory-service
- artifact-service

### Execution plane
- browser-worker
- desktop-worker
- tool-worker (scaffold)
- workspace runtime (scaffold)

### Data plane
- Postgres/Redis/Object storage/Vector DB are documented targets
- Current local runtime persists to SQLite + per-run filesystem

## Implemented v2 modules in this repo

### Backend scaffolds and cores
- `services/orchestrator/src/mission/models.py`
- `services/orchestrator/src/runtime/state_machine.py`
- `services/orchestrator/src/runtime/dispatcher.py`
- `services/orchestrator/src/agents/{planner,validator,reflector}.py`
- `services/memory_service/src/retrieval.py`
- `services/policy_engine/src/engine.py`
- `services/artifact_service/src/store.py`
- `workers/browser_worker/src/session_manager.py`
- `workers/desktop_worker/src/controller.py`

### Dashboard stubs
- `apps/dashboard/src/pages/{live-run,missions,artifacts,memory,apps}.tsx`
- `apps/dashboard/src/components/{ApprovalPanel,LiveDesktopStream}.tsx`

### Infra/evals scaffolds
- `infra/docker/docker-compose.dev.yml`
- `infra/otel/collector.yaml`
- `infra/prometheus/prometheus.yaml`
- `infra/grafana/dashboards/mission-health.json`
- `evals/browser/login_flow_eval.py`
- `evals/desktop/file_ops_eval.py`
- `evals/end_to_end/report_generation_eval.py`

## Existing runtime upgraded
Current `src/skyagentos/runtime/orchestrator.py` now supports:
- runtime dispatch (`browser` / `desktop` / `workspace` hint)
- per-run agent filesystem semantics (`agentfs/missions/<run_id>/...`)
- pause/resume-aware execution through run controls
- separate executor + validator persistence and telemetry

## API controls
- `POST /missions`
- `POST /runs/{run_id}/pause`
- `POST /runs/{run_id}/resume`
- `GET /runs/{run_id}`

## Quickstart
```bash
PYTHONPATH=src SKYAGENT_DRY_RUN=true python main_orchestrator.py run --template web_research
PYTHONPATH=src SKYAGENT_DRY_RUN=true python main_orchestrator.py run --template desktop_ops --runtime desktop
PYTHONPATH=src python main_orchestrator.py serve
PYTHONPATH=src SKYAGENT_DRY_RUN=true python main_orchestrator.py benchmark
```

## Tests
```bash
PYTHONPATH=src pytest -q
```
