# Architecture

SkyAgentOS uses one orchestrator with runtime dispatch:
- Browser runtime (Skyvern)
- Desktop runtime (desktop daemon)
- Workspace runtime (artifact/memory paths)
- Tool runtime (MCP/tool workers)
- Reasoning runtime (planner/validator/reflector)

Control plane: mission-api, orchestrator, scheduler, model-router, policy-engine, memory-service, artifact-service.
Execution plane: browser-worker, desktop-worker, tool/code/file/eval workers.
Data plane: SQLite local store today, Postgres/Redis/Object/vector targets scaffolded.
