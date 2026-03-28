import { useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble.jsx";
import FeedbackButtons from "./FeedbackButtons.jsx";

const SUGGESTIONS = [
  "My phone won't charge",
  "Laptop gets hot and shuts down",
  "Black screen but phone vibrates",
  "Wi‑Fi keeps disconnecting",
];

export default function ChatBox({ messages, sessionId, busy, onPickSuggestion }) {
  const endRef = useRef(null);
  const scrollRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, busy]);

  const lastAssistant = [...messages].reverse().find((m) => m.role === "assistant");

  return (
    <div className="chat-panel" ref={scrollRef}>
      <div className="chat-panel__inner">
        {messages.length === 0 && (
          <div className="empty-state">
            <div className="empty-state__hero">
              <div className="empty-state__glow" />
              <div className="empty-state__icon" aria-hidden>
                <svg viewBox="0 0 120 120" width="100" height="100">
                  <rect
                    x="28"
                    y="22"
                    width="44"
                    height="76"
                    rx="8"
                    fill="none"
                    stroke="url(#phoneGrad)"
                    strokeWidth="3"
                  />
                  <rect x="38" y="32" width="24" height="40" rx="2" fill="url(#phoneGrad)" opacity="0.15" />
                  <circle cx="50" cy="82" r="3" fill="var(--accent)" opacity="0.8" />
                  <path
                    d="M78 38 L102 22 L98 48 Z"
                    fill="none"
                    stroke="var(--accent-2)"
                    strokeWidth="2.5"
                    strokeLinejoin="round"
                  />
                  <defs>
                    <linearGradient id="phoneGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stopColor="var(--accent)" />
                      <stop offset="100%" stopColor="var(--accent-2)" />
                    </linearGradient>
                  </defs>
                </svg>
              </div>
            </div>
            <h2 className="empty-state__title">What&apos;s going wrong?</h2>
            <p className="empty-state__sub">
              Describe your device in plain language. We&apos;ll ask a few focused questions when needed and
              ground answers in repair guides.
            </p>
            <div className="suggestion-grid">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  type="button"
                  className="suggestion-chip"
                  onClick={() => onPickSuggestion?.(s)}
                >
                  <span className="suggestion-chip__icon">→</span>
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <MessageBubble
            key={i}
            role={m.role}
            text={m.text}
            meta={m.meta}
            structured={m.structured}
          />
        ))}

        {busy && (
          <div className="typing-row">
            <div className="typing-avatar" />
            <div className="typing-bubble">
              <span className="typing-dot" />
              <span className="typing-dot" />
              <span className="typing-dot" />
              <span className="typing-label">Analyzing &amp; retrieving guides…</span>
            </div>
          </div>
        )}

        <div ref={endRef} />

        {lastAssistant && !busy && (
          <div className="feedback-bar">
            <FeedbackButtons sessionId={sessionId} disabled={busy} />
          </div>
        )}
      </div>
    </div>
  );
}
