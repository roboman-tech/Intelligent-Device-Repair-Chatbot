import threading
from typing import TYPE_CHECKING, Any

from backend.core.config import settings

if TYPE_CHECKING:
    from chromadb.api.models.Collection import Collection

COLLECTION_NAME = "repair_chunks"

_client_lock = threading.Lock()
_client_inst: Any = None


def get_client():
    """Single PersistentClient per process (avoids reopening SQLite on every query)."""
    global _client_inst
    if _client_inst is not None:
        return _client_inst
    with _client_lock:
        if _client_inst is None:
            import chromadb

            settings.chroma_path.mkdir(parents=True, exist_ok=True)
            _client_inst = chromadb.PersistentClient(path=str(settings.chroma_path))
    return _client_inst


def get_collection() -> "Collection":
    return get_client().get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def add_chunks(chunks: list[dict[str, Any]], embeddings: list[list[float]]) -> None:
    col = get_collection()
    ids = [c["id"] for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]
    col.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)


def clear_collection() -> None:
    client = get_client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
