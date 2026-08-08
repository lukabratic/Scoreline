import functools
import re
import time
from datetime import date

import requests

from app.config import settings

BASE_URL = "https://v3.football.api-sports.io"
PREMIER_LEAGUE_ID = 39

# football-data.org's shortName vs API-Football's name disagree for a handful of clubs
# (abbreviations, missing suffixes) even after normalization — confirmed against live
# responses for the 2024-25 season. Keyed by football-data shortName.
NAME_ALIASES = {
    "man city": "manchester city",
    "man united": "manchester united",
    "nottingham": "nottingham forest",
    "brighton hove": "brighton",
    "wolverhampton": "wolves",
    "leicester city": "leicester",
    "ipswich town": "ipswich",
}


def _headers() -> dict:
    return {"x-apisports-key": settings.api_football_key}


def _get(path: str, params: dict) -> dict:
    resp = requests.get(f"{BASE_URL}{path}", headers=_headers(), params=params, timeout=30)
    for _ in range(3):
        if resp.status_code != 429:
            break
        time.sleep(20)
        resp = requests.get(f"{BASE_URL}{path}", headers=_headers(), params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()["response"]


def normalize_team_name(name: str) -> str:
    normalized = re.sub(r"\b(fc|afc)\b", "", name.lower()).strip()
    return NAME_ALIASES.get(normalized, normalized)


@functools.lru_cache(maxsize=None)
def get_teams(season: int) -> list[dict]:
    teams = _get("/teams", {"league": PREMIER_LEAGUE_ID, "season": season})
    time.sleep(6.5)
    return teams


@functools.lru_cache(maxsize=None)
def _fixtures_for_date(date_iso: str, season: int) -> list[dict]:
    # NB: the single `date=` param is restricted on API-Football's free plan to a near-today
    # window regardless of season; `from`/`to` with the same day works for any allowed season.
    fixtures = _get(
        "/fixtures",
        {"league": PREMIER_LEAGUE_ID, "season": season, "from": date_iso, "to": date_iso},
    )
    time.sleep(6.5)
    return fixtures


def find_fixture_id(match_date: date, season: int, af_home_id: int, af_away_id: int) -> int | None:
    fixtures = _fixtures_for_date(match_date.isoformat(), season)
    for fixture in fixtures:
        teams = fixture["teams"]
        if teams["home"]["id"] == af_home_id and teams["away"]["id"] == af_away_id:
            return fixture["fixture"]["id"]
    return None


def get_events(fixture_id: int) -> list[dict]:
    events = _get("/fixtures/events", {"fixture": fixture_id})
    time.sleep(6.5)
    return events
