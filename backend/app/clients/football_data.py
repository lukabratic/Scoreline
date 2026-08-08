import time
from datetime import date

import requests

from app.config import settings

BASE_URL = "https://api.football-data.org/v4"


def _headers() -> dict:
    return {"X-Auth-Token": settings.football_data_api_key}


def _get(path: str, params: dict) -> dict:
    resp = requests.get(f"{BASE_URL}{path}", headers=_headers(), params=params, timeout=30)
    if resp.status_code == 429:
        time.sleep(15)
        resp = requests.get(f"{BASE_URL}{path}", headers=_headers(), params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def get_teams(season: int | None = None) -> list[dict]:
    params = {"season": season} if season is not None else {}
    return _get("/competitions/PL/teams", params)["teams"]


def get_matches(start_date: date, end_date: date) -> list[dict]:
    payload = _get(
        "/competitions/PL/matches",
        {"dateFrom": start_date.isoformat(), "dateTo": end_date.isoformat()},
    )
    return payload["matches"]
