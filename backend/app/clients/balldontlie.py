import time
from datetime import date

import requests

from app.config import settings

BASE_URL = "https://api.balldontlie.io/v1"


def _headers() -> dict:
    return {"Authorization": settings.balldontlie_api_key}


def _get(path: str, params: dict) -> dict:
    resp = requests.get(f"{BASE_URL}{path}", headers=_headers(), params=params, timeout=30)
    if resp.status_code == 429:
        time.sleep(15)
        resp = requests.get(f"{BASE_URL}{path}", headers=_headers(), params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def get_teams() -> list[dict]:
    return _get("/teams", {"per_page": 100})["data"]


def get_games(start_date: date, end_date: date) -> list[dict]:
    games: list[dict] = []
    cursor: int | None = None
    while True:
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "per_page": 100,
        }
        if cursor is not None:
            params["cursor"] = cursor
        payload = _get("/games", params)
        games.extend(payload["data"])
        cursor = payload["meta"].get("next_cursor")
        if not cursor:
            break
    return games
