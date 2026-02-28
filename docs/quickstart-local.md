# Quickstart (Local)

## Modes
- **local-only**: `SKYAGENT_DRY_RUN=true`, no cloud keys required.
- **hybrid-cloud**: set provider keys in `.env`.
- **full-observability**: run compose + OTEL/Prometheus/Grafana.

## Steps
1. `cp .env.example .env`
2. Set `GF_SECURITY_ADMIN_USER` and `GF_SECURITY_ADMIN_PASSWORD`.
3. Optional local-only mode: keep `SKYAGENT_DRY_RUN=true`.
4. `docker compose up -d --build`
5. Health check: `python -m skyagentos.api.main doctor`
6. Run demo: `bash demos/run_demo.sh`

## First successful API run
```bash
PYTHONPATH=src:. SKYAGENT_DRY_RUN=true python -m skyagentos.api.main serve
curl -X POST http://127.0.0.1:8787/missions -H 'content-type: application/json' -d '{"objective":"quick smoke"}'
```
Expected: JSON containing `"state":"COMPLETED"` in dry-run mode.
