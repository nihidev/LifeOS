import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

CATEGORIES = [
    "Groceries",
    "Transport",
    "Social Life",
    "Fitness",
    "Lifestyle",
    "Bills",
    "Self-improvement",
]


class ExpenseCreate(BaseModel):
    date: datetime.date
    amount: Decimal = Field(gt=Decimal("0"), decimal_places=2)
    category: str
    note: str | None = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if v not in CATEGORIES:
            raise ValueError(f"category must be one of {CATEGORIES}")
        return v


class ExpenseUpdate(BaseModel):
    amount: Decimal | None = Field(None, gt=Decimal("0"), decimal_places=2)
    category: str | None = None
    note: str | None = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str | None) -> str | None:
        if v is not None and v not in CATEGORIES:
            raise ValueError(f"category must be one of {CATEGORIES}")
        return v


class ExpenseResponse(BaseModel):
    id: UUID
    date: datetime.date
    amount: Decimal
    category: str
    note: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class CategorySummary(BaseModel):
    category: str
    total: Decimal
    count: int


class SummaryResponse(BaseModel):
    period: str
    total: Decimal
    by_category: list[CategorySummary]
