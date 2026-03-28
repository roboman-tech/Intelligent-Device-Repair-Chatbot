from typing import Any

from backend.core.config import settings
from backend.core.conversation_manager import conversation_manager
from backend.core.deepseek_client import chat_completion_json
from backend.core.intent_classifier import build_retrieval_query, classify_intent_and_entities
from backend.core.prompt_builder import build_messages, structured_to_reply
from backend.core.safety_rules import evaluate_safety
from backend.models.chat_models import ChatResponse
from backend.models.repair_models import RiskLevel
from backend.rag.retriever import retrieve


def _merge_risk(a: RiskLevel, b: RiskLevel) -> RiskLevel:
    order = {"low": 0, "medium": 1, "high": 2}
    return a if order[a] >= order[b] else b


def run_chat(session_id: str | None, message: str, selected_device: str | None) -> ChatResponse:
    sid = conversation_manager.get_or_create(session_id)
    conversation_manager.append_turn(sid, "user", message)

    safety = evaluate_safety(message)
    if safety.triggered:
        conversation_manager.append_turn(sid, "assistant", safety.user_message)
        return ChatResponse(
            reply=safety.user_message,
            issue_type="safety_escalation",
            risk_level="high",
            needs_followup=False,
            structured=None,
            safety_escalation=True,
        )

    entities = classify_intent_and_entities(message, selected_device)  # type: ignore[arg-type]
    conversation_manager.merge_entities(
        sid,
        entities["device_type"],
        entities["problem_area"],
        entities["symptoms"],
        entities.get("brand"),
        entities["risk_level"],
    )
    facts = conversation_manager.facts(sid)
    q = build_retrieval_query(message, facts)

    chunks = retrieve(
        q,
        top_k=settings.rag_top_k,
        device_type=str(facts.get("device_type") or entities["device_type"]),
        issue=str(entities["problem_area"]) if entities["problem_area"] != "general" else None,
    )
    if not chunks:
        chunks = retrieve(q, top_k=settings.rag_top_k, device_type=None, issue=None)

    hist = conversation_manager.preview_history(sid, last_n=8)
    messages = build_messages(message, hist[:-1], chunks, facts)
    _raw, parsed = chat_completion_json(messages)

    if not parsed:
        reply = (
            "I could not parse a structured answer. Based on general guidance: try safe checks "
            "(cable, outlet, restart) and avoid heat or swelling around the battery. "
            "Seek a technician if you smell burning or the device gets very hot while charging."
        )
        conversation_manager.append_turn(sid, "assistant", reply)
        return ChatResponse(
            reply=reply,
            issue_type=entities["problem_area"],
            risk_level=entities["risk_level"],
            needs_followup=True,
            structured=None,
            safety_escalation=False,
        )

    reply = structured_to_reply(parsed)
    if parsed.get("escalate"):
        entities["risk_level"] = _merge_risk(entities["risk_level"], "high")

    conversation_manager.append_turn(sid, "assistant", reply)
    return ChatResponse(
        reply=reply,
        issue_type=entities["problem_area"],
        risk_level=entities["risk_level"],
        needs_followup=bool(parsed.get("needs_followup")),
        structured=parsed,
        safety_escalation=bool(parsed.get("escalate")),
    )
