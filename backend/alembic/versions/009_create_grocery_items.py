"""create grocery_items table

Revision ID: 009
Revises: 008
Create Date: 2026-03-03

"""
from alembic import op
import sqlalchemy as sa

revision = "009"
down_revision = "008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "grocery_items",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("item", sa.Text(), nullable=False),
        sa.Column("quantity", sa.Text(), nullable=True),
        sa.Column("checked", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["auth.users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_grocery_items_user", "grocery_items", ["user_id"])


def downgrade() -> None:
    op.drop_index("idx_grocery_items_user", table_name="grocery_items")
    op.drop_table("grocery_items")
