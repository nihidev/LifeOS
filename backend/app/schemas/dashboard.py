import datetime
from decimal import Decimal

from pydantic import BaseModel


class DashboardResponse(BaseModel):
    date: datetime.date
    integrity_score_today: int | None
    workout_streak: int
    did_workout_today: bool
    monthly_expense_total: Decimal
    active_resolutions: int
    completed_resolutions: int
    small_wins_today: int
    last_7_days_integrity: list[int | None]
    expense_summary_this_month: dict[str, Decimal]
