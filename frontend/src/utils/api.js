export async function postChat(sessionId, message, deviceType) {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      message,
      device_type: deviceType || null,
    }),
  });
  if (!res.ok) {
    const t = await res.text();
    throw new Error(t || res.statusText);
  }
  return res.json();
}

export async function postFeedback(sessionId, helpful, comment) {
  const res = await fetch("/api/feedback", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      helpful,
      comment: comment || null,
    }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
