import datetime
from uuid import UUID

from fastapi import APIRouter, status

from app.core.deps import CurrentUser, DB
from app.schemas.food_log import FoodLogCreate, FoodLogResponse, WaterDateRequest, WaterIntakeResponse
from app.services import food_log_service as service

router = APIRouter()


@router.post("/", response_model=FoodLogResponse, status_code=status.HTTP_201_CREATED)
async def add_food_log(
    body: FoodLogCreate,
    db: DB,
    user_id: CurrentUser,
) -> FoodLogResponse:
    return await service.add_log(db, user_id, body)


@router.get("/water", response_model=WaterIntakeResponse)
async def get_water(
    date: datetime.date,
    db: DB,
    user_id: CurrentUser,
) -> WaterIntakeResponse:
    return await service.get_water(db, user_id, date)


@router.post("/water/increment", response_model=WaterIntakeResponse)
async def increment_water(
    body: WaterDateRequest,
    db: DB,
    user_id: CurrentUser,
) -> WaterIntakeResponse:
    return await service.increment_water(db, user_id, body.date)


@router.post("/water/decrement", response_model=WaterIntakeResponse)
async def decrement_water(
    body: WaterDateRequest,
    db: DB,
    user_id: CurrentUser,
) -> WaterIntakeResponse:
    return await service.decrement_water(db, user_id, body.date)


@router.get("/", response_model=list[FoodLogResponse])
async def get_food_logs(
    date: datetime.date,
    db: DB,
    user_id: CurrentUser,
) -> list[FoodLogResponse]:
    return await service.get_logs_by_date(db, user_id, date)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_food_log(
    id: UUID,
    db: DB,
    user_id: CurrentUser,
) -> dict[str, str]:
    return await service.delete_log(db, user_id, id)
