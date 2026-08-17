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
      className="group relative cursor-pointer outline-none focus-visible:ring-2 focus-visible:ring-amber-400/70 rounded-xl"
    >
      <span className={`lamp-wrap block transition-opacity duration-700 ${on ? "opacity-100" : "opacity-60"}`}>
        <svg
          width="200"
          height="240"
          viewBox="0 0 200 240"
          role="img"
          aria-label={on ? "Lamp is on" : "Lamp is off"}
          className="lamp-svg"
        >
          <defs>
            <linearGradient id="brass" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stopColor="#d4a017" />
              <stop offset="0.45" stopColor="#9c6b12" />
              <stop offset="1" stopColor="#5b3a0d" />
            </linearGradient>
            <linearGradient id="brassShade" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stopColor="#e3b84f" />
              <stop offset="0.5" stopColor="#a8791a" />
              <stop offset="1" stopColor="#6b4a10" />
            </linearGradient>
            <radialGradient id="bulbOn" cx="0.5" cy="0.45" r="0.6">
              <stop offset="0" stopColor="#fff7d6" />
              <stop offset="0.6" stopColor="#fde68a" />
              <stop offset="1" stopColor="#f59e0b" />
            </radialGradient>
            <radialGradient id="bulbOff" cx="0.5" cy="0.5" r="0.5">
              <stop offset="0" stopColor="#6b7280" />
              <stop offset="1" stopColor="#374151" />
            </radialGradient>
            <radialGradient id="halo" cx="0.5" cy="0.5" r="0.5">
              <stop offset="0" stopColor="#fde68a" stopOpacity="0.9" />
              <stop offset="0.55" stopColor="#f59e0b" stopOpacity="0.35" />
              <stop offset="1" stopColor="#f59e0b" stopOpacity="0" />
            </radialGradient>
          </defs>

          {on && <circle cx="100" cy="150" r="95" fill="url(#halo)" className="lamp-glow" />}

          {/* ceiling mount */}
          <ellipse cx="100" cy="10" rx="26" ry="7" fill="url(#brass)" stroke="#2b1d08" strokeWidth="1.5" />
          <rect x="94" y="10" width="12" height="6" fill="url(#brass)" />

          {/* cable */}
          <line x1="100" y1="16" x2="100" y2="62" stroke={on ? "#8a8f98" : "#4b4f57"} strokeWidth="2.5" />
          <circle cx="100" cy="22" r="2.5" fill="#5b5f66" />
          <circle cx="100" cy="34" r="2.5" fill="#5b5f66" />

          {/* shade */}
          <g className="lamp-shade-group">
            <path d="M100 62 L66 132 L134 132 Z" fill="#241505" />
            <path d="M100 62 L62 134 L138 134 Z" fill="url(#brassShade)" stroke="#2b1d08" strokeWidth="1.5" />
            <ellipse cx="100" cy="134" rx="38" ry="5" fill="#7a5612" stroke="#2b1d08" strokeWidth="1" />
            <path d="M104 62 L72 128" stroke="#ffd97a" strokeWidth="3" opacity="0.35" strokeLinecap="round" />
          </g>

          {/* bulb */}
          <g>
            <ellipse cx="100" cy="150" rx="19" ry="24" fill={on ? "url(#bulbOn)" : "url(#bulbOff)"} stroke="#1a1a1a" strokeWidth="1" />
            {on && (
              <ellipse cx="100" cy="150" rx="19" ry="24" fill="none" stroke="#fde68a" strokeWidth="1.5" className="lamp-glow-ring" />
            )}
            {on && (
              <path
                d="M92 148 q4 -4 8 0 q4 -4 8 0"
                stroke="#fff3c4"
                strokeWidth="1.6"
                fill="none"
                strokeLinecap="round"
                className="lamp-filament"
              />
            )}
          </g>

          {/* pull-cord rope */}
          <g className="lamp-rope" style={{ transformOrigin: "100px 176px" }}>
            <line x1="100" y1="176" x2="100" y2={on ? "206" : "214"} stroke="#7a5612" strokeWidth="2" />
            <circle cx="100" cy={on ? "214" : "222"} r="6.5" fill="#8a5a12" stroke="#2b1d08" strokeWidth="1.5" />
            <circle cx="98.5" cy={on ? "212.5" : "220.5"} r="2" fill="#e3b84f" opacity="0.7" />
          </g>
        </svg>
      </span>
    </button>
  );
}
