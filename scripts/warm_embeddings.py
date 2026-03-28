"""
Pre-download / load the sentence-transformers model so the first API request does not race with uvicorn --reload.
Run from repo root:  python scripts/warm_embeddings.py

If `model.safetensors` stays at 0%%, run first:
  python scripts/download_embedding_model.py
Optional: pip install hf_transfer  then  set HF_HUB_ENABLE_HF_TRANSFER=1
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")
os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "600")

from backend.rag.embedder import warmup_embeddings  # noqa: E402


def main() -> None:
    from backend.core.config import settings

    src = settings.embedding_model_source
    mode = "local" if Path(src).is_dir() else "Hugging Face / cache"
    print(f"Warming up embeddings ({mode}): {src}")
    print("HF timeout = %ss" % os.environ.get("HF_HUB_DOWNLOAD_TIMEOUT", "?"))
    warmup_embeddings()
    print("Done.")





if __name__ == "__main__":

    main()

