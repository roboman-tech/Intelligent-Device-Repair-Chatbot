from fastapi import APIRouter, HTTPException

from backend.core.conversation_manager import conversation_manager
from backend.models.chat_models import SessionResponse

router = APIRouter(prefix="/session", tags=["session"])


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: str) -> SessionResponse:
    payload = conversation_manager.get_session_payload(session_id)
    if not payload:
        raise HTTPException(status_code=404, detail="Unknown session")
    return SessionResponse(
        session_id=session_id,
        facts=payload["facts"],
        history_preview=payload["history"][-12:],
    )
