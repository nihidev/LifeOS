import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.models.small_win import SmallWin
from app.schemas.small_win import SmallWinCreate, SmallWinUpdate


async def create(db: AsyncSession, user_id: UUID, data: SmallWinCreate) -> SmallWin:
    win = SmallWin(
        user_id=user_id,
        date=data.date,
        text=data.text,
        entry_type=data.entry_type,
        completed=data.completed,
    )
    db.add(win)
    await db.flush()
    await db.refresh(win)
    return win


async def get_by_date(
    db: AsyncSession, user_id: UUID, date: datetime.date
) -> list[SmallWin]:
    result = await db.execute(
        select(SmallWin)
        .where(SmallWin.user_id == user_id, SmallWin.date == date)
        .order_by(SmallWin.created_at.desc())
    )
    return list(result.scalars().all())


async def get_by_id(
    db: AsyncSession, user_id: UUID, id: UUID
) -> SmallWin | None:
    result = await db.execute(
        select(SmallWin).where(SmallWin.id == id, SmallWin.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def update(
    db: AsyncSession, user_id: UUID, id: UUID, data: SmallWinUpdate
) -> SmallWin | None:
    win = await get_by_id(db, user_id, id)
    if win is None:
        return None
    if data.text is not None:
        win.text = data.text
    if data.completed is not None:
        win.completed = data.completed
    win.updated_at = func.now()
    await db.flush()
    await db.refresh(win)
    return win


async def delete(db: AsyncSession, user_id: UUID, id: UUID) -> bool:
    win = await get_by_id(db, user_id, id)
    if win is None:
        return False
    await db.delete(win)
    await db.flush()
    return True
