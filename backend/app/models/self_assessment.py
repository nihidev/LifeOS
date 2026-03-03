from datetime import date as date_type
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Date, DateTime, Index, Integer, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


class SelfAssessment(Base):
    __tablename__ = "self_assessments"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    date: Mapped[date_type] = mapped_column(Date, nullable=False)
    performed_well_partner: Mapped[bool] = mapped_column(Boolean, nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    integrity_score: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_self_assessments_user_date"),
        Index("idx_self_assessments_user_date", "user_id", "date"),
    )
