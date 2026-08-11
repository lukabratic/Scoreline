import type {
  GameDetail,
  GameListItem,
  LeagueRecord,
  League,
  RatingSummary,
  Season,
  Team,
  UserRatingRecord,
} from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, { cache: "no-store", ...init });
  if (!res.ok) {
    throw new Error(`API request to ${path} failed: ${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export interface HealthResponse {
  status: string;
}

export function getHealth(): Promise<HealthResponse> {
  return apiFetch<HealthResponse>("/health");
}

export function getLeagues(): Promise<LeagueRecord[]> {
  return apiFetch<LeagueRecord[]>("/leagues");
}

export function getLeagueSeasons(league: League): Promise<Season[]> {
  return apiFetch<Season[]>(`/leagues/${league}/seasons`);
}

export function getLeagueTeams(league: League): Promise<Team[]> {
  return apiFetch<Team[]>(`/leagues/${league}/teams`);
}

export function getRecentGames(league: League, limit = 10): Promise<GameListItem[]> {
  return apiFetch<GameListItem[]>(`/leagues/${league}/games/recent?limit=${limit}`);
}

export function getTeam(teamId: number): Promise<Team> {
  return apiFetch<Team>(`/teams/${teamId}`);
}

export function getTeamSeasonGames(teamId: number, seasonId: number): Promise<GameListItem[]> {
  return apiFetch<GameListItem[]>(`/teams/${teamId}/seasons/${seasonId}/games`);
}

export function getGame(gameId: number): Promise<GameDetail> {
  return apiFetch<GameDetail>(`/games/${gameId}`);
}

export function getRatingSummary(gameId: number): Promise<RatingSummary> {
  return apiFetch<RatingSummary>(`/games/${gameId}/ratings`);
}

export async function getMyRating(
  gameId: number,
  accessToken: string
): Promise<UserRatingRecord | null> {
  const res = await fetch(`${API_BASE_URL}/games/${gameId}/ratings/me`, {
    cache: "no-store",
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  if (res.status === 404) return null;
  if (!res.ok) {
    throw new Error(`API request to /games/${gameId}/ratings/me failed: ${res.status}`);
  }
  return res.json() as Promise<UserRatingRecord>;
}

export async function submitRating(
  gameId: number,
  score: number,
  accessToken: string
): Promise<UserRatingRecord> {
  const res = await fetch(`${API_BASE_URL}/games/${gameId}/ratings/me`, {
    method: "PUT",
    cache: "no-store",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({ score }),
  });
  if (!res.ok) {
    throw new Error(`API request to /games/${gameId}/ratings/me failed: ${res.status}`);
  }
  return res.json() as Promise<UserRatingRecord>;
}
