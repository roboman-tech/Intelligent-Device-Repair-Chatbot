import logging
from typing import Any

from backend.core.config import settings
from backend.rag.embedder import embed_query
from backend.rag.reranker import rerank
from backend.rag.vector_store import get_collection

logger = logging.getLogger(__name__)


def retrieve(
    query: str,
    top_k: int | None = None,
    device_type: str | None = None,
    issue: str | None = None,
) -> list[dict[str, Any]]:
    try:
        return _retrieve_impl(query, top_k, device_type, issue)
    except Exception:
        logger.exception("RAG retrieve failed (empty Chroma, bad cache, or embedding model not ready)")
        return []


def _retrieve_impl(
    query: str,
    top_k: int | None,
    device_type: str | None,
    issue: str | None,
) -> list[dict[str, Any]]:
    k = top_k or settings.rag_top_k
    col = get_collection()
    qemb = [embed_query(query)]
    where: dict[str, Any] | None = None
    if device_type and issue:
        where = {"$and": [{"device_type": device_type}, {"issue": issue}]}
    elif device_type:
        where = {"device_type": device_type}
    elif issue:
        where = {"issue": issue}

    def _query(w: dict[str, Any] | None) -> dict[str, Any]:
        return col.query(
            query_embeddings=qemb,
            n_results=k,
            where=w,
            include=["documents", "metadatas", "distances"],
        )

    res = _query(where)
    ids = (res.get("ids") or [[]])[0]
    if not ids and where is not None:
        res = _query(None)
        ids = (res.get("ids") or [[]])[0]
    chunks: list[dict[str, Any]] = []
    docs = (res.get("documents") or [[]])[0]
    metas = (res.get("metadatas") or [[]])[0]
    for i, cid in enumerate(ids):
        chunks.append(
            {
                "id": cid,
                "text": docs[i] if i < len(docs) else "",
                "metadata": metas[i] if i < len(metas) else {},
            }
        )
    return rerank(chunks, query, keep=min(k, 5))
