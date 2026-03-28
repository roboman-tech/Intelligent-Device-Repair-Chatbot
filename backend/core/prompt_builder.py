import re
from typing import Any


SYSTEM_PROMPT = """You are a safe and helpful device repair assistant for computers and mobile phones.
Your job is to:
1. Understand the issue from the user message and conversation.
2. Ask short diagnostic questions when key information is missing (at most 2 questions).
3. Use the provided REPAIR CONTEXT when it is relevant; do not invent hardware facts not supported by context.
4. Give safe, step-by-step troubleshooting for low-risk actions first.
5. Never suggest dangerous repair actions without strong warnings.
6. Recommend professional repair for high-risk cases (battery swelling, liquid damage, smoke, severe overheating while charging).

Respond ONLY with a single JSON object matching this schema:
{
  "issue_summary": string,
  "needs_followup": boolean,
  "followup_questions": string[],
  "likely_causes": string[],
  "steps": string[],
  "warnings": string[],
  "escalate": boolean
}

In "steps" and "followup_questions", use plain sentences only — do not prefix with numbers (e.g. "1." or "2)") since the UI adds numbering.
"""


def format_context_block(chunks: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for i, c in enumerate(chunks, start=1):
        meta = c.get("metadata") or {}
        head = f"[{i}] device={meta.get('device_type')} issue={meta.get('issue')} risk={meta.get('risk_level')}"
        lines.append(head + "\n" + (c.get("text") or ""))
    return "\n\n---\n\n".join(lines)


def build_messages(
    user_message: str,
    history: list[dict[str, str]],
    rag_chunks: list[dict[str, Any]],
    session_facts: dict[str, Any],
) -> list[dict[str, str]]:
    ctx = format_context_block(rag_chunks)
    facts_json = str(session_facts)
    messages: list[dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.append(
        {
            "role": "system",
            "content": f"SESSION_FACTS (extracted so far): {facts_json}\n\nREPAIR CONTEXT:\n{ctx}",
        }
    )
    for turn in history:
        messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append(
        {
            "role": "user",
            "content": user_message
            + "\n\nIf needs_followup is true, ask at most 2 questions in followup_questions. "
            "Otherwise give clear steps and warnings.",
        }
    )
    return messages


def structured_to_reply(data: dict[str, Any]) -> str:
    parts: list[str] = []
    if data.get("issue_summary"):
        parts.append(data["issue_summary"])
    if data.get("needs_followup") and data.get("followup_questions"):
        parts.append("A few quick questions:")
        for q in data["followup_questions"][:3]:
            parts.append(f"- {q}")
    if data.get("likely_causes"):
        parts.append("Likely causes: " + "; ".join(data["likely_causes"][:5]))
    if data.get("steps"):
        parts.append("Suggested steps:")
        for i, s in enumerate(data["steps"][:12], 1):
            parts.append(f"{i}. {_strip_leading_step_number(str(s))}")
    if data.get("warnings"):
        parts.append("Warnings: " + " ".join(data["warnings"][:5]))
    if data.get("escalate"):
        parts.append("If symptoms worsen or involve battery heat/smell/swelling, stop and seek a technician.")
    return "\n\n".join(parts) if parts else "I could not produce a detailed answer. Please rephrase your issue."


_STEP_PREFIX = re.compile(r"^\s*\d+\s*[\.)]\s*")


def _strip_leading_step_number(text: str) -> str:
    """Remove '1. ', '2)', etc. so we do not double-prefix when formatting numbered steps."""
    s = (text or "").strip()
    while True:
        n = _STEP_PREFIX.sub("", s, count=1)
        if n == s:
            break
        s = n.strip()
    return s
