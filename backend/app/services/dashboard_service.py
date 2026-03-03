import calendar
import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import (
    expense_repository,
    resolution_repository,
    self_assessment_repository,
    small_win_repository,
    workout_repository,
)
from app.schemas.dashboard import DashboardResponse


async def get_dashboard(db: AsyncSession, user_id: UUID) -> DashboardResponse:
    today = datetime.date.today()

    # --- Small wins today (wins + completed tasks) ---
    wins_today = await small_win_repository.get_by_date(db, user_id, today)
    small_wins_today = sum(
        1
        for w in wins_today
        if w.entry_type == "win" or (w.entry_type == "task" and w.completed)
    )

    # --- Self assessment: today + last 7 days ---
    assessment_today = await self_assessment_repository.get_by_date(db, user_id, today)
    integrity_score_today = assessment_today.integrity_score if assessment_today else None

    last_7_days_integrity: list[int | None] = []
    for i in range(6, -1, -1):  # 6 days ago → today
        day = today - datetime.timedelta(days=i)
        record = await self_assessment_repository.get_by_date(db, user_id, day)
        last_7_days_integrity.append(record.integrity_score if record else None)

    # --- Workouts: streak + did_workout_today ---
    all_workouts = await workout_repository.get_all(db, user_id)
    by_date: dict[datetime.date, bool] = {}
    for w in all_workouts:
        by_date[w.date] = by_date.get(w.date, False) or w.did_workout

    did_workout_today = by_date.get(today, False)

    workout_streak = 0
    day = today
    while True:
        if by_date.get(day) is True:
            workout_streak += 1
            day -= datetime.timedelta(days=1)
        else:
            break

    # --- Expenses: monthly total + by-category summary ---
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    month_start = datetime.date(today.year, today.month, 1)
    month_end = datetime.date(today.year, today.month, days_in_month)
    month_expenses = await expense_repository.get_by_range(db, user_id, month_start, month_end)

    monthly_expense_total = sum(
        (e.amount for e in month_expenses), Decimal("0")
    )
    expense_summary: dict[str, Decimal] = {}
    for e in month_expenses:
        expense_summary[e.category] = expense_summary.get(e.category, Decimal("0")) + e.amount

    # --- Resolutions: active + completed counts ---
    all_resolutions = await resolution_repository.get_all(db, user_id)
    active_resolutions = sum(
        1 for r in all_resolutions if r.status in ("not_started", "in_progress")
    )
    completed_resolutions = sum(
        1 for r in all_resolutions if r.status == "completed"
    )

    return DashboardResponse(
        date=today,
        integrity_score_today=integrity_score_today,
        workout_streak=workout_streak,
        did_workout_today=did_workout_today,
        monthly_expense_total=monthly_expense_total,
        active_resolutions=active_resolutions,
        completed_resolutions=completed_resolutions,
        small_wins_today=small_wins_today,
        last_7_days_integrity=last_7_days_integrity,
        expense_summary_this_month=expense_summary,
    )
