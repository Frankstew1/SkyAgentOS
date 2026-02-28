from __future__ import annotations

from collections import Counter


def _tokenize(text: str) -> set[str]:
    return {t.strip(".,:;!?()[]{}\"'").lower() for t in text.split() if t.strip()}


def semantic_rank(query: str, docs: list[str], k: int = 5) -> list[str]:
    q = _tokenize(query)
    scored: list[tuple[float, str]] = []
    for doc in docs:
        d = _tokenize(doc)
        denom = max(1, len(q.union(d)))
        score = len(q.intersection(d)) / denom
        scored.append((score, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for s, d in scored[:k] if s > 0]


def episodic_summary(events: list[str], limit: int = 5) -> str:
    words = Counter()
    for e in events:
        words.update(_tokenize(e))
    common = [w for w, _ in words.most_common(limit)]
    return ", ".join(common)
