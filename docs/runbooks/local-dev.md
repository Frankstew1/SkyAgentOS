# Local Dev Runbook

1. `cp .env.example .env`
2. `docker compose up -d --build`
3. `PYTHONPATH=src:. pytest -q`
4. `PYTHONPATH=src python main_orchestrator.py serve`
