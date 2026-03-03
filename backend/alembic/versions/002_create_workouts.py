"""create workouts table

Revision ID: 002
Revises: 001
Create Date: 2026-03-03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workouts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("did_workout", sa.Boolean(), nullable=False),
        sa.Column("activity_type", sa.Text(), nullable=True),
        sa.Column("duration_mins", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["auth.users.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("user_id", "date", name="uq_workouts_user_date"),
    )
    op.create_index("idx_workouts_user_date", "workouts", ["user_id", "date"])


def downgrade() -> None:
    op.drop_index("idx_workouts_user_date", table_name="workouts")
    op.drop_table("workouts")
