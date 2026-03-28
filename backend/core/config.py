from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/core/config.py -> repo root
_REPO_ROOT = Path(__file__).resolve().parents[2]


def _is_sentence_transformer_dir(path: Path) -> bool:
    """True if folder looks like a saved SentenceTransformer / snapshot_download layout."""
    if not path.is_dir():
        return False
    if not (path / "config.json").is_file():
        return False
    markers = (
        "modules.json",
        "sentence_bert_config.json",
        "model.safetensors",
        "pytorch_model.bin",
    )
    return any((path / name).is_file() for name in markers)


def _looks_like_local_path(s: str) -> bool:
    """True if this string is meant as a filesystem path, not a Hugging Face repo id."""
    s = (s or "").strip()
    if not s:
        return False
    if s.startswith((".", "/", "\\")):
        return True
    if len(s) >= 2 and s[1] == ":":
        return True  # Windows drive, e.g. D:\...
    if "\\" in s:
        return True
    if s.startswith("model/") or s.startswith("models/"):
        return True
    return False


def _resolve_under_repo(raw: str) -> Path:
    p = Path(raw.strip().strip('"').strip("'")).expanduser()
    if not p.is_absolute():
        p = _REPO_ROOT / p
    return p.resolve()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_REPO_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    deepseek_chat_model: str = "deepseek-chat"

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    # Optional: preferred local folder (checked first). If missing or incomplete, Hugging Face is used.
    embedding_local_dir: str = ""

    chroma_persist_dir: str = "./backend/data/chroma_db"
    rag_top_k: int = 5

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def chroma_path(self) -> Path:
        return Path(self.chroma_persist_dir).resolve()

    @property
    def embedding_model_source(self) -> str:
        """Local model directory if one is present; otherwise Hugging Face model id (download/cache)."""
        em = self.embedding_model.strip()
        # Short name for default ./models/<name>/ — use last path segment if EMBEDDING_MODEL is a path
        if _looks_like_local_path(em):
            short_name = Path(em.rstrip("/\\")).name
        else:
            short_name = em.rstrip("/").split("/")[-1]

        candidates: list[Path] = []

        raw = (self.embedding_local_dir or "").strip().strip('"').strip("'")
        if raw:
            candidates.append(_resolve_under_repo(raw))

        if _looks_like_local_path(em):
            candidates.append(_resolve_under_repo(em))

        candidates.append((_REPO_ROOT / "models" / short_name).resolve())

        seen: list[Path] = []
        for path in candidates:
            if path in seen:
                continue
            seen.append(path)
            if _is_sentence_transformer_dir(path):
                return str(path)

        # Hub id only — never pass a missing ./path to SentenceTransformer (it uses process CWD)
        if _looks_like_local_path(em):
            return "sentence-transformers/all-MiniLM-L6-v2"
        return em

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
