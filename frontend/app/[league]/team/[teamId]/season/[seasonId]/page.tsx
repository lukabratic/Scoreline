import { notFound } from "next/navigation";
import { getLeagueSeasons, getTeam, getTeamSeasonGames } from "@/lib/api";
import type { League } from "@/lib/types";
import { SeasonArcGraph } from "@/components/SeasonArcGraph";

export default async function TeamSeasonPage(
  props: PageProps<"/[league]/team/[teamId]/season/[seasonId]">
) {
  const { league, teamId, seasonId } = await props.params;
  const leagueSlug = league as League;

  let team;
  try {
    team = await getTeam(Number(teamId));
  } catch {
    notFound();
  }

  const seasons = await getLeagueSeasons(leagueSlug);
  const season = seasons.find((s) => s.id === Number(seasonId));
  if (!season) {
    notFound();
  }

  const games = await getTeamSeasonGames(Number(teamId), Number(seasonId));

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-6 px-6 py-12">
      <div>
        <h1 className="text-2xl font-semibold">{team.name}</h1>
        <p className="text-sm text-muted-foreground">{season.label} season arc</p>
      </div>
      <div className="rounded-xl border border-border bg-surface p-6">
        <SeasonArcGraph team={team} games={games} />
      </div>
    </div>
  );
}
