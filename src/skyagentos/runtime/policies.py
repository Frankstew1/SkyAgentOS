from __future__ import annotations

from skyagentos.models.schemas import Mission

DOMAIN_POLICIES = {
    "finance": {"blocked_domains": ["*"], "requires_human_review": True},
    "health": {"blocked_domains": ["*"], "requires_human_review": True},
    "general": {"blocked_domains": [], "requires_human_review": False},
}


def check_permissions(mission: Mission, required: list[str]) -> None:
    missing = [perm for perm in required if perm not in mission.permissions]
    if missing:
        raise PermissionError(f"policy: missing permissions: {missing}")


def requires_human_review(mission: Mission) -> bool:
    policy = DOMAIN_POLICIES.get(mission.domain, DOMAIN_POLICIES["general"])
    return bool(policy.get("requires_human_review"))
