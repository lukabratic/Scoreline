export default async function SeasonPage(props: PageProps<"/[league]/season/[seasonId]">) {
  const { league, seasonId } = await props.params;

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-4 px-6 py-12">
      <h1 className="text-2xl font-semibold">
        {league.toUpperCase()} season {seasonId}
      </h1>
      <p className="text-muted-foreground">
        Season arc graph (algorithmic Game Score vs. community average, playoff markers, hover
        breakdown) lands here in build-order step 4.
      </p>
    </div>
  );
}
