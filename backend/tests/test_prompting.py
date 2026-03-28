from backend.core.prompt_builder import structured_to_reply, _strip_leading_step_number


def test_strip_leading_step_number():
    assert _strip_leading_step_number("1. Do this") == "Do this"
    assert _strip_leading_step_number("2) Go there") == "Go there"
    assert _strip_leading_step_number("1. 1. Nested") == "Nested"


def test_structured_to_reply():
    data = {
        "issue_summary": "Charging port may be dirty",
        "needs_followup": True,
        "followup_questions": ["Tried another cable?"],
        "likely_causes": ["lint"],
        "steps": ["Inspect port"],
        "warnings": ["Stop if hot"],
        "escalate": False,
    }
    text = structured_to_reply(data)
    assert "Charging" in text
    assert "cable" in text


def test_structured_to_reply_steps_no_double_number():
    data = {
        "issue_summary": "Test",
        "steps": ["1. First action", "2) Second action"],
        "escalate": False,
    }
    text = structured_to_reply(data)
    assert "1. First action" in text
    assert "1. 1." not in text
