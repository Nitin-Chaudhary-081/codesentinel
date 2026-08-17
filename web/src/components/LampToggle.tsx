"use client";

export default function LampToggle({
  on,
  onToggle,
}: {
  on: boolean;
  onToggle: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onToggle}
      aria-label={on ? "Turn lamp off" : "Turn lamp on"}
      aria-pressed={on}
      className="group mb-4 flex flex-col items-center cursor-pointer outline-none focus-visible:ring-2 focus-visible:ring-amber-400 rounded-lg"
    >
      <svg
        width="120"
        height="170"
        viewBox="0 0 120 170"
        role="img"
        aria-label={on ? "Lamp is on" : "Lamp is off"}
        className="lamp-svg"
      >
        <defs>
          <radialGradient id="lamp-glow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#fde68a" stopOpacity="0.85" />
            <stop offset="60%" stopColor="#f59e0b" stopOpacity="0.25" />
            <stop offset="100%" stopColor="#f59e0b" stopOpacity="0" />
          </radialGradient>
          <linearGradient id="shade-on" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#fbbf24" />
            <stop offset="100%" stopColor="#d97706" />
          </linearGradient>
          <linearGradient id="shade-off" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#475569" />
            <stop offset="100%" stopColor="#1e293b" />
          </linearGradient>
        </defs>

        {on && <circle cx="60" cy="80" r="52" fill="url(#lamp-glow)" className="lamp-glow" />}

        {/* ceiling mount + cable */}
        <line x1="60" y1="0" x2="60" y2="30" stroke="#64748b" strokeWidth="2" />
        <path d="M48 0 H72 L69 8 H51 Z" fill="#334155" />

        {/* shade */}
        <path
          d="M40 30 L80 30 L94 64 L26 64 Z"
          fill={on ? "url(#shade-on)" : "url(#shade-off)"}
          stroke="#1e293b"
          strokeWidth="2"
        />
        <line x1="60" y1="30" x2="60" y2="64" stroke="#fef3c7" strokeWidth="1.5" opacity="0.5" />

        {/* bulb */}
        <ellipse
          cx="60"
          cy="84"
          rx="16"
          ry="20"
          fill={on ? "#fef3c7" : "#64748b"}
          stroke="#1e293b"
          strokeWidth="1.5"
        />
        {on && (
          <ellipse
            cx="60"
            cy="84"
            rx="16"
            ry="20"
            fill="none"
            stroke="#fde68a"
            strokeWidth="1.5"
            className="lamp-glow-ring"
          />
        )}

        {/* pull-cord rope */}
        <line
          x1="60"
          y1="106"
          x2="60"
          y2={on ? "134" : "138"}
          stroke="#a16207"
          strokeWidth="2.5"
          className="lamp-rope"
        />
        <circle
          cx="60"
          cy={on ? "140" : "144"}
          r="6"
          fill="#78350f"
          stroke="#451a03"
          strokeWidth="1.5"
          className="lamp-rope"
        />
      </svg>

      <span
        className={`mt-1 text-xs ${
          on ? "text-amber-500" : "text-gray-500"
        } group-hover:text-gray-300 transition-colors`}
      >
        {on ? "Pull cord to switch off" : "Pull cord to switch on"}
      </span>
    </button>
  );
}
