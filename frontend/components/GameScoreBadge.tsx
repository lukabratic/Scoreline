const SIZES = {
  sm: { diameter: 40, stroke: 4, fontSize: 12 },
  md: { diameter: 64, stroke: 5, fontSize: 18 },
  lg: { diameter: 96, stroke: 6, fontSize: 26 },
} as const;

interface GameScoreBadgeProps {
  score: number | null;
  size?: keyof typeof SIZES;
}

export function GameScoreBadge({ score, size = "md" }: GameScoreBadgeProps) {
  const { diameter, stroke, fontSize } = SIZES[size];
  const radius = (diameter - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const clamped = score === null ? 0 : Math.max(0, Math.min(10, score));
  const dashoffset = circumference * (1 - clamped / 10);

  return (
    <div
      className="relative inline-flex items-center justify-center"
      style={{ width: diameter, height: diameter }}
      role="img"
      aria-label={score === null ? "Game Score not yet available" : `Game Score ${score.toFixed(1)} out of 10`}
    >
      <svg width={diameter} height={diameter} className="-rotate-90">
        <circle
          cx={diameter / 2}
          cy={diameter / 2}
          r={radius}
          fill="none"
          stroke="var(--color-border)"
          strokeWidth={stroke}
        />
        {score !== null && (
          <circle
            cx={diameter / 2}
            cy={diameter / 2}
            r={radius}
            fill="none"
            stroke="var(--color-accent)"
            strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={dashoffset}
          />
        )}
      </svg>
      <span
        className="absolute font-semibold tabular-nums text-foreground"
        style={{ fontSize }}
      >
        {score === null ? "—" : score.toFixed(1)}
      </span>
    </div>
  );
}
