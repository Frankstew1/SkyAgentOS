# Quickstart (Local)

## Modes
- **local-only**: `SKYAGENT_DRY_RUN=true`, no cloud keys required.
- **hybrid-cloud**: set provider keys in `.env`.
- **full-observability**: run compose + OTEL/Prometheus/Grafana.

## Steps
1. `cp .env.example .env`
2. Set `GF_SECURITY_ADMIN_USER` and `GF_SECURITY_ADMIN_PASSWORD`.
3. Optional local-only mode: keep `SKYAGENT_DRY_RUN=true`.
4. `pip install -e .[dev]`
5. `docker compose up -d --build`
6. Health check: `skyagentos doctor`
7. Run demo: `bash demos/run_demo.sh`

## Compose overlays
```bash
# local-only
docker compose -f docker-compose.yml -f docker-compose.local-only.yml up -d --build

# hybrid-cloud
docker compose -f docker-compose.yml -f docker-compose.hybrid-cloud.yml up -d --build

# full-observability
docker compose -f docker-compose.yml -f docker-compose.full-observability.yml up -d --build
```

## First successful API run
```bash
SKYAGENT_DRY_RUN=true skyagentos serve
curl -X POST http://127.0.0.1:8787/missions -H 'content-type: application/json' -d '{"objective":"quick smoke"}'
```
Expected: JSON containing `"state":"COMPLETED"` in dry-run mode.
