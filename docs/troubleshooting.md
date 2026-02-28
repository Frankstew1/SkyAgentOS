# Troubleshooting

## `local_reflector` returns model-not-found
Ensure `ollama-pull` completed and pulled `mistral:latest`.

## API not reachable
Check orchestrator port 8787 and run `python -m skyagentos.api.main doctor`.

## Desktop steps fail
Ensure `desktop-daemon` container is healthy and `DESKTOP_DAEMON_URL` is correct.

## Grafana fails to start
Set required `GF_SECURITY_ADMIN_USER` and `GF_SECURITY_ADMIN_PASSWORD` in `.env`.
