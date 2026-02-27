# SkyAgentOS v2
## Linux-based agent platform for autonomous missions

SkyAgentOS v2 is an agent operating environment (not a kernel OS) combining:
- mission orchestration
- browser-use and desktop-use runtimes
- workspace/tool runtimes
- memory retrieval and policy enforcement
- human-in-the-loop controls
- telemetry + eval harnesses

## Platform shape

### Control Plane
- gateway
- mission-api
- orchestrator
- scheduler
- model-router
- policy-engine
- memory-service
- artifact-service
- notification-service

### Execution Plane
- browser-worker
- desktop-worker
- tool-worker
- code-worker
- file-worker
- eval-worker

### User Plane
- dashboard
- desktop-shell (scaffold)
- admin-console (scaffold)

### Data Plane
- Postgres schema migration scaffold (`data/migrations/001_init_core.sql`)
- Redis/object/vector DB targets documented in `docs/architecture/v2-overview.md`

## Implemented now

### Runtime & API (functional)
- `src/skyagentos/runtime/orchestrator.py` multi-runtime orchestrator
- `src/skyagentos/api/server.py` mission/run-control API
- `src/skyagentos/tools/{skyvern_tool,desktop_tool}.py`
- `src/skyagentos/desktop/daemon.py`
- `src/skyagentos/memory/store.py` queue/state/memory persistence

### v2 service scaffolds
- `services/orchestrator/src/*` (models, state machine, dispatcher, agents)
- `services/{memory_service,policy_engine,artifact_service}/*`
- `services/{gateway,mission-api,scheduler,model-router,notification-service,mcp-hub,auth-service}/*`

### Worker scaffolds
- `workers/{browser_worker,desktop_worker,tool-worker,code-worker,file-worker,eval-worker}/src/*`

### UI scaffolds
- `apps/dashboard/src/pages/*`
- `apps/dashboard/src/components/*`

### Infra / deploy scaffolds
- `infra/docker/docker-compose.dev.yml`
- `infra/k8s/base/*`
- `infra/terraform/main.tf`
- `infra/otel/*`, `infra/prometheus/*`, `infra/grafana/dashboards/*`

### Evals
- `evals/browser/login_flow_eval.py`
- `evals/desktop/file_ops_eval.py`
- `evals/end_to_end/report_generation_eval.py`

## Quickstart
```bash
cp .env.example .env
PYTHONPATH=src:. pytest -q
PYTHONPATH=src python main_orchestrator.py serve
```

## Demo
```bash
bash demos/run_demo.sh
```

## Script entrypoints
- `scripts/dev/up.sh`
- `scripts/test/all.sh`
- `scripts/seed/load_templates.sh`
- `scripts/build/package.sh`
