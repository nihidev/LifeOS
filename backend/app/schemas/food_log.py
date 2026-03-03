import datetime
import re
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator


class FoodLogCreate(BaseModel):
    date: datetime.date
    consumed_at: str  # HH:MM
    food_item: str

    @field_validator("consumed_at")
    @classmethod
    def validate_time(cls, v: str) -> str:
        if not re.match(r"^\d{2}:\d{2}$", v):
            raise ValueError("consumed_at must be in HH:MM format")
        return v


class FoodLogResponse(BaseModel):
    id: UUID
    date: datetime.date
    consumed_at: str
    food_item: str
    ai_comment: str | None
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class WaterIntakeResponse(BaseModel):
    date: datetime.date
    glasses: int

    model_config = ConfigDict(from_attributes=True)


class WaterDateRequest(BaseModel):
    date: datetime.date
