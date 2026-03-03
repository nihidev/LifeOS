import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SmallWinCreate(BaseModel):
    date: datetime.date
    text: str = Field(min_length=1, max_length=500)
    entry_type: str = "win"
    completed: bool | None = None


class SmallWinUpdate(BaseModel):
    text: str | None = Field(None, min_length=1, max_length=500)
    completed: bool | None = None


class SmallWinResponse(BaseModel):
    id: UUID
    date: datetime.date
    text: str
    entry_type: str
    completed: bool | None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
