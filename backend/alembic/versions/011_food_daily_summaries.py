"""create food_daily_summaries table

Revision ID: 011
Revises: 010
Create Date: 2026-03-04

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "food_daily_summaries",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column(
            "generated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("user_id", "date", name="uq_food_daily_summaries_user_date"),
    )
    op.create_index(
        "idx_food_daily_summaries_user",
        "food_daily_summaries",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_index("idx_food_daily_summaries_user", table_name="food_daily_summaries")
    op.drop_table("food_daily_summaries")
