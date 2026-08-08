from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class LeagueOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    sport: str
    country: str


class SeasonOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    year: int
    label: str
    start_date: date
    end_date: date


class TeamOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    short_name: str
    logo_url: str | None


class GameListItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    season_id: int
    date: datetime
    status: str
    home_team: TeamOut
    away_team: TeamOut
    home_score: int | None
    away_score: int | None
    is_playoff: bool
    game_score: float | None
    game_score_breakdown: list[str] | None


class NBAGameStatsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    lead_changes: int | None
    times_tied: int | None
    largest_deficit_overcome: int | None
    overtime_periods: int
    top_performer_id: str | None
    top_performer_pts: int | None


class EPLGameEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    minute: int
    event_type: str
    team_id: int


class GameDetailOut(GameListItemOut):
    playoff_round: str | None
    nba_stats: NBAGameStatsOut | None
    epl_events: list[EPLGameEventOut]
