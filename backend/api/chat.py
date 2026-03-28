import logging

from fastapi import APIRouter

from backend.models.chat_models import ChatRequest, ChatResponse
from backend.services.diagnosis_service import run_chat

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)

_FAIL_HINT = (
    "The repair API hit an error. Common causes: (1) The embedding model was still downloading when "
    "the server reloaded — run without --reload until the first download finishes, or run "
    "`python scripts/warm_embeddings.py` from the RepairBot folder. (2) Corrupt Hugging Face cache — "
    "delete the folder for `sentence-transformers/all-MiniLM-L6-v2` under `%USERPROFILE%\\.cache\\huggingface\\hub` "
    "and restart. (3) Run `python scripts/ingest_data.py` if you have not built the vector index yet."
)


@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    try:
        return run_chat(req.session_id, req.message, req.device_type)
    except Exception:
        logger.exception("POST /api/chat failed")
        return ChatResponse(
            reply=_FAIL_HINT,
            issue_type="error",
            risk_level="low",
            needs_followup=False,
            structured=None,
            safety_escalation=False,
        )
