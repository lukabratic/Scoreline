"use client";

import { useMemo, useState } from "react";
import { SeasonArcGraph } from "@/components/SeasonArcGraph";
import type { GameListItem, Team } from "@/lib/types";

type HomeAway = "all" | "home" | "away";

interface Opponent {
  id: number;
  short_name: string;
}

function monthKey(date: string): string {
  return date.slice(0, 7);
}

function monthLabel(key: string): string {
  const [year, month] = key.split("-").map(Number);
  return new Date(year, month - 1, 1).toLocaleDateString(undefined, {
    month: "long",
    year: "numeric",
  });
}

export function SeasonFilters({ team, games }: { team: Team; games: GameListItem[] }) {
  const [homeAway, setHomeAway] = useState<HomeAway>("all");
  const [opponentId, setOpponentId] = useState<number | "all">("all");
  const [month, setMonth] = useState<string>("all");

  const opponents = useMemo(() => {
    const seen = new Map<number, Opponent>();
    for (const game of games) {
      const isHome = game.home_team.id === team.id;
      const opponent = isHome ? game.away_team : game.home_team;
      seen.set(opponent.id, { id: opponent.id, short_name: opponent.short_name });
    }
    return [...seen.values()].sort((a, b) => a.short_name.localeCompare(b.short_name));
  }, [games, team.id]);

  const months = useMemo(() => {
    const keys = new Set(games.map((g) => monthKey(g.date)));
    return [...keys].sort();
  }, [games]);

  const filtered = useMemo(() => {
    return games.filter((game) => {
      const isHome = game.home_team.id === team.id;
      if (homeAway === "home" && !isHome) return false;
      if (homeAway === "away" && isHome) return false;

      const opponent = isHome ? game.away_team : game.home_team;
      if (opponentId !== "all" && opponent.id !== opponentId) return false;

      if (month !== "all" && monthKey(game.date) !== month) return false;

      return true;
    });
  }, [games, team.id, homeAway, opponentId, month]);

  const selectClass =
    "rounded-lg border border-border bg-surface px-3 py-1.5 text-sm text-foreground outline-none focus:border-accent";

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap gap-3">
        <select
          value={homeAway}
          onChange={(e) => setHomeAway(e.target.value as HomeAway)}
          className={selectClass}
        >
          <option value="all">Home & away</option>
          <option value="home">Home only</option>
          <option value="away">Away only</option>
        </select>

        <select
          value={opponentId}
          onChange={(e) => setOpponentId(e.target.value === "all" ? "all" : Number(e.target.value))}
          className={selectClass}
        >
          <option value="all">All opponents</option>
          {opponents.map((opponent) => (
            <option key={opponent.id} value={opponent.id}>
              {opponent.short_name}
            </option>
          ))}
        </select>

        <select value={month} onChange={(e) => setMonth(e.target.value)} className={selectClass}>
          <option value="all">All months</option>
          {months.map((key) => (
            <option key={key} value={key}>
              {monthLabel(key)}
            </option>
          ))}
        </select>
      </div>

      <SeasonArcGraph team={team} games={filtered} />
    </div>
  );
}
