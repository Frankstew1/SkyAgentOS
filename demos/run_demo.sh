#!/usr/bin/env bash
set -euo pipefail

mkdir -p tmp
export PYTHONPATH=src
export SKYAGENT_DRY_RUN=true
export MEMORY_DB_PATH=tmp/demo.db
export SKYAGENT_OBJECTIVE="Demo: research cloud GPU price trends with references"

if command -v skyagentos >/dev/null 2>&1; then
  CLI="skyagentos"
else
  CLI="python -m skyagentos.api.main"
fi

echo "== web runtime demo =="
$CLI run --template web_research

echo "== desktop runtime demo =="
$CLI run --template desktop_ops --runtime desktop
