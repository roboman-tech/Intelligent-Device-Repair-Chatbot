import { getAssistantBlocks } from "../utils/formatAssistantReply.js";

function RiskBadge({ level, safety }) {
  const lv = (level || "low").toLowerCase();
  const cls =
    safety || lv === "high"
      ? "risk-pill risk-pill--high"
      : lv === "medium"
        ? "risk-pill risk-pill--medium"
        : "risk-pill risk-pill--low";
  const label = safety ? "Safety" : `Risk · ${lv}`;
  return <span className={cls}>{label}</span>;
}

function StructuredView({ s }) {
  return (
    <div className="assistant-structured">
      {s.issue_summary && (
        <div className="assistant-card assistant-card--summary">
          <div className="assistant-card__label">Summary</div>
          <p className="assistant-card__body">{s.issue_summary}</p>
        </div>
      )}
      {s.needs_followup && Array.isArray(s.followup_questions) && s.followup_questions.length > 0 && (
        <div className="assistant-card assistant-card--questions">
          <div className="assistant-card__label">Follow-up</div>
          <ul className="assistant-list assistant-list--dots">
            {s.followup_questions.slice(0, 4).map((q, i) => (
              <li key={i}>{q}</li>
            ))}
          </ul>
        </div>
      )}
      {Array.isArray(s.likely_causes) && s.likely_causes.length > 0 && (
        <div className="assistant-card assistant-card--causes">
          <div className="assistant-card__label">Likely causes</div>
          <div className="cause-chips">
            {s.likely_causes.slice(0, 8).map((c, i) => (
              <span key={i} className="cause-chip">
                {c}
              </span>
            ))}
          </div>
        </div>
      )}
      {Array.isArray(s.steps) && s.steps.length > 0 && (
        <div className="assistant-card assistant-card--steps">
          <div className="assistant-card__label">Steps</div>
          <ol className="step-list">
            {s.steps.slice(0, 16).map((step, i) => (
              <li key={i}>
                <span className="step-list__num">{i + 1}</span>
                <span className="step-list__text">{String(step).replace(/^\d+\s*[\.)]\s*/, "")}</span>
              </li>
            ))}
          </ol>
        </div>
      )}
      {Array.isArray(s.warnings) && s.warnings.length > 0 && (
        <div className="assistant-callout assistant-callout--warn">
          <div className="assistant-callout__title">Warnings</div>
          <ul className="assistant-list">
            {s.warnings.slice(0, 6).map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function TextBlocksView({ blocks }) {
  return (
    <div className="assistant-text-blocks">
      {blocks.map((b, i) => {
        if (b.type === "questions") {
          return (
            <div key={i} className="assistant-card assistant-card--questions">
              <div className="assistant-card__label">Questions</div>
              <ul className="assistant-list assistant-list--dots">
                {b.lines.map((l, j) => (
                  <li key={j}>{l}</li>
                ))}
              </ul>
            </div>
          );
        }
        if (b.type === "causes") {
          const parts = b.text.split(/[;•]/).map((s) => s.trim()).filter(Boolean);
          return (
            <div key={i} className="assistant-card assistant-card--causes">
              <div className="assistant-card__label">Likely causes</div>
              <div className="cause-chips">
                {(parts.length ? parts : [b.text]).slice(0, 10).map((c, j) => (
                  <span key={j} className="cause-chip">
                    {c}
                  </span>
                ))}
              </div>
            </div>
          );
        }
        if (b.type === "steps") {
          return (
            <div key={i} className="assistant-card assistant-card--steps">
              <div className="assistant-card__label">Suggested steps</div>
              <ol className="step-list">
                {b.lines.map((line, j) => (
                  <li key={j}>
                    <span className="step-list__num">{j + 1}</span>
                    <span className="step-list__text">{line.replace(/^\d+\s*[\.)]\s*/, "")}</span>
                  </li>
                ))}
              </ol>
            </div>
          );
        }
        if (b.type === "warnings") {
          return (
            <div key={i} className="assistant-callout assistant-callout--warn">
              <div className="assistant-callout__title">Warnings</div>
              <p className="assistant-callout__p">{b.text}</p>
            </div>
          );
        }
        return (
          <p key={i} className="assistant-paragraph">
            {b.text}
          </p>
        );
      })}
    </div>
  );
}

export default function AssistantMessage({ text, structured, meta }) {
  const data = getAssistantBlocks(text, structured);
  const showRisk = meta?.issue_type || meta?.risk_level || meta?.safety_escalation;

  return (
    <div className="assistant-wrap">
      <div className="assistant-avatar" aria-hidden>
        <svg viewBox="0 0 32 32" width="36" height="36" className="assistant-avatar__svg">
          <circle cx="16" cy="16" r="15" className="assistant-avatar__ring" />
          <path
            className="assistant-avatar__figure"
            d="M16 8a4 4 0 1 1 0 8 4 4 0 0 1 0-8zm-6 14c0-2 2.5-4 6-4s6 2 6 4v2H10v-2z"
          />
        </svg>
      </div>
      <div className="assistant-bubble">
        <div className="assistant-bubble__toolbar">
          <span className="assistant-bubble__title">Repair assistant</span>
          {showRisk && (
            <div className="assistant-bubble__meta">
              {meta?.issue_type && <span className="issue-chip">{meta.issue_type}</span>}
              <RiskBadge level={meta?.risk_level} safety={meta?.safety_escalation} />
            </div>
          )}
        </div>
        <div className="assistant-bubble__body">
          {data.kind === "structured" ? (
            <StructuredView s={data.structured} />
          ) : data.blocks.length > 0 ? (
            <TextBlocksView blocks={data.blocks} />
          ) : (
            <p className="assistant-paragraph">{text}</p>
          )}
        </div>
      </div>
    </div>
  );
}
