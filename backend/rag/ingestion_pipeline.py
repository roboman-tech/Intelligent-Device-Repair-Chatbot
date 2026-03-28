import json
from pathlib import Path
from typing import Any

from backend.rag.chunker import record_to_chunk
from backend.rag.embedder import embed_texts
from backend.rag.vector_store import add_chunks, clear_collection


def load_json_records(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "records" in data:
        return list(data["records"])
    return []


def ingest_paths(paths: list[Path], reset: bool = True) -> int:
    if reset:
        clear_collection()
    all_chunks: list[dict[str, Any]] = []
    for p in paths:
        if not p.exists():
            continue
        for rec in load_json_records(p):
            all_chunks.append(record_to_chunk(rec))
    if not all_chunks:
        return 0
    embs = embed_texts([c["text"] for c in all_chunks])
    add_chunks(all_chunks, embs)
    return len(all_chunks)
