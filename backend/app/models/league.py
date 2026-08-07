from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class League(Base):
    __tablename__ = "leagues"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    slug: Mapped[str] = mapped_column(String(20), unique=True)
    sport: Mapped[str] = mapped_column(String(50))
    country: Mapped[str] = mapped_column(String(100))

    seasons: Mapped[list["Season"]] = relationship(back_populates="league")
    teams: Mapped[list["Team"]] = relationship(back_populates="league")
