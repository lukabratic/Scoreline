import Link from "next/link";
import { getLeagueSeasons, getRecentGames, getTeamSeasonGames } from "@/lib/api";
import type { League } from "@/lib/types";
import { SeasonArcGraph } from "@/components/SeasonArcGraph";
import { GameCard } from "@/components/GameCard";

const LEAGUE_NAMES: Record<League, string> = {
  nba: "NBA",
  epl: "Premier League",
};

export default async function LeagueHomePage(props: PageProps<"/[league]">) {
  const { league } = await props.params;
  const leagueSlug = league as League;
  const leagueName = LEAGUE_NAMES[leagueSlug];

  const [seasons, recentGames] = await Promise.all([
    getLeagueSeasons(leagueSlug),
    getRecentGames(leagueSlug, 10),
  ]);

  const mostRecentGame = recentGames[0];
  const defaultTeam = mostRecentGame?.home_team;
  const currentSeason = seasons[0];

  const teamSeasonGames =
    defaultTeam && currentSeason
      ? await getTeamSeasonGames(defaultTeam.id, currentSeason.id)
      : [];

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-8 px-6 py-12">
      <section className="rounded-xl border border-border bg-surface p-6">
        {defaultTeam && currentSeason ? (
          <>
            <div className="mb-4 flex items-baseline justify-between">
              <div>
                <h1 className="text-2xl font-semibold">
                  {defaultTeam.name} · {currentSeason.label}
                </h1>
                <p className="text-sm text-muted-foreground">{leagueName} season arc</p>
              </div>
              <Link
                href={`/${leagueSlug}/team/${defaultTeam.id}/season/${currentSeason.id}`}
                className="text-sm text-accent hover:underline"
              >
                Full season →
              </Link>
            </div>
            <SeasonArcGraph team={defaultTeam} games={teamSeasonGames} />
          </>
        ) : (
          <p className="py-16 text-center text-muted-foreground">
            No {leagueName} data yet — run the fetcher to populate games.
          </p>
        )}
      </section>

      <section>
        <h2 className="mb-4 text-lg font-semibold">Recent games</h2>
        {recentGames.length === 0 ? (
          <p className="text-muted-foreground">No games yet.</p>
        ) : (
          <div className="flex flex-col gap-3">
            {recentGames.map((game) => (
              <GameCard key={game.id} league={leagueSlug} game={game} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
