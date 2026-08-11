export type League = "nba" | "epl";

export interface LeagueRecord {
  id: number;
  name: string;
  slug: League;
  sport: string;
  country: string;
}

export interface Season {
  id: number;
  year: number;
  label: string;
  start_date: string;
  end_date: string;
}

export interface Team {
  id: number;
  name: string;
  short_name: string;
  logo_url: string | null;
}

export type GameStatus = "scheduled" | "final";

export interface GameListItem {
  id: number;
  season_id: number;
  date: string;
  status: GameStatus;
  home_team: Team;
  away_team: Team;
  home_score: number | null;
  away_score: number | null;
  is_playoff: boolean;
  // Computed and stored at fetch time by the pipeline — null until a game has been scored.
  game_score: number | null;
  game_score_breakdown: string[] | null;
  // Aggregated from UserRating rows at read time — null/0 until at least one person has rated it.
  community_score: number | null;
  community_rating_count: number;
}

export interface NBAGameStats {
  lead_changes: number | null;
  times_tied: number | null;
  largest_deficit_overcome: number | null;
  overtime_periods: number;
  top_performer_id: string | null;
  top_performer_pts: number | null;
}

export type EPLEventType = "goal" | "red_card" | "penalty";

export interface EPLGameEvent {
  minute: number;
  event_type: EPLEventType;
  team_id: number;
}

export interface GameDetail extends GameListItem {
  playoff_round: string | null;
  nba_stats: NBAGameStats | null;
  epl_events: EPLGameEvent[];
}

export interface RatingSummary {
  average: number | null;
  count: number;
}

export interface UserRatingRecord {
  score: number;
}
