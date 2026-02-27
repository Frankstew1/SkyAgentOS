from skyagentos.memory.retrieval import semantic_rank


def test_semantic_rank_returns_relevant_doc():
    docs = [
        "gpu pricing and market trends",
        "gardening and flowers",
        "browser automation reliability",
    ]
    ranked = semantic_rank("gpu market pricing", docs, k=2)
    assert ranked
    assert "gpu pricing" in ranked[0]
