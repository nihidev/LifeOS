"""add entry_type and completed to small_wins

Revision ID: 004
Revises: 003
Create Date: 2026-03-03

"""
from alembic import op
import sqlalchemy as sa

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "small_wins",
        sa.Column("entry_type", sa.Text(), nullable=False, server_default="win"),
    )
    op.add_column(
        "small_wins",
        sa.Column("completed", sa.Boolean(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("small_wins", "completed")
    op.drop_column("small_wins", "entry_type")
