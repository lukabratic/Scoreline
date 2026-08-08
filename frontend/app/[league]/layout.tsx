import { notFound } from "next/navigation";
import type { CSSProperties } from "react";
import type { League } from "@/lib/types";

const VALID_LEAGUES: League[] = ["nba", "epl"];

export default async function LeagueLayout(props: LayoutProps<"/[league]">) {
  const { league } = await props.params;

  if (!VALID_LEAGUES.includes(league as League)) {
    notFound();
  }

  const accentStyle = {
    "--accent": `var(--accent-${league})`,
  } as CSSProperties;

  return (
    <div style={accentStyle} className="flex flex-1 flex-col">
      {props.children}
    </div>
  );
}
