import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.food_log import FoodLog, WaterIntake
from app.schemas.food_log import FoodLogCreate


async def create(
    db: AsyncSession, user_id: UUID, data: FoodLogCreate, ai_comment: str | None
) -> FoodLog:
    entry = FoodLog(
        user_id=user_id,
        date=data.date,
        consumed_at=data.consumed_at,
        food_item=data.food_item,
        ai_comment=ai_comment,
    )
    db.add(entry)
    await db.flush()
    await db.refresh(entry)
    return entry


async def get_by_date(
    db: AsyncSession, user_id: UUID, date: datetime.date
) -> list[FoodLog]:
    result = await db.execute(
        select(FoodLog)
        .where(FoodLog.user_id == user_id, FoodLog.date == date)
        .order_by(FoodLog.consumed_at.asc(), FoodLog.created_at.asc())
    )
    return list(result.scalars().all())


async def get_by_id(
    db: AsyncSession, user_id: UUID, id: UUID
) -> FoodLog | None:
    result = await db.execute(
        select(FoodLog).where(FoodLog.id == id, FoodLog.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def delete(db: AsyncSession, user_id: UUID, id: UUID) -> bool:
    entry = await get_by_id(db, user_id, id)
    if entry is None:
        return False
    await db.delete(entry)
    await db.flush()
    return True


async def get_water(
    db: AsyncSession, user_id: UUID, date: datetime.date
) -> WaterIntake | None:
    result = await db.execute(
        select(WaterIntake).where(
            WaterIntake.user_id == user_id, WaterIntake.date == date
        )
    )
    return result.scalar_one_or_none()


async def upsert_water(
    db: AsyncSession, user_id: UUID, date: datetime.date, glasses: int
) -> WaterIntake:
    """Upsert a water_intake row; SQLite-compatible path via ORM."""
    row = await get_water(db, user_id, date)
    if row is None:
        row = WaterIntake(user_id=user_id, date=date, glasses=glasses)
        db.add(row)
    else:
        row.glasses = glasses
    await db.flush()
    await db.refresh(row)
    return row
