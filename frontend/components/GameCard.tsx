import Link from "next/link";
import { GameScoreBadge } from "@/components/GameScoreBadge";
import type { GameListItem, League } from "@/lib/types";

interface GameCardProps {
  league: League;
  game: GameListItem;
}

export function GameCard({ league, game }: GameCardProps) {
  return (
    <Link
      href={`/${league}/game/${game.id}`}
      className="flex items-center gap-4 rounded-lg border border-border bg-surface p-4 transition-colors hover:border-accent"
    >
      <GameScoreBadge score={game.game_score} size="sm" />
      <div className="flex-1">
        <div className="font-medium">
          {game.away_team.short_name} @ {game.home_team.short_name}
          {game.is_playoff && (
            <span className="ml-2 rounded-full bg-accent/20 px-2 py-0.5 text-xs text-accent">
              Playoffs
            </span>
          )}
        </div>
        <div className="text-sm text-muted-foreground">
          {game.away_score}–{game.home_score} · {new Date(game.date).toLocaleDateString()}
        </div>
      </div>
    </Link>
  );
}
