# Intelligent Device Repair Chatbot (MVP)

Chat-first assistant for **phone** and **laptop** troubleshooting: intent/symptom extraction, **RAG** over a local repair dataset, **DeepSeek** for grounded replies (OpenAI-compatible API), rule-based **safety** escalation, and a **React** chat UI with feedback.

## Quick start

### 1. Backend

```powershell
cd d:\Source\RepairBot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Add DEEPSEEK_API_KEY to .env (optional for demo — without it, the API returns a setup hint)
python scripts\ingest_data.py
python scripts\warm_embeddings.py
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

**Local vs Hugging Face:** if `models\all-MiniLM-L6-v2\` exists (e.g. after `python scripts\download_embedding_model.py`), the API uses it; otherwise it downloads **`EMBEDDING_MODEL`** from the hub. Optional **`EMBEDDING_LOCAL_DIR`** adds another path to check first. See `models\README.md`.

If **`model.safetensors` stays at 0%**: use the download script above, or `pip install hf_transfer` and `HF_HUB_ENABLE_HF_TRANSFER=1`, or set `HF_ENDPOINT` in `.env` if the hub is slow or blocked (see `.env.example`).

On the **first** run, sentence-transformers downloads ~90 MB. If you use `--reload`, **do not save files** until the terminal shows `Embedding model ready` — otherwise the server restarts mid-download and `/api/chat` can error until you run `python scripts\warm_embeddings.py` again (or delete a partial model under `%USERPROFILE%\.cache\huggingface\hub`).

- API: `http://127.0.0.1:8000/docs`
- Health: `GET http://127.0.0.1:8000/health`

### 2. Frontend

```powershell
cd d:\Source\RepairBot\frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The dev server proxies `/api` and `/health` to port `8000`.

## Layout

Matches the architecture you described: `backend/` (FastAPI, RAG, DeepSeek client, safety), `frontend/` (Vite + React), `scripts/` (ingest / smoke eval), `backend/data/raw/` (JSON guides).

## Main API routes

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/chat` | Chat turn (`session_id`, `message`, optional `device_type`) |
| POST | `/api/retrieve` | Debug RAG retrieval |
| POST | `/api/feedback` | Thumbs up/down (in-memory MVP store) |
| GET | `/api/session/{id}` | Session facts + recent history |
| GET | `/health` | Liveness |

## Environment

See `.env.example`. Embeddings use **sentence-transformers** locally (`all-MiniLM-L6-v2` by default). Vectors live under `backend/data/chroma_db` (configurable via `CHROMA_PERSIST_DIR`).

## Tests

```powershell
cd d:\Source\RepairBot
pytest
```

## Next steps (your roadmap)

- Second retrieval pass after follow-up answers; cross-encoder **reranker**
- PostgreSQL/Mongo for sessions and feedback
- `deepseek-reasoner` for harder cases
- Image upload and richer taxonomy
