import { GameScoreBadge } from "@/components/GameScoreBadge";
import type { League } from "@/lib/types";

const LEAGUE_NAMES: Record<League, string> = {
  nba: "NBA",
  epl: "Premier League",
};

export default async function LeagueHomePage(props: PageProps<"/[league]">) {
  const { league } = await props.params;
  const leagueName = LEAGUE_NAMES[league as League];

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-8 px-6 py-12">
      <section className="flex flex-col items-center gap-4 rounded-xl border border-border bg-surface py-16 text-center">
        <GameScoreBadge score={null} size="lg" />
        <h1 className="text-2xl font-semibold">{leagueName} season arc graph</h1>
        <p className="max-w-md text-muted-foreground">
          The hero season graph lands here once Game Score calculation (build-order step 3) is
          in place — this route and its theming are wired up and ready for it.
        </p>
      </section>

      <section>
        <h2 className="mb-4 text-lg font-semibold">Recent games</h2>
        <p className="text-muted-foreground">Coming once the read API endpoints exist.</p>
      </section>
    </div>
  );
}
