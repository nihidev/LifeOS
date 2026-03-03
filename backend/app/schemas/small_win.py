import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SmallWinCreate(BaseModel):
    date: datetime.date
    text: str = Field(min_length=1, max_length=500)


class SmallWinUpdate(BaseModel):
    text: str = Field(min_length=1, max_length=500)


class SmallWinResponse(BaseModel):
    id: UUID
    date: datetime.date
    text: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
