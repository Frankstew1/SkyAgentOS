from pathlib import Path


def test_v2_scaffold_files_exist():
    required = [
        "data/migrations/001_init_core.sql",
        "infra/k8s/base/orchestrator-deployment.yaml",
        "infra/terraform/main.tf",
        "services/gateway/src/app.py",
        "workers/tool-worker/src/runner.py",
        "apps/dashboard/src/pages/live-run.tsx",
    ]
    for f in required:
        assert Path(f).exists(), f


def test_migration_contains_core_tables():
    text = Path("data/migrations/001_init_core.sql").read_text(encoding="utf-8")
    for table in [
        "users",
        "projects",
        "missions",
        "runs",
        "steps",
        "tool_calls",
        "artifacts",
        "approvals",
    ]:
        assert f"CREATE TABLE IF NOT EXISTS {table}" in text
