import { useCallback, useMemo, useState } from "react";
import ChatBox from "./components/ChatBox.jsx";
import DeviceSelector from "./components/DeviceSelector.jsx";
import { postChat } from "./utils/api.js";

function getOrCreateSessionId() {
  const k = "repairbot_session_id";
  let id = localStorage.getItem(k);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(k, id);
  }
  return id;
}

export default function App() {
  const [sessionId] = useState(() => getOrCreateSessionId());
  const [deviceType, setDeviceType] = useState("");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  const canSend = useMemo(() => input.trim().length > 0 && !busy, [input, busy]);

  const send = useCallback(
    async (rawText) => {
      const text = (rawText ?? input).trim();
      if (!text || busy) return;
      setError(null);
      setInput("");
      setMessages((m) => [...m, { role: "user", text }]);
      setBusy(true);
      try {
        const res = await postChat(sessionId, text, deviceType || null);
        setMessages((m) => [
          ...m,
          {
            role: "assistant",
            text: res.reply,
            structured: res.structured ?? null,
            meta: {
              issue_type: res.issue_type,
              risk_level: res.risk_level,
              safety_escalation: res.safety_escalation,
              needs_followup: res.needs_followup,
            },
          },
        ]);
      } catch (e) {
        setError(e.message || String(e));
        setMessages((m) => [
          ...m,
          {
            role: "assistant",
            text: "Sorry — could not reach the repair API. Is the backend running on port 8000?",
            structured: null,
            meta: {},
          },
        ]);
      } finally {
        setBusy(false);
      }
    },
    [busy, deviceType, input, sessionId],
  );

  function newSession() {
    localStorage.removeItem("repairbot_session_id");
    window.location.reload();
  }

  return (
    <div className="app-root">
      <div className="app-bg" aria-hidden />
      <header className="app-header">
        <div className="app-header__brand">
          <div className="logo-mark" aria-hidden>
            <svg viewBox="0 0 40 40" width="40" height="40">
              <rect x="6" y="4" width="18" height="32" rx="4" fill="none" stroke="currentColor" strokeWidth="2" />
              <path d="M26 12 L38 4 L36 20 Z" fill="currentColor" opacity="0.35" />
            </svg>
          </div>
          <div>
            <h1 className="app-header__title">Repair assistant</h1>
            <p className="app-header__tagline">Grounded troubleshooting for phones &amp; laptops</p>
          </div>
        </div>
        <button type="button" className="btn-ghost" onClick={newSession}>
          New chat
        </button>
      </header>

      <main className="app-main">
        <aside className="app-sidebar">
          <DeviceSelector value={deviceType} onChange={setDeviceType} />
          <div className="sidebar-card">
            <div className="sidebar-card__title">How it works</div>
            <ol className="sidebar-steps">
              <li>Describe the problem</li>
              <li>We retrieve repair guides</li>
              <li>Safe steps &amp; escalation when needed</li>
            </ol>
          </div>
          <div className="sidebar-note">
            Not a substitute for a technician when you see smoke, swelling, burns, or major liquid damage.
          </div>
        </aside>

        <section className="app-chat-column">
          <ChatBox
            messages={messages}
            sessionId={sessionId}
            busy={busy}
            onPickSuggestion={(s) => send(s)}
          />

          {error && <div className="banner-error">{error}</div>}

          <div className="composer">
            <textarea
              className="composer__input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  send();
                }
              }}
              placeholder="Describe what happened — e.g. phone gets warm when charging…"
              rows={1}
              style={{ minHeight: "52px", maxHeight: "160px" }}
              onInput={(e) => {
                const t = e.target;
                t.style.height = "auto";
                t.style.height = `${Math.min(t.scrollHeight, 160)}px`;
              }}
            />
            <button type="button" className="composer__send" disabled={!canSend} onClick={() => send()} aria-label="Send">
              <span className="composer__send-icon" aria-hidden>
                ➤
              </span>
            </button>
          </div>
        </section>
      </main>
    </div>
  );
}
