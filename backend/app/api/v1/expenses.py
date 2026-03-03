import datetime
from uuid import UUID

from fastapi import APIRouter, status

from app.core.deps import CurrentUser, DB
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseResponse,
    ExpenseUpdate,
    SummaryResponse,
)
from app.services import expense_service as service

router = APIRouter()


@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def add_expense(
    body: ExpenseCreate,
    db: DB,
    user_id: CurrentUser,
) -> ExpenseResponse:
    return await service.add_expense(db, user_id, body)


@router.get("/", response_model=list[ExpenseResponse])
async def get_expenses(
    date: datetime.date,
    db: DB,
    user_id: CurrentUser,
) -> list[ExpenseResponse]:
    return await service.get_expenses_by_date(db, user_id, date)


@router.get("/all", response_model=list[ExpenseResponse])
async def get_all_expenses(
    db: DB,
    user_id: CurrentUser,
) -> list[ExpenseResponse]:
    return await service.get_all_expenses(db, user_id)


@router.patch("/{id}", response_model=ExpenseResponse)
async def update_expense(
    id: UUID,
    body: ExpenseUpdate,
    db: DB,
    user_id: CurrentUser,
) -> ExpenseResponse:
    return await service.update_expense(db, user_id, id, body)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_expense(
    id: UUID,
    db: DB,
    user_id: CurrentUser,
) -> dict[str, str]:
    return await service.delete_expense(db, user_id, id)


@router.get("/summary/weekly", response_model=SummaryResponse)
async def get_weekly_summary(
    date: datetime.date,
    db: DB,
    user_id: CurrentUser,
) -> SummaryResponse:
    return await service.get_weekly_summary(db, user_id, date)


@router.get("/summary/monthly", response_model=SummaryResponse)
async def get_monthly_summary(
    year: int,
    month: int,
    db: DB,
    user_id: CurrentUser,
) -> SummaryResponse:
    return await service.get_monthly_summary(db, user_id, year, month)


@router.get("/summary/cumulative", response_model=SummaryResponse)
async def get_cumulative_summary(
    db: DB,
    user_id: CurrentUser,
) -> SummaryResponse:
    return await service.get_cumulative_summary(db, user_id)
