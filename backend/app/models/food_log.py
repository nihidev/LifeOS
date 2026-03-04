from datetime import date as date_type
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, Index, Integer, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


class FoodLog(Base):
    __tablename__ = "food_logs"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    date: Mapped[date_type] = mapped_column(Date, nullable=False)
    consumed_at: Mapped[str] = mapped_column(Text, nullable=False)  # HH:MM
    food_item: Mapped[str] = mapped_column(Text, nullable=False)
    ai_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("idx_food_logs_user_date", "user_id", "date"),
    )


class WaterIntake(Base):
    __tablename__ = "water_intake"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    date: Mapped[date_type] = mapped_column(Date, nullable=False)
    glasses: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_water_intake_user_date"),
    )


class FoodDailySummary(Base):
    __tablename__ = "food_daily_summaries"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    date: Mapped[date_type] = mapped_column(Date, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_food_daily_summaries_user_date"),
        Index("idx_food_daily_summaries_user", "user_id"),
    )
