# Local embedding model (optional)

The app **auto-detects** a local model:

1. **`EMBEDDING_LOCAL_DIR`** in `.env` (if set and the folder contains a valid model), then  
2. **`models/<short-model-name>/`** (e.g. `models/all-MiniLM-L6-v2` for `EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2`), then  
3. **Hugging Face** — download into the HF cache (same as unset local).

To populate the default folder:

`python scripts/download_embedding_model.py`

No `.env` line is required if files land in `models/all-MiniLM-L6-v2/`.

You can also copy a full model directory here (or set **`EMBEDDING_LOCAL_DIR`** to any path).
