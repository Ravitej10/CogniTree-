// TreeMotif.jsx
// The signature visual: a branching knowledge tree where each node is a
// sub-topic. Green nodes = mastered, amber nodes = a diagnosed gap.
// This isn't decoration — it's the same visual language used for the
// diagnostic matrix elsewhere in the product, so it should stay consistent.

export default function TreeMotif({ className = "", animate = true }) {
  return (
    <svg
      viewBox="0 0 400 520"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      role="img"
      aria-label="Branching diagram representing mapped and unmapped knowledge topics"
    >
      <g className={animate ? "ct-sway" : ""}>
        {/* Trunk */}
        <path
          d="M200 500 L200 340"
          stroke="#8B9A8C"
          strokeWidth="3"
          strokeLinecap="round"
        />

        {/* Primary branches */}
        <path d="M200 340 L140 280" stroke="#8B9A8C" strokeWidth="2.5" strokeLinecap="round" />
        <path d="M200 340 L200 260" stroke="#8B9A8C" strokeWidth="2.5" strokeLinecap="round" />
        <path d="M200 340 L260 280" stroke="#8B9A8C" strokeWidth="2.5" strokeLinecap="round" />

        {/* Secondary branches — left cluster */}
        <path d="M140 280 L100 220" stroke="#8B9A8C" strokeWidth="2" strokeLinecap="round" />
        <path d="M140 280 L160 220" stroke="#8B9A8C" strokeWidth="2" strokeLinecap="round" />

        {/* Secondary branches — center cluster */}
        <path d="M200 260 L200 200" stroke="#8B9A8C" strokeWidth="2" strokeLinecap="round" />
        <path d="M200 200 L170 150" stroke="#8B9A8C" strokeWidth="1.75" strokeLinecap="round" />
        <path d="M200 200 L230 150" stroke="#8B9A8C" strokeWidth="1.75" strokeLinecap="round" />

        {/* Secondary branches — right cluster */}
        <path d="M260 280 L240 220" stroke="#8B9A8C" strokeWidth="2" strokeLinecap="round" />
        <path d="M260 280 L300 220" stroke="#8B9A8C" strokeWidth="2" strokeLinecap="round" />

        {/* Root node */}
        <circle cx="200" cy="340" r="7" fill="#F7F8F4" stroke="#8B9A8C" strokeWidth="2.5" />

        {/* Mid-level nodes */}
        <circle cx="140" cy="280" r="6" fill="#2F6B4F" />
        <circle cx="200" cy="260" r="6" fill="#2F6B4F" />
        <circle cx="260" cy="280" r="6" fill="#E2A73E" />

        {/* Leaf nodes (topics) */}
        <circle cx="100" cy="220" r="9" fill="#E2A73E" />
        <circle cx="160" cy="220" r="9" fill="#2F6B4F" />
        <circle cx="170" cy="150" r="8" fill="#2F6B4F" />
        <circle cx="230" cy="150" r="8" fill="#E2A73E" />
        <circle cx="240" cy="220" r="9" fill="#2F6B4F" />
        <circle cx="300" cy="220" r="9" fill="#E2A73E" />
      </g>

      <style>{`
        @media (prefers-reduced-motion: no-preference) {
          .ct-sway {
            transform-origin: 200px 500px;
            animation: ct-sway 7s ease-in-out infinite;
          }
        }
        @keyframes ct-sway {
          0%, 100% { transform: rotate(-0.6deg); }
          50% { transform: rotate(0.6deg); }
        }
      `}</style>
    </svg>
  );
}
