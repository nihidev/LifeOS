import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.self_assessment import SelfAssessment
from app.schemas.self_assessment import SelfAssessmentCreate


async def upsert(
    db: AsyncSession, user_id: UUID, data: SelfAssessmentCreate, integrity_score: int
) -> SelfAssessment:
    existing = await get_by_date(db, user_id, data.date)
    if existing:
        existing.performed_well_partner = data.performed_well_partner
        existing.note = data.note
        existing.integrity_score = integrity_score
        existing.updated_at = datetime.datetime.now(datetime.timezone.utc)
        await db.flush()
        await db.refresh(existing)
        return existing

    assessment = SelfAssessment(
        user_id=user_id,
        date=data.date,
        performed_well_partner=data.performed_well_partner,
        note=data.note,
        integrity_score=integrity_score,
    )
    db.add(assessment)
    await db.flush()
    await db.refresh(assessment)
    return assessment


async def get_by_date(
    db: AsyncSession, user_id: UUID, date: datetime.date
) -> SelfAssessment | None:
    result = await db.execute(
        select(SelfAssessment).where(
            SelfAssessment.user_id == user_id, SelfAssessment.date == date
        )
    )
    return result.scalar_one_or_none()


async def get_history(
    db: AsyncSession, user_id: UUID, limit: int, offset: int
) -> list[SelfAssessment]:
    result = await db.execute(
        select(SelfAssessment)
        .where(SelfAssessment.user_id == user_id)
        .order_by(SelfAssessment.date.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def get_average_score(db: AsyncSession, user_id: UUID) -> float:
    result = await db.execute(
        select(func.avg(SelfAssessment.integrity_score)).where(
            SelfAssessment.user_id == user_id
        )
    )
    avg = result.scalar_one_or_none()
    return round(float(avg), 1) if avg is not None else 0.0
