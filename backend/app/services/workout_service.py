import calendar
import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import workout_repository as repo
from app.schemas.workout import (
    MonthlySummaryResponse,
    StreakResponse,
    WorkoutCreate,
    WorkoutResponse,
)


async def log_workout(
    db: AsyncSession, user_id: UUID, data: WorkoutCreate
) -> WorkoutResponse:
    workout = await repo.create(db, user_id, data)
    return WorkoutResponse.model_validate(workout)


async def get_workouts(
    db: AsyncSession, user_id: UUID, date: datetime.date
) -> list[WorkoutResponse]:
    workouts = await repo.get_by_date(db, user_id, date)
    return [WorkoutResponse.model_validate(w) for w in workouts]


async def delete_workout(
    db: AsyncSession, user_id: UUID, id: UUID
) -> bool:
    return await repo.delete(db, user_id, id)


async def get_streak(db: AsyncSession, user_id: UUID) -> StreakResponse:
    workouts = await repo.get_all(db, user_id)

    # Build per-date lookup: date → True if ANY entry has did_workout=True
    by_date: dict[datetime.date, bool] = {}
    for w in workouts:
        by_date[w.date] = by_date.get(w.date, False) or w.did_workout

    today = datetime.date.today()

    # Current streak: walk back from today
    current_streak = 0
    day = today
    while True:
        val = by_date.get(day)
        if val is True:
            current_streak += 1
            day -= datetime.timedelta(days=1)
        else:
            break

    # Longest streak: scan all history
    if not by_date:
        return StreakResponse(current_streak=current_streak, longest_streak=0)

    dates = sorted(by_date.keys())
    longest = 0
    run = 0
    for d in dates:
        if by_date[d]:
            run += 1
            longest = max(longest, run)
        else:
            run = 0

    return StreakResponse(current_streak=current_streak, longest_streak=longest)


async def get_monthly_summary(
    db: AsyncSession, user_id: UUID, year: int, month: int
) -> MonthlySummaryResponse:
    days_in_month = calendar.monthrange(year, month)[1]
    start = datetime.date(year, month, 1)
    end = datetime.date(year, month, days_in_month)

    workouts = await repo.get_range(db, user_id, start, end)
    entries = [WorkoutResponse.model_validate(w) for w in workouts]

    # Aggregate by date: a day counts as workout if ANY entry has did_workout=True
    by_date: dict[datetime.date, bool] = {}
    for w in workouts:
        by_date[w.date] = by_date.get(w.date, False) or w.did_workout

    workout_days = sum(1 for v in by_date.values() if v)
    rest_days = sum(1 for v in by_date.values() if not v)
    completion_percent = round(workout_days / days_in_month * 100, 1)

    return MonthlySummaryResponse(
        month=f"{year}-{month:02d}",
        total_days=days_in_month,
        workout_days=workout_days,
        rest_days=rest_days,
        completion_percent=completion_percent,
        entries=entries,
    )
