from backend.core.safety_rules import SafetyResult


def escalation_reply(safety: SafetyResult) -> str:
    return safety.user_message
