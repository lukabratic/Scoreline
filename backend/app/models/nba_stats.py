from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class NBAGameStats(Base):
    __tablename__ = "nba_game_stats"

    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), primary_key=True)
    lead_changes: Mapped[int | None]
    times_tied: Mapped[int | None]
    largest_deficit_overcome: Mapped[int | None]
    overtime_periods: Mapped[int] = mapped_column(default=0)
    top_performer_id: Mapped[str | None]
    top_performer_pts: Mapped[int | None]

    game: Mapped["Game"] = relationship(back_populates="nba_stats")
