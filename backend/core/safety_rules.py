import re
from dataclasses import dataclass

_HIGH_RISK_RAW: list[tuple[str, str]] = [
    (r"\bswollen\b.*\bbattery\b|\bbattery\b.*\bswollen\b", "swollen battery"),
    (r"\bburn\b.*\bsmell\b|\bsmell\b.*\bburn", "burn smell"),
    (r"\bspark", "sparking"),
    (r"\bsmoke\b", "smoke"),
    (r"\belectric\s+shock\b|\bshock\b.*\bplug", "electric shock risk"),
    (r"\bliquid\b.*\bspill|\bspill\b.*\bkeyboard|\bwater\b.*\bphone", "liquid damage"),
    (r"\bcracked\b.*\bbattery\b", "cracked battery"),
    (r"\boverheat.*charg|\bcharg.*\boverheat|\bvery\s+hot\b.*\bcharg", "overheating while charging"),
    (r"\bmotherboard\b.*\bsolder|\breflow\b.*\bmotherboard", "advanced motherboard repair"),
]

_COMPILED_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(p, re.IGNORECASE), label) for p, label in _HIGH_RISK_RAW
]

_WS = re.compile(r"\s+")


@dataclass
class SafetyResult:
    triggered: bool
    reason: str | None
    risk_level: str
    user_message: str


def _normalize(text: str) -> str:
    return _WS.sub(" ", text.lower().strip())


def evaluate_safety(user_message: str) -> SafetyResult:
    t = _normalize(user_message)
    for pat, label in _COMPILED_PATTERNS:
        if pat.search(t):
            return SafetyResult(
                triggered=True,
                reason=label,
                risk_level="high",
                user_message=(
                    "Because your description may indicate a serious safety issue "
                    f"({label}), stop DIY repair steps. Unplug the device if it is "
                    "plugged in, avoid charging or opening it further, and contact "
                    "a qualified technician or the manufacturer service center."
                ),
            )
    return SafetyResult(
        triggered=False,
        reason=None,
        risk_level="low",
        user_message="",
    )
