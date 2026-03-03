import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SelfAssessmentCreate(BaseModel):
    date: datetime.date
    performed_well_partner: bool
    note: str | None = None


class SelfAssessmentResponse(BaseModel):
    id: UUID
    date: datetime.date
    performed_well_partner: bool
    note: str | None
    integrity_score: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class SelfAssessmentHistoryResponse(BaseModel):
    entries: list[SelfAssessmentResponse]
    average_score: float
