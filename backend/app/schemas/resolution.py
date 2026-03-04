from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

VALID_STATUSES = ["not_started", "in_progress", "completed"]


class AIPlanMonth(BaseModel):
    month_label: str
    goal: str
    actions: list[str]

    model_config = ConfigDict(from_attributes=True)


class ResolutionCreate(BaseModel):
    title: str = Field(min_length=1)
    description: str | None = None
    target_date: date | None = None


class ResolutionUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    progress_percent: int | None = Field(None, ge=0, le=100)
    target_date: date | None = None
    ai_plan: list[dict] | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        if v is not None and v not in VALID_STATUSES:
            raise ValueError(f"status must be one of {VALID_STATUSES}")
        return v


class ProgressLogCreate(BaseModel):
    progress_percent: int = Field(ge=0, le=100)
    note: str | None = None


class ProgressLogResponse(BaseModel):
    id: UUID
    progress_percent: int
    note: str | None
    logged_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CheckInCreate(BaseModel):
    year: int
    month: int
    rating: int = Field(ge=1, le=5)
    note: str | None = None


class CheckInResponse(BaseModel):
    id: UUID
    resolution_id: UUID
    year: int
    month: int
    rating: int
    note: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResolutionResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    status: str
    progress_percent: int
    target_date: date | None
    ai_plan: list[AIPlanMonth] | None = None
    created_at: datetime
    updated_at: datetime
    check_ins: list[CheckInResponse] = []
    progress_logs: list[ProgressLogResponse] = []

    model_config = ConfigDict(from_attributes=True)


class AIAnalysisItem(BaseModel):
    resolution_id: str
    resolution_title: str
    signal: str  # "on_track" | "at_risk" | "no_signal"
    evidence: list[str]
    suggestion: str


class AIAnalysisResponse(BaseModel):
    generated_at: str  # ISO date
    analyses: list[AIAnalysisItem]
