import argparse
from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from app.clients import api_football, football_data
from app.db import SessionLocal
from app.models import EPLGameEvent, Game, League, Season, Team
from app.scoring.epl import calculate_epl_game_score

RED_CARD_DETAILS = {"Red Card", "Yellow Card / Red Card"}


def seed_league(db: Session) -> League:
    league = db.query(League).filter_by(slug="epl").one_or_none()
    if league is None:
        league = League(name="Premier League", slug="epl", sport="soccer", country="England")
        db.add(league)
        db.flush()
    return league


def seed_teams_for_season(
    db: Session, league: League, year: int, teams_by_external_id: dict[str, Team]
) -> dict[str, int]:
    """Upserts Team rows for this season and returns {our Team.external_id: API-Football team id}.

    football-data.org's /teams endpoint is season-scoped — a club relegated/promoted since `year`
    won't show up in the default (current-season) call, so this must be per-season. The two
    providers use different numeric team ids, so we resolve API-Football's id for each club once
    here (by name, with a small alias table for known mismatches) rather than re-matching by name
    on every fixture lookup.
    """
    af_teams_by_name = {
        api_football.normalize_team_name(t["team"]["name"]): t["team"]["id"]
        for t in api_football.get_teams(season=year)
    }

    af_team_id_by_external_id: dict[str, int] = {}
    for fd_team in football_data.get_teams(season=year):
        external_id = str(fd_team["id"])
        if external_id not in teams_by_external_id:
            team = db.query(Team).filter_by(external_id=external_id).one_or_none()
            if team is None:
                team = Team(league_id=league.id, external_id=external_id)
                db.add(team)
            team.name = fd_team["name"]
            team.short_name = fd_team["shortName"]
            team.logo_url = fd_team.get("crest")
            teams_by_external_id[external_id] = team

        af_id = af_teams_by_name.get(api_football.normalize_team_name(fd_team["shortName"]))
        if af_id is None:
            print(f"[epl_fetcher] no API-Football team match for '{fd_team['shortName']}' (season {year})")
        else:
            af_team_id_by_external_id[external_id] = af_id

    db.flush()
    return af_team_id_by_external_id


def get_or_create_season(db: Session, league_id: int, year: int) -> Season:
    season = db.query(Season).filter_by(league_id=league_id, year=year).one_or_none()
    if season is None:
        season = Season(
            league_id=league_id,
            year=year,
            label=f"{year}-{str(year + 1)[-2:]}",
            start_date=date(year, 8, 1),
            end_date=date(year + 1, 5, 31),
        )
        db.add(season)
        db.flush()
    return season


def upsert_game(db: Session, fd_match: dict, season: Season, teams_by_external_id: dict[str, Team]) -> Game:
    external_id = str(fd_match["id"])
    game = db.query(Game).filter_by(external_id=external_id).one_or_none()
    if game is None:
        game = Game(external_id=external_id)
        db.add(game)

    game.season_id = season.id
    game.home_team_id = teams_by_external_id[str(fd_match["homeTeam"]["id"])].id
    game.away_team_id = teams_by_external_id[str(fd_match["awayTeam"]["id"])].id
    game.date = datetime.fromisoformat(fd_match["utcDate"].replace("Z", "+00:00"))
    game.status = "final" if fd_match["status"] == "FINISHED" else "scheduled"
    full_time = fd_match["score"]["fullTime"]
    game.home_score = full_time["home"]
    game.away_score = full_time["away"]
    game.is_playoff = False
    db.flush()
    return game


def _event_type(event: dict) -> str | None:
    if event["type"] == "Goal":
        return "penalty" if event["detail"] == "Penalty" else "goal"
    if event["type"] == "Card" and event["detail"] in RED_CARD_DETAILS:
        return "red_card"
    return None


def enrich_epl_events(
    db: Session, game: Game, fixture_id: int, home_team: Team, away_team: Team, af_home_id: int, af_away_id: int
) -> None:
    events = api_football.get_events(fixture_id)
    team_id_by_af_id = {af_home_id: home_team.id, af_away_id: away_team.id}

    db.query(EPLGameEvent).filter_by(game_id=game.id).delete()
    for event in events:
        event_type = _event_type(event)
        if event_type is None:
            continue

        team_id = team_id_by_af_id.get(event["team"]["id"])
        if team_id is None:
            print(f"[epl_fetcher] unmatched event team id {event['team']['id']} for game {game.external_id}, skipping event")
            continue

        minute = event["time"]["elapsed"] + (event["time"]["extra"] or 0)
        db.add(EPLGameEvent(game_id=game.id, minute=minute, event_type=event_type, team_id=team_id))
    db.flush()


def fetch_epl_games(start_date: date, end_date: date) -> None:
    db = SessionLocal()
    try:
        league = seed_league(db)
        db.commit()

        teams_by_external_id: dict[str, Team] = {}
        af_team_id_by_external_id: dict[str, int] = {}
        seasons_seeded: set[int] = set()

        fd_matches = football_data.get_matches(start_date, end_date)
        for fd_match in fd_matches:
            year = int(fd_match["season"]["startDate"][:4])
            if year not in seasons_seeded:
                af_team_id_by_external_id.update(
                    seed_teams_for_season(db, league, year, teams_by_external_id)
                )
                db.commit()
                seasons_seeded.add(year)

            season = get_or_create_season(db, league.id, year)
            game = upsert_game(db, fd_match, season, teams_by_external_id)

            home_external_id = str(fd_match["homeTeam"]["id"])
            away_external_id = str(fd_match["awayTeam"]["id"])
            af_home_id = af_team_id_by_external_id.get(home_external_id)
            af_away_id = af_team_id_by_external_id.get(away_external_id)

            if fd_match["status"] == "FINISHED":
                home_team = teams_by_external_id[home_external_id]
                away_team = teams_by_external_id[away_external_id]

                if af_home_id and af_away_id:
                    fixture_id = api_football.find_fixture_id(
                        date.fromisoformat(fd_match["utcDate"][:10]), year, af_home_id, af_away_id
                    )
                    if fixture_id is not None:
                        try:
                            enrich_epl_events(db, game, fixture_id, home_team, away_team, af_home_id, af_away_id)
                        except Exception as exc:
                            print(f"[epl_fetcher] event enrichment failed for game {game.external_id}: {exc}")
                    else:
                        print(f"[epl_fetcher] no API-Football fixture for game {game.external_id} on {fd_match['utcDate'][:10]}")

                # Score with whatever events exist (possibly none, if enrichment above didn't
                # find a fixture) — home_score/away_score are always reliable from football-data.org.
                events = db.query(EPLGameEvent).filter_by(game_id=game.id).all()
                game.game_score, game.game_score_breakdown = calculate_epl_game_score(
                    game, events, home_team, away_team
                )

            db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    yesterday = date.today() - timedelta(days=1)
    parser.add_argument("--start", type=date.fromisoformat, default=yesterday)
    parser.add_argument("--end", type=date.fromisoformat, default=yesterday)
    args = parser.parse_args()
    fetch_epl_games(args.start, args.end)
