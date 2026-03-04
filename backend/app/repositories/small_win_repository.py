import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.models.small_win import SmallWin
from app.schemas.small_win import DayCount, SmallWinCreate, SmallWinStats, SmallWinUpdate


async def create(db: AsyncSession, user_id: UUID, data: SmallWinCreate) -> SmallWin:
    win = SmallWin(
        user_id=user_id,
        date=data.date,
        text=data.text,
        entry_type=data.entry_type,
        completed=data.completed,
        category=data.category,
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
    if data.category is not None:
        win.category = data.category
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


async def get_stats(
    db: AsyncSession, user_id: UUID, today: datetime.date
) -> SmallWinStats:
    # All-time total wins (wins + completed tasks)
    all_result = await db.execute(
        select(SmallWin).where(SmallWin.user_id == user_id)
    )
    all_rows = list(all_result.scalars().all())

    total_wins = sum(
        1
        for row in all_rows
        if row.entry_type == "win"
        or (row.entry_type == "task" and row.completed is True)
    )

    # Build per-day counts for last 7 days
    day_counts: dict[datetime.date, int] = {}
    for row in all_rows:
        qualifies = row.entry_type == "win" or (
            row.entry_type == "task" and row.completed is True
        )
        if qualifies:
            day_counts[row.date] = day_counts.get(row.date, 0) + 1

    wins_last_7_days = []
    for offset in range(6, -1, -1):
        day = today - datetime.timedelta(days=offset)
        wins_last_7_days.append(DayCount(date=day, count=day_counts.get(day, 0)))

    return SmallWinStats(total_wins=total_wins, wins_last_7_days=wins_last_7_days)
