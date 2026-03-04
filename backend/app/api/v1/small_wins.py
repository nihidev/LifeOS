import datetime
from uuid import UUID

from fastapi import APIRouter, status

from app.core.deps import CurrentUser, DB
from app.schemas.small_win import SmallWinCreate, SmallWinResponse, SmallWinStats, SmallWinUpdate
from app.services import small_win_service as service

router = APIRouter()


@router.post("/", response_model=SmallWinResponse, status_code=status.HTTP_201_CREATED)
async def create_win(
    body: SmallWinCreate,
    db: DB,
    user_id: CurrentUser,
) -> SmallWinResponse:
    return await service.create_win(db, user_id, body)


@router.get("/", response_model=list[SmallWinResponse])
async def get_wins_by_date(
    date: datetime.date,
    db: DB,
    user_id: CurrentUser,
) -> list[SmallWinResponse]:
    return await service.get_wins_by_date(db, user_id, date)


@router.get("/stats", response_model=SmallWinStats)
async def get_stats(
    db: DB,
    user_id: CurrentUser,
) -> SmallWinStats:
    return await service.get_stats(db, user_id)


@router.patch("/{id}", response_model=SmallWinResponse)
async def update_win(
    id: UUID,
    body: SmallWinUpdate,
    db: DB,
    user_id: CurrentUser,
) -> SmallWinResponse:
    return await service.update_win(db, user_id, id, body)


@router.delete("/{id}")
async def delete_win(
    id: UUID,
    db: DB,
    user_id: CurrentUser,
) -> dict[str, str]:
    return await service.delete_win(db, user_id, id)
