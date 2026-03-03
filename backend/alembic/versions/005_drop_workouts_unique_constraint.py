"""drop unique constraint on workouts to allow multiple entries per day

Revision ID: 005
Revises: 004
Create Date: 2026-03-03

"""
from alembic import op

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("uq_workouts_user_date", "workouts", type_="unique")


def downgrade() -> None:
    op.create_unique_constraint(
        "uq_workouts_user_date", "workouts", ["user_id", "date"]
    )
