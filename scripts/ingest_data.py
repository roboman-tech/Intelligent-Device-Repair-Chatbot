"""
Build / refresh the Chroma vector index from JSON guides in backend/data/raw.
Run from repo root:  python scripts/ingest_data.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.rag.ingestion_pipeline import ingest_paths  # noqa: E402


def main() -> None:
    raw = ROOT / "backend" / "data" / "raw"
    paths = [
        raw / "phone_repair_guides.json",
        raw / "laptop_repair_guides.json",
        raw / "faq.json",
    ]
    n = ingest_paths(paths, reset=True)
    print(f"Ingested {n} chunks into Chroma at configured persist dir.")


if __name__ == "__main__":
    main()
