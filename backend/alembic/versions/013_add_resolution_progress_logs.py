"""add resolution_progress_logs table

Revision ID: 013
Revises: 012
Create Date: 2026-03-04

"""
from alembic import op
import sqlalchemy as sa

revision = "013"
down_revision = "012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "resolution_progress_logs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("resolution_id", sa.UUID(), nullable=False),
        sa.Column("progress_percent", sa.Integer(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column(
            "logged_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["resolution_id"],
            ["resolutions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_progress_logs_resolution",
        "resolution_progress_logs",
        ["resolution_id"],
    )


def downgrade() -> None:
    op.drop_index("idx_progress_logs_resolution", table_name="resolution_progress_logs")
    op.drop_table("resolution_progress_logs")
