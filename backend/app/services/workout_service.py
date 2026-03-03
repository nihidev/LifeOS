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
    workout = await repo.upsert(db, user_id, data)
    return WorkoutResponse.model_validate(workout)


async def get_workout(
    db: AsyncSession, user_id: UUID, date: datetime.date
) -> WorkoutResponse | None:
    workout = await repo.get_by_date(db, user_id, date)
    return WorkoutResponse.model_validate(workout) if workout else None


async def get_streak(db: AsyncSession, user_id: UUID) -> StreakResponse:
    workouts = await repo.get_all(db, user_id)
    # Build a lookup dict: date → did_workout
    by_date: dict[datetime.date, bool] = {w.date: w.did_workout for w in workouts}

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

    workout_days = sum(1 for w in workouts if w.did_workout)
    rest_days = sum(1 for w in workouts if not w.did_workout)
    completion_percent = round(workout_days / days_in_month * 100, 1)

    return MonthlySummaryResponse(
        month=f"{year}-{month:02d}",
        total_days=days_in_month,
        workout_days=workout_days,
        rest_days=rest_days,
        completion_percent=completion_percent,
        entries=entries,
    )
