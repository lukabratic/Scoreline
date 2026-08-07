from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True)
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id"))
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20))  # scheduled | final
    home_score: Mapped[int | None]
    away_score: Mapped[int | None]
    external_id: Mapped[str] = mapped_column(String(100), unique=True)
    is_playoff: Mapped[bool] = mapped_column(default=False)
    playoff_round: Mapped[str | None] = mapped_column(String(50))

    # Computed and stored at fetch time — never recalculated on read.
    game_score: Mapped[float | None]
    game_score_breakdown: Mapped[list | None] = mapped_column(JSON)

    season: Mapped["Season"] = relationship(back_populates="games")
    home_team: Mapped["Team"] = relationship(
        back_populates="home_games", foreign_keys=[home_team_id]
    )
    away_team: Mapped["Team"] = relationship(
        back_populates="away_games", foreign_keys=[away_team_id]
    )
    nba_stats: Mapped["NBAGameStats | None"] = relationship(
        back_populates="game", uselist=False
    )
    epl_events: Mapped[list["EPLGameEvent"]] = relationship(back_populates="game")
    ratings: Mapped[list["UserRating"]] = relationship(back_populates="game")
