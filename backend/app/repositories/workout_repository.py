import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workout import Workout
from app.schemas.workout import WorkoutCreate


async def create(db: AsyncSession, user_id: UUID, data: WorkoutCreate) -> Workout:
    """Always insert a new workout entry (multiple per day allowed)."""
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
) -> list[Workout]:
    result = await db.execute(
        select(Workout)
        .where(Workout.user_id == user_id, Workout.date == date)
        .order_by(Workout.created_at.asc())
    )
    return list(result.scalars().all())


async def get_by_id(
    db: AsyncSession, user_id: UUID, id: UUID
) -> Workout | None:
    result = await db.execute(
        select(Workout).where(Workout.id == id, Workout.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def delete(db: AsyncSession, user_id: UUID, id: UUID) -> bool:
    workout = await get_by_id(db, user_id, id)
    if workout is None:
        return False
    await db.delete(workout)
    await db.flush()
    return True


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
        .order_by(Workout.date.asc())
    )
    return list(result.scalars().all())


async def get_all(db: AsyncSession, user_id: UUID) -> list[Workout]:
    result = await db.execute(
        select(Workout)
        .where(Workout.user_id == user_id)
        .order_by(Workout.date.desc())
    )
    return list(result.scalars().all())
