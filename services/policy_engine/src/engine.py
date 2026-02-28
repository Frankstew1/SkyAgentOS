from __future__ import annotations

POLICY_PROFILES = {
    "Safe Research": {
        "allow_runtimes": {"browser", "workspace", "tools"},
        "require_approval": {"desktop"},
    },
    "Operator Mode": {
        "allow_runtimes": {"browser", "workspace", "tools", "desktop"},
        "require_approval": set(),
    },
}


class PolicyEngine:
    def authorize(self, profile: str, runtime: str) -> tuple[bool, bool]:
        policy = POLICY_PROFILES.get(profile, POLICY_PROFILES["Safe Research"])
        allowed = runtime in policy["allow_runtimes"]
        needs_approval = runtime in policy["require_approval"]
        return allowed, needs_approval
