"use client";

import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { DotItemDotProps } from "recharts/types/util/types";
import { GameScoreBadge } from "@/components/GameScoreBadge";
import { ScoreBreakdownList } from "@/components/ScoreBreakdownList";
import type { GameListItem, Team } from "@/lib/types";

interface SeasonArcGraphProps {
  team: Team;
  games: GameListItem[];
}

function opponentAndResult(game: GameListItem, teamId: number) {
  const isHome = game.home_team.id === teamId;
  const opponent = isHome ? game.away_team : game.home_team;
  const teamScore = isHome ? game.home_score : game.away_score;
  const opponentScore = isHome ? game.away_score : game.home_score;
  return { isHome, opponent, teamScore, opponentScore };
}

function GraphDot(props: DotItemDotProps) {
  const { cx, cy, payload } = props;
  if (cx === undefined || cy === undefined || payload.game_score === null) return null;

  const isPlayoff = (payload as GameListItem).is_playoff;
  return (
    <circle
      cx={cx}
      cy={cy}
      r={isPlayoff ? 5 : 3.5}
      fill={isPlayoff ? "var(--color-accent)" : "var(--color-background)"}
      stroke="var(--color-accent)"
      strokeWidth={2}
    />
  );
}

function CommunityDot(props: DotItemDotProps) {
  const { cx, cy, payload } = props;
  if (cx === undefined || cy === undefined || (payload as GameListItem).community_score === null) {
    return null;
  }
  return (
    <circle
      cx={cx}
      cy={cy}
      r={3}
      fill="var(--color-community)"
      stroke="var(--color-background)"
      strokeWidth={1.5}
    />
  );
}

function GraphTooltip({
  active,
  payload,
  teamId,
}: {
  active?: boolean;
  payload?: { payload: GameListItem }[];
  teamId: number;
}) {
  if (!active || !payload || payload.length === 0) return null;
  const game = payload[0].payload;
  const { isHome, opponent, teamScore, opponentScore } = opponentAndResult(game, teamId);

  return (
    <div className="max-w-xs rounded-lg border border-border bg-surface p-3 shadow-lg">
      <div className="mb-2 flex items-center gap-3">
        <GameScoreBadge score={game.game_score} size="sm" />
        <div className="text-sm">
          <div className="font-medium">
            {isHome ? "vs" : "@"} {opponent.short_name}
          </div>
          <div className="text-muted-foreground">
            {teamScore}–{opponentScore} · {new Date(game.date).toLocaleDateString()}
            {game.is_playoff ? " · Playoffs" : ""}
          </div>
        </div>
      </div>
      <ScoreBreakdownList breakdown={game.game_score_breakdown} />
      <p className="mt-2 text-xs text-muted-foreground">
        {game.community_score !== null
          ? `Community: ${game.community_score.toFixed(1)} (${game.community_rating_count} rating${
              game.community_rating_count === 1 ? "" : "s"
            })`
          : "No community ratings yet"}
      </p>
    </div>
  );
}

export function SeasonArcGraph({ team, games }: SeasonArcGraphProps) {
  const points = games.filter((g) => g.game_score !== null);

  if (points.length === 0) {
    return (
      <p className="py-16 text-center text-muted-foreground">
        No scored games yet for {team.name} this season.
      </p>
    );
  }

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center gap-4 text-xs text-muted-foreground">
        <span className="flex items-center gap-1.5">
          <span className="h-0.5 w-3 rounded-full" style={{ backgroundColor: "var(--color-accent)" }} />
          Game Score
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-0.5 w-3 rounded-full" style={{ backgroundColor: "var(--color-community)" }} />
          Community
        </span>
      </div>
      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={points} margin={{ top: 16, right: 16, bottom: 0, left: -16 }}>
            <XAxis
              dataKey="date"
              tickFormatter={(value: string) =>
                new Date(value).toLocaleDateString(undefined, { month: "short", day: "numeric" })
              }
              stroke="var(--color-muted-foreground)"
              fontSize={12}
              tickLine={false}
            />
            <YAxis
              domain={[0, 10]}
              stroke="var(--color-muted-foreground)"
              fontSize={12}
              tickLine={false}
              axisLine={false}
              width={28}
            />
            <Tooltip
              content={(props) => (
                <GraphTooltip
                  active={props.active}
                  payload={props.payload as unknown as { payload: GameListItem }[] | undefined}
                  teamId={team.id}
                />
              )}
            />
            <Line
              dataKey="game_score"
              stroke="var(--color-accent)"
              strokeWidth={2}
              dot={(props) => <GraphDot key={props.index} {...props} />}
              activeDot={{ r: 6 }}
              isAnimationActive={false}
            />
            <Line
              dataKey="community_score"
              stroke="var(--color-community)"
              strokeWidth={2}
              strokeDasharray="4 3"
              dot={(props) => <CommunityDot key={props.index} {...props} />}
              activeDot={{ r: 5 }}
              connectNulls={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
