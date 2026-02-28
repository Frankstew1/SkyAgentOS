from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
from pathlib import Path
from uuid import uuid4

from skyagentos.api.server import run_server
from skyagentos.config import load_settings
from skyagentos.models.schemas import Mission
from skyagentos.runtime.orchestrator import Orchestrator, specialist_catalog


def load_template(name: str | None) -> dict:
    template_path = Path(__file__).resolve().parents[1] / "templates" / "missions.json"
    templates = json.loads(template_path.read_text(encoding="utf-8"))
    return templates.get(name or "web_research", templates["web_research"])


def _orchestrator() -> Orchestrator:
    cfg = load_settings()
    return Orchestrator(
        db_path=Path(cfg.memory_db_path),
        litellm_base_url=cfg.litellm_base_url,
        litellm_key=os.getenv("LITELLM_MASTER_KEY", "skyagentos-dev-key"),
        skyvern_url=cfg.skyvern_base_url,
    )


def run_once(args: argparse.Namespace) -> None:
    t = load_template(args.template)
    metadata = {"runtime": args.runtime} if args.runtime else {}
    mission = Mission(
        id=f"mission-{uuid4().hex[:8]}",
        objective=args.objective or t["objective"],
        domain=args.domain or t["domain"],
        permissions=t["permissions"],
        budget_usd=float(os.getenv("SKYAGENT_BUDGET_USD", t["budget_usd"])),
        max_steps=int(os.getenv("MAX_SELF_CORRECTIONS", t["max_steps"])),
        template=args.template,
        metadata=metadata,
    )

    result = _orchestrator().run_mission(mission)
    print(json.dumps({"result": result, "specialists": specialist_catalog()}, indent=2))


def run_benchmark() -> None:
    templates = ["web_research", "desktop_ops"]
    results = []
    for tname in templates:
        t = load_template(tname)
        mission = Mission(
            id=f"mission-{uuid4().hex[:8]}",
            objective=t["objective"],
            domain=t["domain"],
            permissions=t["permissions"],
            budget_usd=t["budget_usd"],
            max_steps=2,
            template=tname,
            metadata={"runtime": "desktop" if tname == "desktop_ops" else "browser"},
        )
        results.append({"template": tname, "result": _orchestrator().run_mission(mission)})
    print(json.dumps({"benchmark": results}, indent=2))


def _check_tcp(host: str, port: int, timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def doctor() -> None:
    cfg = load_settings()
    checks = {
        "memory_path_parent_exists": Path(cfg.memory_db_path).parent.exists(),
        "litellm_dns_resolves": _check_tcp("litellm", 4000) or _check_tcp("127.0.0.1", 4000),
        "ollama_dns_resolves": _check_tcp("ollama", 11434) or _check_tcp("127.0.0.1", 11434),
        "skyvern_dns_resolves": _check_tcp("skyvern", 8000) or _check_tcp("127.0.0.1", 8000),
        "dry_run_enabled": cfg.dry_run,
    }
    print(
        json.dumps(
            {"doctor": checks, "ok": all(v for k, v in checks.items() if k != "dry_run_enabled")},
            indent=2,
        )
    )


def up() -> None:
    subprocess.run(["bash", "scripts/dev/up.sh"], check=True)


def logs() -> None:
    subprocess.run(["bash", "-lc", "docker compose logs --tail=120"], check=False)


def demo() -> None:
    subprocess.run(["bash", "demos/run_demo.sh"], check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="SkyAgentOS runtime")
    sub = parser.add_subparsers(dest="command")

    run_cmd = sub.add_parser("run", help="Run one mission")
    run_cmd.add_argument(
        "--objective",
        default=os.getenv(
            "SKYAGENT_OBJECTIVE", "Research cloud GPU pricing trends and summarize with sources"
        ),
    )
    run_cmd.add_argument("--template", default=os.getenv("SKYAGENT_TEMPLATE", "web_research"))
    run_cmd.add_argument("--domain", default=os.getenv("SKYAGENT_DOMAIN", "general"))
    run_cmd.add_argument("--runtime", choices=["browser", "desktop", "workspace"], default=None)

    sub.add_parser("serve", help="Start orchestrator HTTP API")
    sub.add_parser("benchmark", help="Run small benchmark/eval harness")
    sub.add_parser("doctor", help="Validate local runtime prerequisites")
    sub.add_parser("up", help="Bring up local stack via scripts/dev/up.sh")
    sub.add_parser("logs", help="Tail docker compose logs")
    sub.add_parser("demo", help="Run local demo workflow")

    args = parser.parse_args()

    if args.command == "serve":
        run_server()
    elif args.command == "benchmark":
        run_benchmark()
    elif args.command == "doctor":
        doctor()
    elif args.command == "up":
        up()
    elif args.command == "logs":
        logs()
    elif args.command == "demo":
        demo()
    else:
        if args.command is None:
            args.command = "run"
            args.objective = os.getenv(
                "SKYAGENT_OBJECTIVE", "Research cloud GPU pricing trends and summarize with sources"
            )
            args.template = os.getenv("SKYAGENT_TEMPLATE", "web_research")
            args.domain = os.getenv("SKYAGENT_DOMAIN", "general")
            args.runtime = None
        run_once(args)


if __name__ == "__main__":
    main()
