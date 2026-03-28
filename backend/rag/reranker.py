from typing import Any


def rerank(chunks: list[dict[str, Any]], _query: str, keep: int = 5) -> list[dict[str, Any]]:
    """MVP: keep top `keep` chunks in retrieval order (replace with cross-encoder later)."""
    return chunks[:keep]
