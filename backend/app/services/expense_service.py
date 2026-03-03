import calendar
import datetime
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import expense_repository as repo
from app.schemas.expense import (
    CategorySummary,
    ExpenseCreate,
    ExpenseResponse,
    ExpenseUpdate,
    SummaryResponse,
)
from app.models.expense import Expense


def _build_summary(entries: list[Expense], period: str) -> SummaryResponse:
    total = sum(e.amount for e in entries) if entries else Decimal("0")

    by_cat: dict[str, dict] = {}
    for e in entries:
        if e.category not in by_cat:
            by_cat[e.category] = {"total": Decimal("0"), "count": 0}
        by_cat[e.category]["total"] += e.amount
        by_cat[e.category]["count"] += 1

    by_category = sorted(
        [
            CategorySummary(category=cat, total=vals["total"], count=vals["count"])
            for cat, vals in by_cat.items()
        ],
        key=lambda x: x.total,
        reverse=True,
    )

    return SummaryResponse(period=period, total=total, by_category=by_category)


async def add_expense(
    db: AsyncSession, user_id: UUID, data: ExpenseCreate
) -> ExpenseResponse:
    expense = await repo.create(db, user_id, data)
    return ExpenseResponse.model_validate(expense)


async def get_expenses_by_date(
    db: AsyncSession, user_id: UUID, date: datetime.date
) -> list[ExpenseResponse]:
    expenses = await repo.get_by_date(db, user_id, date)
    return [ExpenseResponse.model_validate(e) for e in expenses]


async def update_expense(
    db: AsyncSession, user_id: UUID, id: UUID, data: ExpenseUpdate
) -> ExpenseResponse:
    expense = await repo.update(db, user_id, id, data)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return ExpenseResponse.model_validate(expense)


async def delete_expense(
    db: AsyncSession, user_id: UUID, id: UUID
) -> dict[str, str]:
    deleted = await repo.delete(db, user_id, id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "deleted"}


async def get_weekly_summary(
    db: AsyncSession, user_id: UUID, date: datetime.date
) -> SummaryResponse:
    week_start = date - datetime.timedelta(days=date.weekday())
    week_end = week_start + datetime.timedelta(days=6)
    iso = date.isocalendar()
    period = f"{iso.year}-W{iso.week:02d}"
    entries = await repo.get_by_range(db, user_id, week_start, week_end)
    return _build_summary(entries, period)


async def get_monthly_summary(
    db: AsyncSession, user_id: UUID, year: int, month: int
) -> SummaryResponse:
    days_in_month = calendar.monthrange(year, month)[1]
    start = datetime.date(year, month, 1)
    end = datetime.date(year, month, days_in_month)
    period = f"{year}-{month:02d}"
    entries = await repo.get_by_range(db, user_id, start, end)
    return _build_summary(entries, period)


async def get_cumulative_summary(
    db: AsyncSession, user_id: UUID
) -> SummaryResponse:
    entries = await repo.get_all(db, user_id)
    return _build_summary(entries, "all-time")


async def get_all_expenses(
    db: AsyncSession, user_id: UUID
) -> list[ExpenseResponse]:
    entries = await repo.get_all(db, user_id)
    return [ExpenseResponse.model_validate(e) for e in entries]
