from app.db import SessionLocal
from app.models import EPLGameEvent, Game, League, NBAGameStats, Season, Team
from app.scoring.epl import calculate_epl_game_score
from app.scoring.nba import calculate_nba_game_score


def backfill_game_scores() -> None:
    db = SessionLocal()
    try:
        games = (
            db.query(Game)
            .join(Season, Game.season_id == Season.id)
            .join(League, Season.league_id == League.id)
            .filter(Game.status == "final")
            .add_columns(League.slug)
            .all()
        )

        nba_scored = epl_scored = nba_skipped = 0
        for game, league_slug in games:
            if league_slug == "nba":
                stats = db.query(NBAGameStats).filter_by(game_id=game.id).one_or_none()
                if stats is None:
                    nba_skipped += 1
                    print(f"[backfill] skipping NBA game {game.external_id}: no NBAGameStats row")
                    continue
                game.game_score, game.game_score_breakdown = calculate_nba_game_score(game, stats)
                nba_scored += 1
            elif league_slug == "epl":
                home_team = db.get(Team, game.home_team_id)
                away_team = db.get(Team, game.away_team_id)
                events = db.query(EPLGameEvent).filter_by(game_id=game.id).all()
                game.game_score, game.game_score_breakdown = calculate_epl_game_score(
                    game, events, home_team, away_team
                )
                epl_scored += 1

        db.commit()
        print(f"[backfill] scored {nba_scored} NBA games, {epl_scored} EPL games, skipped {nba_skipped} NBA games (no stats)")
    finally:
        db.close()


if __name__ == "__main__":
    backfill_game_scores()
