import logging
from functools import lru_cache
from pathlib import Path
from typing import Sequence

import numpy as np

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _model():
    from sentence_transformers import SentenceTransformer

    from backend.core.config import settings

    src = settings.embedding_model_source
    if Path(src).is_dir():
        logger.info("Using local embedding model: %s", src)
    else:
        logger.info("Using Hugging Face embedding model (download or cache): %s", src)
    return SentenceTransformer(src)


def embed_texts(texts: Sequence[str]) -> list[list[float]]:
    if not texts:
        return []
    model = _model()
    emb = model.encode(list(texts), convert_to_numpy=True, show_progress_bar=False)
    if isinstance(emb, np.ndarray):
        return emb.tolist()
    return [e.tolist() for e in emb]


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]


def warmup_embeddings() -> None:
    """Load/download the model once. Call at startup so the first /chat does not race with uvicorn --reload."""
    embed_texts(["warmup"])
