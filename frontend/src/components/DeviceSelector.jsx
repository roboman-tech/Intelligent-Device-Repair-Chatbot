const OPTIONS = [
  { value: "", label: "Auto", icon: "✦" },
  { value: "mobile", label: "Phone", icon: "📱" },
  { value: "laptop", label: "Laptop", icon: "💻" },
  { value: "tablet", label: "Tablet", icon: "📋" },
  { value: "desktop", label: "Desktop", icon: "🖥" },
];

export default function DeviceSelector({ value, onChange }) {
  return (
    <div className="device-selector">
      <span className="device-selector__label">Device hint</span>
      <div className="device-selector__pills" role="group" aria-label="Device type hint">
        {OPTIONS.map((o) => (
          <button
            key={o.value || "auto"}
            type="button"
            className={`device-pill ${value === o.value ? "device-pill--active" : ""}`}
            onClick={() => onChange(o.value)}
          >
            <span className="device-pill__icon" aria-hidden>
              {o.icon}
            </span>
            {o.label}
          </button>
        ))}
      </div>
    </div>
  );
}
