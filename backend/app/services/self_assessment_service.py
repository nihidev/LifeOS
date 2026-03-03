import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import self_assessment_repository as repo
from app.schemas.self_assessment import (
    SelfAssessmentCreate,
    SelfAssessmentHistoryResponse,
    SelfAssessmentResponse,
)


def _calc_score(performed_well: bool) -> int:
    return 100 if performed_well else 0


async def save_assessment(
    db: AsyncSession, user_id: UUID, data: SelfAssessmentCreate
) -> SelfAssessmentResponse:
    score = _calc_score(data.performed_well_partner)
    assessment = await repo.upsert(db, user_id, data, score)
    return SelfAssessmentResponse.model_validate(assessment)


async def get_assessment(
    db: AsyncSession, user_id: UUID, date: datetime.date
) -> SelfAssessmentResponse | None:
    assessment = await repo.get_by_date(db, user_id, date)
    return SelfAssessmentResponse.model_validate(assessment) if assessment else None


async def get_history(
    db: AsyncSession, user_id: UUID, limit: int, offset: int
) -> SelfAssessmentHistoryResponse:
    entries = await repo.get_history(db, user_id, limit, offset)
    average = await repo.get_average_score(db, user_id)
    return SelfAssessmentHistoryResponse(
        entries=[SelfAssessmentResponse.model_validate(e) for e in entries],
        average_score=average,
    )
