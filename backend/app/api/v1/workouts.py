import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.core.deps import CurrentUser, DB
from app.schemas.workout import (
    MonthlySummaryResponse,
    StreakResponse,
    WorkoutCreate,
    WorkoutResponse,
)
from app.services import workout_service as service

router = APIRouter()


@router.post("/", response_model=WorkoutResponse, status_code=status.HTTP_200_OK)
async def log_workout(
    body: WorkoutCreate,
    db: DB,
    user_id: CurrentUser,
) -> WorkoutResponse:
    return await service.log_workout(db, user_id, body)


@router.get("/streak", response_model=StreakResponse)
async def get_streak(
    db: DB,
    user_id: CurrentUser,
) -> StreakResponse:
    return await service.get_streak(db, user_id)


@router.get("/monthly-summary", response_model=MonthlySummaryResponse)
async def get_monthly_summary(
    year: int,
    month: int,
    db: DB,
    user_id: CurrentUser,
) -> MonthlySummaryResponse:
    return await service.get_monthly_summary(db, user_id, year, month)


@router.get("/", response_model=list[WorkoutResponse])
async def get_workouts(
    date: datetime.date,
    db: DB,
    user_id: CurrentUser,
) -> list[WorkoutResponse]:
    return await service.get_workouts(db, user_id, date)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_workout(
    id: UUID,
    db: DB,
    user_id: CurrentUser,
) -> dict[str, str]:
    deleted = await service.delete_workout(db, user_id, id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Workout entry not found")
    return {"message": "deleted"}
