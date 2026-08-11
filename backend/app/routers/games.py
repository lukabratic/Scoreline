from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Game, Season, Team
from app.rating_stats import attach_community_scores
from app.schemas import GameDetailOut, GameListItemOut

router = APIRouter(tags=["games"])


@router.get("/seasons/{season_id}/games", response_model=list[GameListItemOut])
def list_games_for_season(season_id: int, db: Session = Depends(get_db)):
    season = db.get(Season, season_id)
    if season is None:
        raise HTTPException(status_code=404, detail=f"Season {season_id} not found")
    games = db.query(Game).filter_by(season_id=season_id).order_by(Game.date).all()
    return attach_community_scores(games, db)


@router.get("/teams/{team_id}/seasons/{season_id}/games", response_model=list[GameListItemOut])
def list_games_for_team_season(team_id: int, season_id: int, db: Session = Depends(get_db)):
    team = db.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail=f"Team {team_id} not found")
    season = db.get(Season, season_id)
    if season is None:
        raise HTTPException(status_code=404, detail=f"Season {season_id} not found")
    games = (
        db.query(Game)
        .filter(
            Game.season_id == season_id,
            or_(Game.home_team_id == team_id, Game.away_team_id == team_id),
        )
        .order_by(Game.date)
        .all()
    )
    return attach_community_scores(games, db)


@router.get("/games/{game_id}", response_model=GameDetailOut)
def get_game(game_id: int, db: Session = Depends(get_db)):
    game = db.get(Game, game_id)
    if game is None:
        raise HTTPException(status_code=404, detail=f"Game {game_id} not found")
    attach_community_scores([game], db)
    return game
