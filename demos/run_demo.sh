#!/usr/bin/env bash
set -euo pipefail

mkdir -p tmp
export PYTHONPATH=src
export SKYAGENT_DRY_RUN=true
export MEMORY_DB_PATH=tmp/demo.db
export SKYAGENT_OBJECTIVE="Demo: research cloud GPU price trends with references"

echo "== web runtime demo =="
python main_orchestrator.py run --template web_research

echo "== desktop runtime demo =="
python main_orchestrator.py run --template desktop_ops --runtime desktop

