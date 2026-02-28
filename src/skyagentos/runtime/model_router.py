from __future__ import annotations

import json
import os
from urllib import request


class ModelRouter:
    def __init__(self, base_url: str, api_key: str, budget_usd: float):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.budget_usd = budget_usd
        self.spent_usd = 0.0
        self.fallbacks = {
            "planner": ["planner", "manager", "local_reflector"],
            "vision_executor": ["vision_executor", "planner"],
            "validator": ["local_reflector", "planner"],
            "manager": ["manager", "planner"],
        }

    def _estimate_cost(self, text: str) -> float:
        return max(0.0002, len(text) / 10000.0)

    def complete(self, role: str, prompt: str) -> str:
        est = self._estimate_cost(prompt)
        if self.spent_usd + est > self.budget_usd:
            raise RuntimeError("budget exceeded")

        models = self.fallbacks.get(role, [role])
        last_err = None
        for model in models:
            try:
                out = self._call(model, prompt)
                self.spent_usd += est
                return out
            except Exception as exc:
                last_err = exc
        raise RuntimeError(f"all model fallbacks failed for role={role}: {last_err}")

    def _call(self, model: str, prompt: str) -> str:
        if os.getenv("SKYAGENT_DRY_RUN", "false").lower() == "true":
            if model == "local_reflector":
                return '{"passed": true, "reason": "dry-run validated", "next_action": "none"}'
            return f"[dry-run:{model}] {prompt[:180]}"

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }
        req = request.Request(
            f"{self.base_url}/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        with request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        return body["choices"][0]["message"]["content"]
