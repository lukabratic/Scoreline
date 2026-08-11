from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Game, UserRating


def attach_community_scores(games: list[Game], db: Session) -> list[Game]:
    """Set `community_score`/`community_rating_count` on each Game instance in place.

    These aren't mapped columns — UserRating rows are aggregated per request and stashed as
    plain attributes so GameListItemOut (from_attributes=True) can read them like any other field.
    """
    if not games:
        return games
    game_ids = [g.id for g in games]
    rows = (
        db.query(UserRating.game_id, func.avg(UserRating.score), func.count(UserRating.id))
        .filter(UserRating.game_id.in_(game_ids))
        .group_by(UserRating.game_id)
        .all()
    )
    stats = {game_id: (average, count) for game_id, average, count in rows}
    for game in games:
        average, count = stats.get(game.id, (None, 0))
        game.community_score = average
        game.community_rating_count = count
    return games
