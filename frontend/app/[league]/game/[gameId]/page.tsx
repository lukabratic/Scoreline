import { notFound } from "next/navigation";
import Link from "next/link";
import { getGame } from "@/lib/api";
import type { League } from "@/lib/types";
import { GameScoreBadge } from "@/components/GameScoreBadge";
import { ScoreBreakdownList } from "@/components/ScoreBreakdownList";
import { RatingWidget } from "@/components/RatingWidget";

export default async function GamePage(props: PageProps<"/[league]/game/[gameId]">) {
  const { league, gameId } = await props.params;
  const leagueSlug = league as League;

  let game;
  try {
    game = await getGame(Number(gameId));
  } catch {
    notFound();
  }

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-8 px-6 py-12">
      <div className="flex flex-col items-center gap-3 text-center">
        <div className="flex items-center gap-6">
          <TeamHeader league={leagueSlug} teamId={game.away_team.id} seasonId={game.season_id}>
            {game.away_team.short_name}
          </TeamHeader>
          <div className="text-3xl font-semibold tabular-nums">
            {game.away_score} – {game.home_score}
          </div>
          <TeamHeader league={leagueSlug} teamId={game.home_team.id} seasonId={game.season_id}>
            {game.home_team.short_name}
          </TeamHeader>
        </div>
        <p className="text-sm text-muted-foreground">
          {new Date(game.date).toLocaleDateString(undefined, {
            weekday: "long",
            month: "long",
            day: "numeric",
            year: "numeric",
          })}
          {game.is_playoff ? " · Playoffs" : ""}
        </p>
      </div>

      <div className="flex flex-col items-center gap-4 rounded-xl border border-border bg-surface p-8">
        <GameScoreBadge score={game.game_score} size="lg" />
        <ScoreBreakdownList breakdown={game.game_score_breakdown} className="max-w-sm" />
      </div>

      <RatingWidget gameId={game.id} />

      <section>
        <h2 className="mb-4 text-lg font-semibold">Key stats</h2>
        {game.nba_stats && <NBAStatsList stats={game.nba_stats} />}
        {game.epl_events.length > 0 && <EPLEventsList events={game.epl_events} game={game} />}
        {!game.nba_stats && game.epl_events.length === 0 && (
          <p className="text-muted-foreground">No detailed stats available for this game.</p>
        )}
      </section>
    </div>
  );
}

function TeamHeader({
  league,
  teamId,
  seasonId,
  children,
}: {
  league: League;
  teamId: number;
  seasonId: number;
  children: React.ReactNode;
}) {
  return (
    <Link
      href={`/${league}/team/${teamId}/season/${seasonId}`}
      className="text-xl font-semibold hover:text-accent"
    >
      {children}
    </Link>
  );
}

function NBAStatsList({
  stats,
}: {
  stats: NonNullable<Awaited<ReturnType<typeof getGame>>["nba_stats"]>;
}) {
  const rows: [string, string | number | null][] = [
    ["Lead changes", stats.lead_changes],
    ["Times tied", stats.times_tied],
    ["Largest deficit overcome", stats.largest_deficit_overcome],
    ["Overtime periods", stats.overtime_periods],
    ["Top performer points", stats.top_performer_pts],
  ];
  return (
    <dl className="grid grid-cols-2 gap-3 rounded-lg border border-border bg-surface p-4 sm:grid-cols-3">
      {rows.map(([label, value]) => (
        <div key={label}>
          <dt className="text-xs text-muted-foreground">{label}</dt>
          <dd className="text-lg font-medium tabular-nums">{value ?? "—"}</dd>
        </div>
      ))}
    </dl>
  );
}

function EPLEventsList({
  events,
  game,
}: {
  events: Awaited<ReturnType<typeof getGame>>["epl_events"];
  game: Awaited<ReturnType<typeof getGame>>;
}) {
  const label = (teamId: number) =>
    teamId === game.home_team.id ? game.home_team.short_name : game.away_team.short_name;
  const eventLabel = { goal: "Goal", penalty: "Penalty", red_card: "Red card" };

  return (
    <ul className="flex flex-col gap-2 rounded-lg border border-border bg-surface p-4">
      {[...events]
        .sort((a, b) => a.minute - b.minute)
        .map((event, i) => (
          <li key={i} className="flex justify-between text-sm">
            <span>
              {eventLabel[event.event_type]} — {label(event.team_id)}
            </span>
            <span className="tabular-nums text-muted-foreground">{event.minute}&apos;</span>
          </li>
        ))}
    </ul>
  );
}
