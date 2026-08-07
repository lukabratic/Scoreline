"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-08-07

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_initial"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "leagues",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=20), nullable=False),
        sa.Column("sport", sa.String(length=50), nullable=False),
        sa.Column("country", sa.String(length=100), nullable=False),
        sa.UniqueConstraint("slug"),
    )

    op.create_table(
        "seasons",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("league_id", sa.Integer(), sa.ForeignKey("leagues.id"), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(length=20), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
    )

    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("league_id", sa.Integer(), sa.ForeignKey("leagues.id"), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("short_name", sa.String(length=20), nullable=False),
        sa.Column("logo_url", sa.String(length=500), nullable=True),
        sa.Column("external_id", sa.String(length=100), nullable=False),
        sa.UniqueConstraint("external_id"),
    )

    op.create_table(
        "games",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("season_id", sa.Integer(), sa.ForeignKey("seasons.id"), nullable=False),
        sa.Column("home_team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("away_team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("home_score", sa.Integer(), nullable=True),
        sa.Column("away_score", sa.Integer(), nullable=True),
        sa.Column("external_id", sa.String(length=100), nullable=False),
        sa.Column("is_playoff", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("playoff_round", sa.String(length=50), nullable=True),
        sa.Column("game_score", sa.Float(), nullable=True),
        sa.Column("game_score_breakdown", sa.JSON(), nullable=True),
        sa.UniqueConstraint("external_id"),
    )

    op.create_table(
        "nba_game_stats",
        sa.Column("game_id", sa.Integer(), sa.ForeignKey("games.id"), primary_key=True),
        sa.Column("lead_changes", sa.Integer(), nullable=True),
        sa.Column("times_tied", sa.Integer(), nullable=True),
        sa.Column("largest_deficit_overcome", sa.Integer(), nullable=True),
        sa.Column("overtime_periods", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("top_performer_id", sa.String(), nullable=True),
        sa.Column("top_performer_pts", sa.Integer(), nullable=True),
    )

    op.create_table(
        "epl_game_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("game_id", sa.Integer(), sa.ForeignKey("games.id"), nullable=False),
        sa.Column("minute", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=20), nullable=False),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
    )

    op.create_table(
        "user_ratings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.String(length=100), nullable=False),
        sa.Column("game_id", sa.Integer(), sa.ForeignKey("games.id"), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("user_id", "game_id"),
    )


def downgrade() -> None:
    op.drop_table("user_ratings")
    op.drop_table("epl_game_events")
    op.drop_table("nba_game_stats")
    op.drop_table("games")
    op.drop_table("teams")
    op.drop_table("seasons")
    op.drop_table("leagues")
