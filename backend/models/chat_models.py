from typing import Any

from pydantic import BaseModel, Field

from backend.models.repair_models import DeviceType, RiskLevel


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    device_type: DeviceType | None = None


class ChatResponse(BaseModel):
    reply: str
    issue_type: str | None = None
    risk_level: RiskLevel = "low"
    needs_followup: bool = False
    structured: dict[str, Any] | None = None
    safety_escalation: bool = False


class RetrieveRequest(BaseModel):
    query: str = Field(..., min_length=1)
    device_type: DeviceType | None = None
    issue: str | None = None
    top_k: int = 5


class RetrieveResponse(BaseModel):
    chunks: list[dict[str, Any]]


class SessionResponse(BaseModel):
    session_id: str
    facts: dict[str, Any]
    history_preview: list[dict[str, str]]
