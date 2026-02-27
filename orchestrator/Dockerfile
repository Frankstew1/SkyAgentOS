FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY orchestrator/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY main_orchestrator.py /app/main_orchestrator.py
COPY mcp_workspace_server.py /app/mcp_workspace_server.py

CMD ["python", "main_orchestrator.py"]
