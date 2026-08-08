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
  league_id: number;
  year: number;
  label: string;
  start_date: string;
  end_date: string;
}

export interface Team {
  id: number;
  league_id: number;
  name: string;
  short_name: string;
  logo_url: string | null;
  external_id: string;
}

export type GameStatus = "scheduled" | "final";

export interface Game {
  id: number;
  season_id: number;
  home_team_id: number;
  away_team_id: number;
  date: string;
  status: GameStatus;
  home_score: number | null;
  away_score: number | null;
  external_id: string;
  is_playoff: boolean;
  playoff_round: string | null;
  // Computed and stored at fetch time by the pipeline — null until build-order step 3 runs.
  game_score: number | null;
  game_score_breakdown: string[] | null;
}

export interface NBAGameStats {
  game_id: number;
  lead_changes: number | null;
  times_tied: number | null;
  largest_deficit_overcome: number | null;
  overtime_periods: number;
  top_performer_id: string | null;
  top_performer_pts: number | null;
}

export type EPLEventType = "goal" | "red_card" | "penalty";

export interface EPLGameEvent {
  id: number;
  game_id: number;
  minute: number;
  event_type: EPLEventType;
  team_id: number;
}

export interface UserRating {
  id: number;
  user_id: string;
  game_id: number;
  score: number;
  created_at: string;
}
