from fastapi import APIRouter

from backend.models.feedback_models import FeedbackRequest

router = APIRouter(prefix="/feedback", tags=["feedback"])

_feedback_store: list[dict] = []


@router.post("")
def feedback(req: FeedbackRequest) -> dict[str, str]:
    _feedback_store.append(
        {
            "session_id": req.session_id,
            "message_id": req.message_id,
            "helpful": req.helpful,
            "comment": req.comment,
        }
    )
    return {"status": "ok"}
