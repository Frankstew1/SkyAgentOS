from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from uuid import uuid4

from skyagentos.api.server import run_server
from skyagentos.models.schemas import Mission
from skyagentos.runtime.orchestrator import Orchestrator, specialist_catalog


def load_template(name: str | None) -> dict:
    template_path = Path(__file__).resolve().parents[1] / "templates" / "missions.json"
    templates = json.loads(template_path.read_text(encoding="utf-8"))
    return templates.get(name or "web_research", templates["web_research"])


def _orchestrator() -> Orchestrator:
    return Orchestrator(
        db_path=Path(os.getenv("MEMORY_DB_PATH", "/data/memory/skyagentos.db")),
        litellm_base_url=os.getenv("LITELLM_BASE_URL", "http://litellm:4000"),
        litellm_key=os.getenv("LITELLM_MASTER_KEY", "skyagentos-dev-key"),
        skyvern_url=os.getenv("SKYVERN_BASE_URL", "http://skyvern:8000"),
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


def main() -> None:
    parser = argparse.ArgumentParser(description="SkyAgentOS runtime")
    sub = parser.add_subparsers(dest="command")

    run_cmd = sub.add_parser("run", help="Run one mission")
    run_cmd.add_argument("--objective", default=os.getenv("SKYAGENT_OBJECTIVE", "Research cloud GPU pricing trends and summarize with sources"))
    run_cmd.add_argument("--template", default=os.getenv("SKYAGENT_TEMPLATE", "web_research"))
    run_cmd.add_argument("--domain", default=os.getenv("SKYAGENT_DOMAIN", "general"))
    run_cmd.add_argument("--runtime", choices=["browser", "desktop", "workspace"], default=None)

    sub.add_parser("serve", help="Start orchestrator HTTP API")
    sub.add_parser("benchmark", help="Run small benchmark/eval harness")
    args = parser.parse_args()

    if args.command == "serve":
        run_server()
    elif args.command == "benchmark":
        run_benchmark()
    else:
        if args.command is None:
            args.command = "run"
            args.objective = os.getenv("SKYAGENT_OBJECTIVE", "Research cloud GPU pricing trends and summarize with sources")
            args.template = os.getenv("SKYAGENT_TEMPLATE", "web_research")
            args.domain = os.getenv("SKYAGENT_DOMAIN", "general")
            args.runtime = None
        run_once(args)


if __name__ == "__main__":
    main()
