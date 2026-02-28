# SkyAgentOS
### The Operating System for Autonomous AI Agents

SkyAgentOS is a unified autonomous agent platform that combines modular skills, multi-agent crews, browser automation, memory, and planner → actor → validator loops in a single runtime.

## Tagline
**SkyAgentOS — The Operating System for Autonomous AI Agents.**

## What’s Included
- **OpenClaw-style skills** for event-driven triggering (WhatsApp/Telegram).
- **Skyvern-style browser execution** with vision-capable task automation.
- **CrewAI orchestration** with a `ResearchCrew` and sequential process flow.
- **AutoGPT/BabyAGI-style looping** with iterative self-correction and run journaling.
- **LiteLLM routing layer** with centralized model aliases.
- **Ollama local inference** for low-latency reflection tasks.
- **MCP workspace server** to share read/write context across the stack.
- **OTEL v2 observability** wired into Prometheus + Grafana.

## Architecture
`docker-compose.yml` defines:
- `openclaw-gateway` (OpenClaw 2026.2.19)
- `skyvern`
- `litellm`
- `ollama`
- `orchestrator`
- `mcp-workspace`
- `otel-collector`
- `prometheus`
- `grafana`

## Key Files
- `docker-compose.yml` — end-to-end service topology and shared volumes.
- `litellm_config.yaml` — model aliases and provider routing.
- `main_orchestrator.py` — CrewAI ResearchCrew + self-correction logic.
- `openclaw_skill.js` — OpenClaw trigger skill (Codex CLI first, Python fallback).
- `mcp_workspace_server.py` — shared workspace MCP read/write tools.
- `orchestrator/Dockerfile` + `orchestrator/requirements.txt` — pinned orchestrator runtime.
- `telemetry/` — OTEL collector + Prometheus scrape configuration.

## Required Environment Variables
- `OPENROUTER_API_KEY`
- `NVIDIA_API_KEY`
- `OPENAI_API_KEY`
- `LITELLM_MASTER_KEY`

Optional:
- `SKYVERN_BASE_URL`
- `SKYAGENT_OBJECTIVE`
- `MAX_SELF_CORRECTIONS`
- `OPENCLAW_WHATSAPP_ENABLED`
- `OPENCLAW_TELEGRAM_ENABLED`

## Quick Start
```bash
docker compose up -d --build
```

## Suggested GitHub Topics
`ai-agents`, `autonomous-agents`, `agent-framework`, `multi-agent-systems`, `ai-automation`, `browser-automation`, `ai-orchestration`, `agent-os`, `ai-infrastructure`, `llm-agents`
