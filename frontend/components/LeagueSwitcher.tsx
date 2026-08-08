"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { League } from "@/lib/types";

const LEAGUES: { slug: League; label: string }[] = [
  { slug: "nba", label: "NBA" },
  { slug: "epl", label: "EPL" },
];

export function LeagueSwitcher() {
  const pathname = usePathname();
  const activeLeague = pathname.split("/")[1];

  return (
    <nav className="flex items-center gap-1 rounded-full border border-border bg-surface p-1">
      {LEAGUES.map(({ slug, label }) => {
        const isActive = activeLeague === slug;
        return (
          <Link
            key={slug}
            href={`/${slug}`}
            className={`rounded-full px-3 py-1 text-sm font-medium transition-colors ${
              isActive
                ? "text-white"
                : "text-muted-foreground hover:text-foreground"
            }`}
            style={isActive ? { backgroundColor: `var(--accent-${slug})` } : undefined}
          >
            {label}
          </Link>
        );
      })}
    </nav>
  );
}
