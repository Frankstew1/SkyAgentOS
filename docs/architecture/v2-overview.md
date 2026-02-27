# SkyAgentOS v2 Architecture Overview

## Control Plane
- gateway
- mission-api
- orchestrator
- scheduler
- model-router
- policy-engine
- memory-service
- artifact-service
- notification-service

## Execution Plane
- browser-worker
- desktop-worker
- tool-worker
- code-worker
- file-worker
- eval-worker

## User Plane
- dashboard
- desktop-shell
- admin-console

## Data Plane
- Postgres (core records)
- Redis (queue/locks/presence)
- Object storage (screenshots/videos/reports)
- Vector DB or pgvector (semantic memory)
