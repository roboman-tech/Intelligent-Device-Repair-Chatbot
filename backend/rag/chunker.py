from typing import Any


def record_to_chunk(record: dict[str, Any]) -> dict[str, Any]:
    """Turn a structured repair record into one RAG chunk + metadata."""
    rid = str(record.get("id") or record.get("issue_id") or "unknown")
    title = record.get("title") or record.get("issue") or "Repair topic"
    lines = [f"# {title}"]

    for key in ("symptoms", "possible_causes", "diagnostic_questions", "solutions", "escalation_conditions"):
        vals = record.get(key)
        if isinstance(vals, list) and vals:
            lines.append(f"{key.replace('_', ' ').title()}:")
            for v in vals:
                lines.append(f"- {v}")

    if record.get("notes"):
        lines.append(str(record["notes"]))

    text = "\n".join(lines)
    metadata = {
        "device_type": str(record.get("device_type") or "generic"),
        "issue": str(record.get("issue") or "general"),
        "risk_level": str(record.get("risk_level") or "low"),
        "source_type": str(record.get("source_type") or "repair_guide"),
        "brand": str(record.get("brand") or "generic"),
        "chunk_id": rid,
    }
    return {"id": rid, "text": text, "metadata": metadata}
