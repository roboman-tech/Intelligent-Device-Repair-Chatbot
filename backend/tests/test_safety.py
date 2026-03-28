from backend.core.safety_rules import evaluate_safety


def test_swollen_battery_triggers():
    r = evaluate_safety("I think my battery is swollen on the back")
    assert r.triggered
    assert r.risk_level == "high"


def test_benign_message():
    r = evaluate_safety("My phone is a bit slow today")
    assert not r.triggered
