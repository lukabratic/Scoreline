import argparse
import functools
import time
from datetime import date, datetime, timedelta

from nba_api.stats.endpoints import boxscoresummaryv3, playbyplayv3, scoreboardv2
from sqlalchemy.orm import Session

from app.clients import balldontlie
from app.db import SessionLocal
from app.models import Game, League, NBAGameStats, Season, Team

NBA_COM_SLEEP_SECONDS = 0.6


def seed_league_and_teams(db: Session) -> tuple[League, dict[str, Team]]:
    league = db.query(League).filter_by(slug="nba").one_or_none()
    if league is None:
        league = League(name="National Basketball Association", slug="nba", sport="basketball", country="USA")
        db.add(league)
        db.flush()

    teams_by_external_id: dict[str, Team] = {}
    for bdl_team in balldontlie.get_teams():
        external_id = str(bdl_team["id"])
        team = db.query(Team).filter_by(external_id=external_id).one_or_none()
        if team is None:
            team = Team(league_id=league.id, external_id=external_id)
            db.add(team)
        team.name = bdl_team["full_name"]
        team.short_name = bdl_team["abbreviation"]
        teams_by_external_id[external_id] = team
    db.flush()
    return league, teams_by_external_id


def get_or_create_season(db: Session, league_id: int, year: int) -> Season:
    season = db.query(Season).filter_by(league_id=league_id, year=year).one_or_none()
    if season is None:
        season = Season(
            league_id=league_id,
            year=year,
            label=f"{year}-{str(year + 1)[-2:]}",
            start_date=date(year, 10, 1),
            end_date=date(year + 1, 6, 30),
        )
        db.add(season)
        db.flush()
    return season


def _overtime_periods(bdl_game: dict) -> int:
    return sum(1 for key in ("home_ot1", "home_ot2", "home_ot3") if bdl_game.get(key) is not None)


def upsert_game(db: Session, bdl_game: dict, season: Season, teams_by_external_id: dict[str, Team]) -> Game:
    external_id = str(bdl_game["id"])
    game = db.query(Game).filter_by(external_id=external_id).one_or_none()
    if game is None:
        game = Game(external_id=external_id)
        db.add(game)

    game.season_id = season.id
    game.home_team_id = teams_by_external_id[str(bdl_game["home_team"]["id"])].id
    game.away_team_id = teams_by_external_id[str(bdl_game["visitor_team"]["id"])].id
    game.date = datetime.fromisoformat(bdl_game["datetime"].replace("Z", "+00:00"))
    game.status = "final" if bdl_game["status"] == "Final" else "scheduled"
    game.home_score = bdl_game["home_team_score"] or None
    game.away_score = bdl_game["visitor_team_score"] or None
    game.is_playoff = bool(bdl_game["postseason"])
    db.flush()
    return game


@functools.lru_cache(maxsize=None)
def _scoreboard_for_date(game_date_iso: str) -> dict:
    sb = scoreboardv2.ScoreboardV2(game_date=game_date_iso, day_offset=0, league_id="00")
    time.sleep(NBA_COM_SLEEP_SECONDS)
    return sb.get_normalized_dict()


def find_nba_game_id(game_date: date, home_abbr: str, away_abbr: str) -> str | None:
    data = _scoreboard_for_date(game_date.isoformat())
    line_score_by_game: dict[str, set[str]] = {}
    for row in data["LineScore"]:
        line_score_by_game.setdefault(row["GAME_ID"], set()).add(row["TEAM_ABBREVIATION"])

    wanted = {home_abbr, away_abbr}
    for header in data["GameHeader"]:
        game_id = header["GAME_ID"]
        if line_score_by_game.get(game_id) == wanted:
            return game_id
    return None


def _largest_deficit_overcome(nba_game_id: str, home_won: bool) -> int:
    actions = playbyplayv3.PlayByPlayV3(
        game_id=nba_game_id, start_period=0, end_period=0
    ).get_dict()["game"]["actions"]
    time.sleep(NBA_COM_SLEEP_SECONDS)

    margins: list[int] = []
    for action in actions:
        home_raw, away_raw = action.get("scoreHome"), action.get("scoreAway")
        if not home_raw or not away_raw:
            continue
        margins.append(int(home_raw) - int(away_raw))

    if not margins:
        return 0
    if home_won:
        return max(0, -min(margins))
    return max(0, max(margins))


def enrich_nba_stats(db: Session, game: Game, nba_game_id: str, overtime_periods: int) -> None:
    charts = boxscoresummaryv3.BoxScoreSummaryV3(game_id=nba_game_id).get_dict()["boxScoreSummary"][
        "postgameCharts"
    ]
    time.sleep(NBA_COM_SLEEP_SECONDS)

    home_stats = charts["homeTeam"]["statistics"]
    away_stats = charts["awayTeam"]["statistics"]

    home_won = bool(game.home_score is not None and game.away_score is not None and game.home_score > game.away_score)
    largest_deficit_overcome = _largest_deficit_overcome(nba_game_id, home_won)

    top_side = home_stats if home_stats["playerPtsLeaderPts"] >= away_stats["playerPtsLeaderPts"] else away_stats

    stats = db.query(NBAGameStats).filter_by(game_id=game.id).one_or_none()
    if stats is None:
        stats = NBAGameStats(game_id=game.id)
        db.add(stats)

    stats.lead_changes = int(home_stats["leadChanges"])
    stats.times_tied = int(home_stats["timesTied"])
    stats.largest_deficit_overcome = largest_deficit_overcome
    stats.overtime_periods = overtime_periods
    stats.top_performer_id = str(top_side["playerPtsLeaderId"])
    stats.top_performer_pts = int(top_side["playerPtsLeaderPts"])
    db.flush()


def fetch_nba_games(start_date: date, end_date: date) -> None:
    db = SessionLocal()
    try:
        league, teams_by_external_id = seed_league_and_teams(db)
        db.commit()

        bdl_games = balldontlie.get_games(start_date, end_date)
        for bdl_game in bdl_games:
            season = get_or_create_season(db, league.id, bdl_game["season"])
            game = upsert_game(db, bdl_game, season, teams_by_external_id)
            ot_periods = _overtime_periods(bdl_game)

            if bdl_game["status"] == "Final":
                nba_game_id = find_nba_game_id(
                    date.fromisoformat(bdl_game["date"]),
                    bdl_game["home_team"]["abbreviation"],
                    bdl_game["visitor_team"]["abbreviation"],
                )
                if nba_game_id is not None:
                    try:
                        enrich_nba_stats(db, game, nba_game_id, ot_periods)
                    except Exception as exc:  # unofficial API — log and keep going
                        print(f"[nba_fetcher] stats enrichment failed for game {game.external_id}: {exc}")
                else:
                    print(f"[nba_fetcher] no nba.com match for game {game.external_id} on {bdl_game['date']}")

            db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    yesterday = date.today() - timedelta(days=1)
    parser.add_argument("--start", type=date.fromisoformat, default=yesterday)
    parser.add_argument("--end", type=date.fromisoformat, default=yesterday)
    args = parser.parse_args()
    fetch_nba_games(args.start, args.end)
