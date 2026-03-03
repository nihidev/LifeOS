import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseUpdate


async def create(db: AsyncSession, user_id: UUID, data: ExpenseCreate) -> Expense:
    expense = Expense(
        user_id=user_id,
        date=data.date,
        amount=data.amount,
        category=data.category,
        note=data.note,
    )
    db.add(expense)
    await db.flush()
    await db.refresh(expense)
    return expense


async def get_by_id(db: AsyncSession, user_id: UUID, id: UUID) -> Expense | None:
    result = await db.execute(
        select(Expense).where(Expense.id == id, Expense.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_by_date(
    db: AsyncSession, user_id: UUID, date: datetime.date
) -> list[Expense]:
    result = await db.execute(
        select(Expense)
        .where(Expense.user_id == user_id, Expense.date == date)
        .order_by(Expense.created_at.asc())
    )
    return list(result.scalars().all())


async def get_by_range(
    db: AsyncSession,
    user_id: UUID,
    start: datetime.date,
    end: datetime.date,
) -> list[Expense]:
    result = await db.execute(
        select(Expense)
        .where(
            Expense.user_id == user_id,
            Expense.date >= start,
            Expense.date <= end,
        )
        .order_by(Expense.date.asc())
    )
    return list(result.scalars().all())


async def get_all(db: AsyncSession, user_id: UUID) -> list[Expense]:
    result = await db.execute(
        select(Expense)
        .where(Expense.user_id == user_id)
        .order_by(Expense.date.desc())
    )
    return list(result.scalars().all())


async def update(
    db: AsyncSession, user_id: UUID, id: UUID, data: ExpenseUpdate
) -> Expense | None:
    expense = await get_by_id(db, user_id, id)
    if expense is None:
        return None
    if data.amount is not None:
        expense.amount = data.amount
    if data.category is not None:
        expense.category = data.category
    if data.note is not None:
        expense.note = data.note
    await db.flush()
    await db.refresh(expense)
    return expense


async def delete(db: AsyncSession, user_id: UUID, id: UUID) -> bool:
    expense = await get_by_id(db, user_id, id)
    if expense is None:
        return False
    await db.delete(expense)
    await db.flush()
    return True
