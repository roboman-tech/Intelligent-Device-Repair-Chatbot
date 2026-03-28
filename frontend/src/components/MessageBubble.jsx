import AssistantMessage from "./AssistantMessage.jsx";

export default function MessageBubble({ role, text, meta, structured }) {
  const isUser = role === "user";

  if (!isUser) {
    return (
      <div className="message-row message-row--assistant">
        <AssistantMessage text={text} structured={structured} meta={meta} />
      </div>
    );
  }

  return (
    <div className="message-row message-row--user">
      <div className="user-wrap">
        <div className="user-bubble">
          <div className="user-bubble__label">You</div>
          <p className="user-bubble__text">{text}</p>
        </div>
        <div className="user-avatar" aria-hidden>
          <svg viewBox="0 0 32 32" width="32" height="32">
            <circle cx="16" cy="12" r="6" fill="currentColor" opacity="0.85" />
            <path
              fill="currentColor"
              opacity="0.85"
              d="M8 26c0-4 3.5-7 8-7s8 3 8 7v1H8v-1z"
            />
          </svg>
        </div>
      </div>
    </div>
  );
}
