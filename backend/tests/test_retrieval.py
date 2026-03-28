from backend.rag.chunker import record_to_chunk


def test_record_to_chunk_metadata():
    rec = {
        "id": "t1",
        "device_type": "mobile",
        "issue": "charging",
        "risk_level": "low",
        "source_type": "repair_guide",
        "brand": "generic",
        "title": "Test",
        "symptoms": ["a"],
        "possible_causes": ["b"],
        "diagnostic_questions": [],
        "solutions": ["c"],
        "escalation_conditions": [],
    }
    ch = record_to_chunk(rec)
    assert ch["id"] == "t1"
    assert "charging" in ch["metadata"]["issue"]
