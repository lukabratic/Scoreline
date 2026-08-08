import { GameScoreBadge } from "@/components/GameScoreBadge";

export default async function GamePage(props: PageProps<"/[league]/game/[gameId]">) {
  const { league, gameId } = await props.params;

  return (
    <div className="mx-auto flex max-w-3xl flex-col items-center gap-4 px-6 py-12 text-center">
      <GameScoreBadge score={null} size="lg" />
      <h1 className="text-2xl font-semibold">
        {league.toUpperCase()} game {gameId}
      </h1>
      <p className="text-muted-foreground">
        Matchup header, score breakdown, and community rating submission land here in build-order
        step 5.
      </p>
    </div>
  );
}
