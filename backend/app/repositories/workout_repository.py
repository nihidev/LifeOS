import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workout import Workout
from app.schemas.workout import WorkoutCreate


async def upsert(db: AsyncSession, user_id: UUID, data: WorkoutCreate) -> Workout:
    """Create a workout entry, or replace it if one already exists for that date."""
    existing = await get_by_date(db, user_id, data.date)
    if existing:
        existing.did_workout = data.did_workout
        existing.activity_type = data.activity_type
        existing.duration_mins = data.duration_mins
        existing.notes = data.notes
        existing.updated_at = datetime.datetime.now(datetime.timezone.utc)
        await db.flush()
        await db.refresh(existing)
        return existing

    workout = Workout(
        user_id=user_id,
        date=data.date,
        did_workout=data.did_workout,
        activity_type=data.activity_type,
        duration_mins=data.duration_mins,
        notes=data.notes,
    )
    db.add(workout)
    await db.flush()
    await db.refresh(workout)
    return workout


async def get_by_date(
    db: AsyncSession, user_id: UUID, date: datetime.date
) -> Workout | None:
    result = await db.execute(
        select(Workout).where(Workout.user_id == user_id, Workout.date == date)
    )
    return result.scalar_one_or_none()


async def get_range(
    db: AsyncSession,
    user_id: UUID,
    start: datetime.date,
    end: datetime.date,
) -> list[Workout]:
    result = await db.execute(
        select(Workout)
        .where(
            Workout.user_id == user_id,
            Workout.date >= start,
            Workout.date <= end,
        )
        .order_by(Workout.date.desc())
    )
    return list(result.scalars().all())


async def get_all(db: AsyncSession, user_id: UUID) -> list[Workout]:
    result = await db.execute(
        select(Workout)
        .where(Workout.user_id == user_id)
        .order_by(Workout.date.desc())
    )
    return list(result.scalars().all())
