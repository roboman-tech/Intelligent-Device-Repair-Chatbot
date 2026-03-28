"""
Lightweight manual RAG smoke checks (extend with labeled queries later).
Run from repo root:  python scripts/evaluate_rag.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.rag.retriever import retrieve  # noqa: E402


def main() -> None:
    cases = [
        ("phone not charging cable works sometimes", "mobile", "charging"),
        ("laptop gets hot and turns off", "laptop", "overheating"),
        ("spilled water on keyboard", None, None),
    ]
    for q, dt, issue in cases:
        chunks = retrieve(q, top_k=5, device_type=dt, issue=issue)
        print("---")
        print("Q:", q, "| filter:", dt, issue)
        for c in chunks:
            print(" ", c.get("id"), c.get("metadata"))


if __name__ == "__main__":
    main()
