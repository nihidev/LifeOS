from uuid import UUID

from fastapi import APIRouter, status

from app.core.deps import CurrentUser, DB
from app.schemas.resolution import (
    AIAnalysisResponse,
    CheckInCreate,
    CheckInResponse,
    ProgressLogCreate,
    ProgressLogResponse,
    ResolutionCreate,
    ResolutionResponse,
    ResolutionUpdate,
)
from app.services import resolution_service as service

router = APIRouter()


@router.get("/analysis", response_model=AIAnalysisResponse)
async def get_analysis(
    db: DB,
    user_id: CurrentUser,
) -> AIAnalysisResponse:
    return await service.get_analysis(db, user_id)


@router.post("/", response_model=ResolutionResponse, status_code=status.HTTP_201_CREATED)
async def create_resolution(
    body: ResolutionCreate,
    db: DB,
    user_id: CurrentUser,
) -> ResolutionResponse:
    return await service.create_resolution(db, user_id, body)


@router.get("/", response_model=list[ResolutionResponse])
async def list_resolutions(
    db: DB,
    user_id: CurrentUser,
    status_filter: str | None = None,
) -> list[ResolutionResponse]:
    return await service.list_resolutions(db, user_id, status_filter)


@router.patch("/{id}", response_model=ResolutionResponse)
async def update_resolution(
    id: UUID,
    body: ResolutionUpdate,
    db: DB,
    user_id: CurrentUser,
) -> ResolutionResponse:
    return await service.update_resolution(db, user_id, id, body)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resolution(
    id: UUID,
    db: DB,
    user_id: CurrentUser,
) -> None:
    await service.delete_resolution(db, user_id, id)


@router.post("/{id}/progress-logs", response_model=ProgressLogResponse, status_code=status.HTTP_201_CREATED)
async def log_progress(
    id: UUID,
    body: ProgressLogCreate,
    db: DB,
    user_id: CurrentUser,
) -> ProgressLogResponse:
    return await service.log_progress(db, user_id, id, body)


@router.post("/{id}/generate-plan", response_model=ResolutionResponse)
async def generate_plan(
    id: UUID,
    db: DB,
    user_id: CurrentUser,
) -> ResolutionResponse:
    return await service.generate_plan(db, user_id, id)


@router.post("/{id}/calculate-progress", response_model=ResolutionResponse)
async def calculate_progress(
    id: UUID,
    db: DB,
    user_id: CurrentUser,
) -> ResolutionResponse:
    return await service.calculate_progress(db, user_id, id)


@router.post("/{id}/check-ins", response_model=CheckInResponse)
async def log_check_in(
    id: UUID,
    body: CheckInCreate,
    db: DB,
    user_id: CurrentUser,
) -> CheckInResponse:
    return await service.log_check_in(db, user_id, id, body)
