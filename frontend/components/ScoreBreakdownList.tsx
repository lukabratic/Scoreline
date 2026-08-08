interface ScoreBreakdownListProps {
  breakdown: string[] | null;
  className?: string;
}

export function ScoreBreakdownList({ breakdown, className }: ScoreBreakdownListProps) {
  if (!breakdown || breakdown.length === 0) {
    return <p className={`text-sm text-muted-foreground ${className ?? ""}`}>No breakdown available.</p>;
  }

  return (
    <ul className={`flex flex-col gap-1 text-sm ${className ?? ""}`}>
      {breakdown.map((reason) => (
        <li key={reason} className="flex items-start gap-2">
          <span className="mt-1.5 h-1 w-1 flex-shrink-0 rounded-full bg-accent" />
          <span>{reason}</span>
        </li>
      ))}
    </ul>
  );
}
