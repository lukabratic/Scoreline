from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Game, League, Season, Team
from app.schemas import GameListItemOut, LeagueOut, SeasonOut, TeamOut

router = APIRouter(tags=["leagues"])


def _get_league_or_404(slug: str, db: Session) -> League:
    league = db.query(League).filter_by(slug=slug).one_or_none()
    if league is None:
        raise HTTPException(status_code=404, detail=f"League '{slug}' not found")
    return league


@router.get("/leagues", response_model=list[LeagueOut])
def list_leagues(db: Session = Depends(get_db)):
    return db.query(League).order_by(League.slug).all()


@router.get("/leagues/{slug}/seasons", response_model=list[SeasonOut])
def list_seasons(slug: str, db: Session = Depends(get_db)):
    league = _get_league_or_404(slug, db)
    return db.query(Season).filter_by(league_id=league.id).order_by(Season.year.desc()).all()


@router.get("/leagues/{slug}/teams", response_model=list[TeamOut])
def list_teams(slug: str, db: Session = Depends(get_db)):
    league = _get_league_or_404(slug, db)
    return db.query(Team).filter_by(league_id=league.id).order_by(Team.name).all()


@router.get("/leagues/{slug}/games/recent", response_model=list[GameListItemOut])
def list_recent_games(slug: str, limit: int = 10, db: Session = Depends(get_db)):
    league = _get_league_or_404(slug, db)
    return (
        db.query(Game)
        .join(Season, Game.season_id == Season.id)
        .filter(Season.league_id == league.id)
        .order_by(Game.date.desc())
        .limit(limit)
        .all()
    )
