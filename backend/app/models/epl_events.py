from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class EPLGameEvent(Base):
    __tablename__ = "epl_game_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))
    minute: Mapped[int]
    event_type: Mapped[str] = mapped_column(String(20))  # goal | red_card | penalty
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))

    game: Mapped["Game"] = relationship(back_populates="epl_events")
    team: Mapped["Team"] = relationship()
