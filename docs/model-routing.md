# Model Routing

Routing aliases are in `litellm_config.yaml`:
- planner
- vision_executor
- local_reflector
- manager

Policies:
- prefer local reflector for validation when possible
- fallback chains in `src/skyagentos/runtime/model_router.py`
- budget ceiling via `SKYAGENT_BUDGET_USD`
