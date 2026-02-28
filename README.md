# SkyAgentOS v2
## Linux-based agent platform for autonomous missions

SkyAgentOS is a **mission runner + computer-use platform** (browser + desktop + tools + memory + human controls), not a kernel operating system.

## Recommended entry path (new users)
1. Read `docs/quickstart-local.md`.
2. Run `skyagentos doctor`.
3. Run `bash demos/run_demo.sh`.
4. Use API: `POST /missions`.

## Canonical vs scaffolded code

### Canonical runtime (active)
- `src/skyagentos/` (orchestrator, API, runtime tools, memory)
- `docker-compose.yml` (local stack wiring)
- `demos/` + `tests/`

### Scaffold/prototype surfaces (v2 expansion)
- `services/` (service decomposition stubs)
- `workers/` (worker stubs)
- `apps/dashboard/` (UI stubs)
- `infra/k8s`, `infra/terraform`, `deploy/`

## Repo map
- `src/skyagentos`: runtime implementation
- `services`: control-plane service modules and stubs
- `workers`: execution-plane workers
- `apps`: user-plane dashboards
- `data`: migrations/seed/fixtures
- `docs`: onboarding, architecture, troubleshooting, model routing, skills
- `infra`: docker, k8s, terraform, observability assets
- `evals`: benchmark and scenario checks
- `tests`: unit/integration checks

## Install / packaging
SkyAgentOS is packaged from `src/` with `pyproject.toml`.

```bash
pip install -e .[dev]
skyagentos doctor
```

## Runtime modes and environment requirements

### Local-only dry-run (no provider keys required)
Use this for offline smoke runs and development.

Required variables:
- `GF_SECURITY_ADMIN_USER`
- `GF_SECURITY_ADMIN_PASSWORD`

Recommended variables:
- `SKYAGENT_DRY_RUN=true`

### Hybrid-cloud (provider keys required)
Use this when model/API calls should run against cloud providers.

Required variables:
- `OPENROUTER_API_KEY` and/or `OPENAI_API_KEY` and/or `NVIDIA_API_KEY`
- `LITELLM_MASTER_KEY`
- `GF_SECURITY_ADMIN_USER`
- `GF_SECURITY_ADMIN_PASSWORD`

## CLI
```bash
skyagentos run --template web_research
skyagentos serve
skyagentos benchmark
skyagentos doctor
skyagentos demo
skyagentos logs
```

## Docker compose entrypoints
- base stack: `docker compose up -d --build`
- local-only profile: `docker compose -f docker-compose.yml -f docker-compose.local-only.yml up -d --build`
- hybrid-cloud profile: `docker compose -f docker-compose.yml -f docker-compose.hybrid-cloud.yml up -d --build`
- full-observability profile: `docker compose -f docker-compose.yml -f docker-compose.full-observability.yml up -d --build`

## Security defaults
- Grafana credentials are **required** (no default `admin/admin`).
- Keep secrets only in `.env` (never commit real keys).
- For local/offline runs set `SKYAGENT_DRY_RUN=true`.

See `docs/troubleshooting.md` and `docs/model-routing.md` for runtime failure triage.

## OSS hygiene
- `LICENSE`
- `CONTRIBUTING.md`
- `CHANGELOG.md`
- `.github/ISSUE_TEMPLATE/*`
- `.github/pull_request_template.md`
