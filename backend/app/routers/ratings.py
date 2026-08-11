from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_current_user_id
from app.db import get_db
from app.models import Game, UserRating
from app.schemas import RatingIn, RatingSummaryOut, UserRatingOut

router = APIRouter(tags=["ratings"])


def _get_game_or_404(game_id: int, db: Session) -> Game:
    game = db.get(Game, game_id)
    if game is None:
        raise HTTPException(status_code=404, detail=f"Game {game_id} not found")
    return game


@router.get("/games/{game_id}/ratings", response_model=RatingSummaryOut)
def get_rating_summary(game_id: int, db: Session = Depends(get_db)):
    _get_game_or_404(game_id, db)
    average, count = (
        db.query(func.avg(UserRating.score), func.count(UserRating.id))
        .filter(UserRating.game_id == game_id)
        .one()
    )
    return RatingSummaryOut(average=average, count=count)


@router.get("/games/{game_id}/ratings/me", response_model=UserRatingOut)
def get_my_rating(
    game_id: int, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)
):
    _get_game_or_404(game_id, db)
    rating = db.query(UserRating).filter_by(game_id=game_id, user_id=user_id).one_or_none()
    if rating is None:
        raise HTTPException(status_code=404, detail="No rating from this user for this game")
    return rating


@router.put("/games/{game_id}/ratings/me", response_model=UserRatingOut)
def upsert_my_rating(
    game_id: int,
    body: RatingIn,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    _get_game_or_404(game_id, db)
    rating = db.query(UserRating).filter_by(game_id=game_id, user_id=user_id).one_or_none()
    if rating is None:
        rating = UserRating(game_id=game_id, user_id=user_id, score=body.score)
        db.add(rating)
    else:
        rating.score = body.score
    db.commit()
    db.refresh(rating)
    return rating
