from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

_FAKE_CHUNKS = [
    {
        "id": "mobile_charging_01",
        "text": "Try another cable; inspect charging port.",
        "metadata": {"device_type": "mobile", "issue": "charging", "risk_level": "medium"},
    }
]


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@patch("backend.services.diagnosis_service.retrieve", return_value=_FAKE_CHUNKS)
def test_chat_without_deepseek_returns_structured_fallback(_mock_retrieve):
    payload = {"session_id": "s-test", "message": "My phone is not charging", "device_type": "mobile"}
    r = client.post("/api/chat", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert "reply" in body
    assert body.get("needs_followup") is not None
