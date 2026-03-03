import datetime

from fastapi import APIRouter, status

from app.core.deps import CurrentUser, DB
from app.schemas.self_assessment import (
    SelfAssessmentCreate,
    SelfAssessmentHistoryResponse,
    SelfAssessmentResponse,
)
from app.services import self_assessment_service as service

router = APIRouter()


@router.post("/", response_model=SelfAssessmentResponse, status_code=status.HTTP_200_OK)
async def save_assessment(
    body: SelfAssessmentCreate,
    db: DB,
    user_id: CurrentUser,
) -> SelfAssessmentResponse:
    return await service.save_assessment(db, user_id, body)


@router.get("/history", response_model=SelfAssessmentHistoryResponse)
async def get_history(
    db: DB,
    user_id: CurrentUser,
    limit: int = 30,
    offset: int = 0,
) -> SelfAssessmentHistoryResponse:
    return await service.get_history(db, user_id, limit, offset)


@router.get("/", response_model=SelfAssessmentResponse | None)
async def get_assessment(
    date: datetime.date,
    db: DB,
    user_id: CurrentUser,
) -> SelfAssessmentResponse | None:
    return await service.get_assessment(db, user_id, date)
