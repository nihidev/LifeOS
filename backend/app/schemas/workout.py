import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WorkoutCreate(BaseModel):
    date: datetime.date
    did_workout: bool
    activity_type: str | None = None
    duration_mins: int | None = None
    notes: str | None = None


class WorkoutResponse(BaseModel):
    id: UUID
    date: datetime.date
    did_workout: bool
    activity_type: str | None
    duration_mins: int | None
    notes: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class StreakResponse(BaseModel):
    current_streak: int
    longest_streak: int


class MonthlySummaryResponse(BaseModel):
    month: str
    total_days: int
    workout_days: int
    rest_days: int
    completion_percent: float
    entries: list[WorkoutResponse]
