import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Allow `uvicorn main:app` from backend/ — package imports expect repo root on sys.path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import chat, feedback, health, retrieve, session
from backend.core.config import settings

_log = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    _log.info(
        "Loading embedding model (first run downloads ~90MB). "
        "Avoid saving files that trigger uvicorn --reload until this finishes."
    )
    try:
        from backend.rag.embedder import warmup_embeddings

        await asyncio.to_thread(warmup_embeddings)
        _log.info("Embedding model ready.")
    except Exception:
        _log.exception("Embedding warmup failed; chat will still work but RAG may be empty until this is fixed.")
    try:
        yield
    finally:
        try:
            from backend.core.deepseek_client import close_deepseek_http_client

            close_deepseek_http_client()
        except Exception:
            pass


app = FastAPI(title="Device Repair Chatbot API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(chat.router, prefix="/api")
app.include_router(retrieve.router, prefix="/api")
app.include_router(feedback.router, prefix="/api")
app.include_router(session.router, prefix="/api")
