import type { GameDetail, GameListItem, LeagueRecord, League, Season, Team } from "@/lib/types";

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
