function hasStructuredContent(s) {
  if (!s || typeof s !== "object") return false;
  return Boolean(
    (s.issue_summary && String(s.issue_summary).trim()) ||
      (Array.isArray(s.followup_questions) && s.followup_questions.length) ||
      (Array.isArray(s.likely_causes) && s.likely_causes.length) ||
      (Array.isArray(s.steps) && s.steps.length) ||
      (Array.isArray(s.warnings) && s.warnings.length),
  );
}

/**
 * Turn API `structured` JSON or plain `reply` text into renderable blocks.
 */
export function getAssistantBlocks(text, structured) {
  if (hasStructuredContent(structured)) {
    return { kind: "structured", structured };
  }
  return { kind: "text", blocks: parsePlainReply(text || "") };
}

function parsePlainReply(text) {
  const blocks = [];
  const chunks = text.split(/\n\n+/).map((s) => s.trim()).filter(Boolean);

  for (const chunk of chunks) {
    const lower = chunk.slice(0, 40).toLowerCase();
    if (chunk.startsWith("A few quick questions:")) {
      const lines = chunk.split("\n").slice(1).map((l) => l.replace(/^-\s*/, "").trim()).filter(Boolean);
      blocks.push({ type: "questions", lines });
      continue;
    }
    if (lower.startsWith("likely causes:")) {
      const rest = chunk.replace(/^likely causes:\s*/i, "").trim();
      blocks.push({ type: "causes", text: rest });
      continue;
    }
    if (lower.startsWith("suggested steps:")) {
      const lines = chunk.split("\n").slice(1).map((l) => l.trim()).filter(Boolean);
      blocks.push({ type: "steps", lines: lines.length ? lines : [chunk.replace(/^suggested steps:\s*/i, "").trim()] });
      continue;
    }
    if (lower.startsWith("warnings:")) {
      const rest = chunk.replace(/^warnings:\s*/i, "").trim();
      blocks.push({ type: "warnings", text: rest });
      continue;
    }
    if (/^\d+\.\s/.test(chunk.split("\n")[0])) {
      const lines = chunk.split("\n").map((l) => l.trim()).filter(Boolean);
      blocks.push({ type: "steps", lines });
      continue;
    }
    blocks.push({ type: "paragraph", text: chunk });
  }
  return blocks;
}
