from pydantic import BaseModel, Field


class FeedbackRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    message_id: str | None = None
    helpful: bool
    comment: str | None = None
