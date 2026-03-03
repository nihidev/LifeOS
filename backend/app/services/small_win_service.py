import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import small_win_repository as repo
from app.schemas.small_win import SmallWinCreate, SmallWinResponse, SmallWinUpdate


async def create_win(
    db: AsyncSession, user_id: UUID, data: SmallWinCreate
) -> SmallWinResponse:
    win = await repo.create(db, user_id, data)
    return SmallWinResponse.model_validate(win)


async def get_wins_by_date(
    db: AsyncSession, user_id: UUID, date: datetime.date
) -> list[SmallWinResponse]:
    wins = await repo.get_by_date(db, user_id, date)
    return [SmallWinResponse.model_validate(w) for w in wins]


async def update_win(
    db: AsyncSession, user_id: UUID, id: UUID, data: SmallWinUpdate
) -> SmallWinResponse:
    win = await repo.update(db, user_id, id, data)
    if win is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Win not found")
    return SmallWinResponse.model_validate(win)


async def delete_win(
    db: AsyncSession, user_id: UUID, id: UUID
) -> dict[str, str]:
    deleted = await repo.delete(db, user_id, id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Win not found")
    return {"message": "deleted"}
