import re
from typing import Any

from backend.models.repair_models import DeviceType, IntentType, RiskLevel


DEVICE_KEYWORDS: list[tuple[re.Pattern[str], DeviceType]] = [
    (re.compile(r"\b(iphone|android|phone|mobile|pixel|galaxy|smartphone)\b", re.I), "mobile"),
    (re.compile(r"\b(laptop|macbook|notebook|ultrabook)\b", re.I), "laptop"),
    (re.compile(r"\b(desktop|pc|workstation)\b", re.I), "desktop"),
    (re.compile(r"\b(ipad|tablet|surface)\b", re.I), "tablet"),
]

ISSUE_KEYWORDS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bcharg|not charging|won't charge|battery.*%\b", re.I), "charging"),
    (re.compile(r"\boverheat|hot|thermal|shuts?\s+down|shutdown\b", re.I), "overheating"),
    (re.compile(r"\bblack\s+screen|no\s+display|screen\s+off\b", re.I), "display"),
    (re.compile(r"\bwifi|network|internet|cellular|lte\b", re.I), "network"),
    (re.compile(r"\bwon't\s+turn|no\s+power|boot|stuck\s+on\s+logo\b", re.I), "boot_power"),
    (re.compile(r"\bslow|lag|freeze|performance\b", re.I), "performance"),
    (re.compile(r"\bspeaker|mic|audio|sound\b", re.I), "audio"),
    (re.compile(r"\bstorage|full\s+disk|space\b", re.I), "storage"),
    (re.compile(r"\bbattery\b.*\b(drain|life)|drain.*fast\b", re.I), "battery"),
]

_MEDIUM_RISK_AREAS = frozenset({"charging", "overheating", "boot_power"})

INTENT_PATTERNS: list[tuple[re.Pattern[str], IntentType]] = [
    (re.compile(r"\bhow\s+does\b|\bexplain\b|\bwhy\b", re.I), "explain"),
    (re.compile(r"\bwarranty|service\s+center|repair\s+shop|technician\b", re.I), "service"),
    (re.compile(r"\burgent|danger|smoke|fire\b", re.I), "urgent_danger"),
    (re.compile(r"\bstep|how\s+to\s+fix|repair\b", re.I), "repair_step"),
]


def classify_intent_and_entities(
    message: str,
    selected_device: DeviceType | None = None,
) -> dict[str, Any]:
    text = message.strip()
    low = text.lower()

    intent: IntentType = "troubleshoot"
    for pat, it in INTENT_PATTERNS:
        if pat.search(low):
            intent = it
            break

    device_type: DeviceType | None = selected_device
    if not device_type:
        for pat, dt in DEVICE_KEYWORDS:
            if pat.search(low):
                device_type = dt
                break
    if not device_type:
        device_type = "mobile"

    problem_area = "general"
    for pat, area in ISSUE_KEYWORDS:
        if pat.search(low):
            problem_area = area
            break

    risk_level: RiskLevel = "medium" if problem_area in _MEDIUM_RISK_AREAS else "low"

    brand = None
    for b in ("iphone", "samsung", "google pixel", "pixel", "dell", "hp", "lenovo", "macbook"):
        if b in low:
            brand = b
            break

    return {
        "intent": intent,
        "device_type": device_type,
        "problem_area": problem_area,
        "symptoms": _extract_symptoms(low),
        "risk_level": risk_level,
        "brand": brand,
    }


def _extract_symptoms(low: str) -> list[str]:
    hints = []
    for phrase in (
        "not charging",
        "overheat",
        "shuts down",
        "black screen",
        "slow",
        "no wifi",
        "won't turn on",
    ):
        if phrase in low:
            hints.append(phrase.replace("'", ""))
    return hints or ["unspecified symptom"]


def build_retrieval_query(message: str, facts: dict[str, Any]) -> str:
    parts = [message]
    if facts.get("device_type"):
        parts.append(str(facts["device_type"]))
    if facts.get("problem_area"):
        parts.append(str(facts["problem_area"]))
    if facts.get("observed_symptoms"):
        parts.extend(str(s) for s in facts["observed_symptoms"][:5])
    return " ".join(parts)
