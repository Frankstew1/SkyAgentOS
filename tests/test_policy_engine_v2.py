from services.policy_engine.src.engine import PolicyEngine


def test_safe_research_blocks_desktop_without_approval():
    allowed, needs_approval = PolicyEngine().authorize("Safe Research", "desktop")
    assert allowed is False
    assert needs_approval is True
