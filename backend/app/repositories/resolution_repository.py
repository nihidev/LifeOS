import datetime
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resolution import Resolution, ResolutionAICache, ResolutionCheckIn
from app.schemas.resolution import CheckInCreate, ResolutionCreate, ResolutionUpdate


async def create(db: AsyncSession, user_id: UUID, data: ResolutionCreate) -> Resolution:
    resolution = Resolution(
        user_id=user_id,
        title=data.title,
        description=data.description,
        target_date=data.target_date,
    )
    db.add(resolution)
    await db.flush()
    await db.refresh(resolution)
    return resolution


async def get_all(
    db: AsyncSession, user_id: UUID, status: str | None = None
) -> list[Resolution]:
    stmt = select(Resolution).where(Resolution.user_id == user_id)
    if status is not None:
        stmt = stmt.where(Resolution.status == status)
    stmt = stmt.order_by(Resolution.created_at.asc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, user_id: UUID, id: UUID) -> Resolution | None:
    result = await db.execute(
        select(Resolution).where(Resolution.id == id, Resolution.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def update(
    db: AsyncSession, user_id: UUID, id: UUID, data: ResolutionUpdate
) -> Resolution | None:
    resolution = await get_by_id(db, user_id, id)
    if resolution is None:
        return None
    if data.title is not None:
        resolution.title = data.title
    if data.description is not None:
        resolution.description = data.description
    if data.status is not None:
        resolution.status = data.status
    if data.progress_percent is not None:
        resolution.progress_percent = data.progress_percent
    if data.target_date is not None:
        resolution.target_date = data.target_date
    await db.flush()
    await db.refresh(resolution)
    return resolution


async def upsert_check_in(
    db: AsyncSession, user_id: UUID, resolution_id: UUID, data: CheckInCreate
) -> ResolutionCheckIn:
    # Check if a check-in already exists for this (resolution_id, year, month)
    result = await db.execute(
        select(ResolutionCheckIn).where(
            ResolutionCheckIn.resolution_id == resolution_id,
            ResolutionCheckIn.year == data.year,
            ResolutionCheckIn.month == data.month,
        )
    )
    existing = result.scalar_one_or_none()

    if existing is not None:
        existing.rating = data.rating
        existing.note = data.note
        await db.flush()
        await db.refresh(existing)
        return existing

    check_in = ResolutionCheckIn(
        user_id=user_id,
        resolution_id=resolution_id,
        year=data.year,
        month=data.month,
        rating=data.rating,
        note=data.note,
    )
    db.add(check_in)
    await db.flush()
    await db.refresh(check_in)
    return check_in


async def delete(db: AsyncSession, user_id: UUID, id: UUID) -> bool:
    resolution = await get_by_id(db, user_id, id)
    if resolution is None:
        return False
    await db.delete(resolution)
    await db.flush()
    return True


async def get_ai_cache(
    db: AsyncSession, user_id: UUID, date: datetime.date
) -> ResolutionAICache | None:
    result = await db.execute(
        select(ResolutionAICache).where(
            ResolutionAICache.user_id == user_id,
            ResolutionAICache.date == date,
        )
    )
    return result.scalar_one_or_none()


async def save_ai_cache(
    db: AsyncSession, user_id: UUID, date: datetime.date, analysis_dict: dict
) -> ResolutionAICache:
    cache = ResolutionAICache(
        user_id=user_id,
        date=date,
        analysis=analysis_dict,
    )
    db.add(cache)
    await db.flush()
    await db.refresh(cache)
    return cache
