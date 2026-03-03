import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class GroceryItemCreate(BaseModel):
    item: str
    quantity: str | None = None


class GroceryItemUpdate(BaseModel):
    item: str | None = None
    quantity: str | None = None
    checked: bool | None = None


class GroceryItemResponse(BaseModel):
    id: UUID
    item: str
    quantity: str | None
    checked: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class ClearCheckedResponse(BaseModel):
    deleted_count: int
