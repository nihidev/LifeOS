"""add category column to small_wins

Revision ID: 010
Revises: 009
Create Date: 2026-03-04

"""
from alembic import op
import sqlalchemy as sa

revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("small_wins", sa.Column("category", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("small_wins", "category")
