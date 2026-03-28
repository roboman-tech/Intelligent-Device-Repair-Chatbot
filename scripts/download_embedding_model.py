"""
Download the embedding model into ./models/<model-name>/ (default).

The API loads that folder automatically if it exists; otherwise it pulls from Hugging Face.

Examples (from repo root):
  python scripts/download_embedding_model.py
  python scripts/download_embedding_model.py --local-dir models/my-minilm
  python scripts/download_embedding_model.py --hub-cache

Optional: pip install hf_transfer  and  set HF_HUB_ENABLE_HF_TRANSFER=1
Mirror: HF_ENDPOINT=https://hf-mirror.com in .env
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")
os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "600")

from huggingface_hub import snapshot_download  # noqa: E402

from backend.core.config import settings  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Download sentence-transformers embedding model")
    parser.add_argument(
        "--local-dir",
        type=Path,
        default=None,
        help="Folder to write model files (offline use). Default: models/<huggingface-model-name>/",
    )
    parser.add_argument(
        "--hub-cache",
        action="store_true",
        help="Download into the Hugging Face cache only (do not use EMBEDDING_LOCAL_DIR workflow)",
    )
    args = parser.parse_args()

    repo_id = settings.embedding_model
    short_name = repo_id.split("/")[-1]

    print("Repo:", repo_id)
    print("HF_HUB_DOWNLOAD_TIMEOUT =", os.environ.get("HF_HUB_DOWNLOAD_TIMEOUT"))
    if os.environ.get("HF_ENDPOINT"):
        print("HF_ENDPOINT =", os.environ["HF_ENDPOINT"])

    if args.hub_cache:
        print("Downloading into Hugging Face cache…")
        snapshot_download(repo_id=repo_id, repo_type="model")
        print("Done. Unset EMBEDDING_LOCAL_DIR (or leave empty) to use the cache.")
        return

    local = (args.local_dir or (ROOT / "models" / short_name)).resolve()
    local.mkdir(parents=True, exist_ok=True)
    print(f"Downloading into: {local}")
    snapshot_download(
        repo_id=repo_id,
        repo_type="model",
        local_dir=str(local),
        local_dir_use_symlinks=False,
    )
    print("Done. The API will use this folder automatically (no .env change needed if path matches EMBEDDING_MODEL).")
    try:
        rel = local.relative_to(ROOT)
        print(f"Optional .env override: EMBEDDING_LOCAL_DIR={rel.as_posix()}")
    except ValueError:
        print(f"Optional .env override: EMBEDDING_LOCAL_DIR={local}")
    print("Then run: python scripts/warm_embeddings.py")


if __name__ == "__main__":
    main()
