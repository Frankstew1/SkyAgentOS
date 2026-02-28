from __future__ import annotations

from collections import Counter


class MemoryService:
    def retrieve_before_plan(self, objective: str, episodic: list[str], semantic: list[str]) -> dict:
        tokens = set(objective.lower().split())
        ranked = sorted(semantic, key=lambda d: len(tokens.intersection(set(d.lower().split()))), reverse=True)
        top = ranked[:5]
        counts = Counter(" ".join(episodic).lower().split())
        return {"semantic": top, "episodic_hint": [w for w, _ in counts.most_common(5)]}
