from typing import Any
from uuid import uuid4

from backend.models.repair_models import DeviceType, RiskLevel


class ConversationManager:
    """In-memory sessions: short history + extracted facts (MVP)."""

    def __init__(self) -> None:
        self._sessions: dict[str, dict[str, Any]] = {}

    def get_or_create(self, session_id: str | None) -> str:
        sid = session_id or str(uuid4())
        if sid not in self._sessions:
            self._sessions[sid] = {
                "facts": {
                    "device_type": None,
                    "brand": None,
                    "issue": None,
                    "observed_symptoms": [],
                    "risk_flags": [],
                },
                "history": [],
            }
        return sid

    def facts(self, session_id: str) -> dict[str, Any]:
        return self._sessions[session_id]["facts"]

    def history(self, session_id: str) -> list[dict[str, str]]:
        return self._sessions[session_id]["history"]

    def append_turn(self, session_id: str, role: str, content: str) -> None:
        self._sessions[session_id]["history"].append({"role": role, "content": content})
        if len(self._sessions[session_id]["history"]) > 20:
            self._sessions[session_id]["history"] = self._sessions[session_id]["history"][-20:]

    def merge_entities(
        self,
        session_id: str,
        device_type: DeviceType,
        problem_area: str,
        symptoms: list[str],
        brand: str | None,
        risk_level: RiskLevel,
    ) -> None:
        f = self.facts(session_id)
        f["device_type"] = device_type
        f["issue"] = problem_area
        if brand:
            f["brand"] = brand
        for s in symptoms:
            if s not in f["observed_symptoms"]:
                f["observed_symptoms"].append(s)
        if risk_level == "high":
            f["risk_flags"].append("elevated_risk_context")

    def preview_history(self, session_id: str, last_n: int = 8) -> list[dict[str, str]]:
        return self.history(session_id)[-last_n:]

    def get_session_payload(self, session_id: str) -> dict[str, Any] | None:
        return self._sessions.get(session_id)


conversation_manager = ConversationManager()
