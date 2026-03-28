import { useState } from "react";
import { postFeedback } from "../utils/api";

export default function FeedbackButtons({ sessionId, disabled }) {
  const [sent, setSent] = useState(null);
  const [err, setErr] = useState(null);

  async function send(helpful) {
    setErr(null);
    try {
      await postFeedback(sessionId, helpful, null);
      setSent(helpful ? "up" : "down");
    } catch (e) {
      setErr(String(e.message || e));
    }
  }

  if (sent) {
    return (
      <div className="feedback-done">
        <span className="feedback-done__check">✓</span> Thanks — that helps improve answers.
      </div>
    );
  }

  return (
    <div className="feedback-row">
      <span className="feedback-row__ask">Was this helpful?</span>
      <div className="feedback-actions">
        <button
          type="button"
          className="feedback-btn feedback-btn--yes"
          disabled={disabled}
          onClick={() => send(true)}
          aria-label="Yes, helpful"
        >
          <span aria-hidden>👍</span> Yes
        </button>
        <button
          type="button"
          className="feedback-btn feedback-btn--no"
          disabled={disabled}
          onClick={() => send(false)}
          aria-label="Not helpful"
        >
          <span aria-hidden>👎</span> No
        </button>
      </div>
      {err && <span className="feedback-err">{err}</span>}
    </div>
  );
}
