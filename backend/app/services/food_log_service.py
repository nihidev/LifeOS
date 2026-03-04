import datetime
import logging
from uuid import UUID

from fastapi import HTTPException
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repositories import food_log_repository as repo
from app.schemas.food_log import (
    FoodDailySummaryResponse,
    FoodLogCreate,
    FoodLogResponse,
    WaterIntakeResponse,
)

logger = logging.getLogger(__name__)

_SUMMARY_PROMPT = (
    "You are a concise nutrition advisor. Today the user logged these foods: {foods}.\n\n"
    "In 2–4 sentences, do the following:\n"
    "1. Identify what nutrients and food groups are well covered (protein, carbs, healthy fats, etc.)\n"
    "2. Point out what is MISSING for a balanced diet (vegetables, fruits, minerals, fiber, dairy, etc.)\n"
    "3. If any junk food or highly processed food is present, flag it briefly\n"
    "4. End with a short encouraging recommendation for a balanced diet\n\n"
    "Rules: Do NOT mention calories or specific quantities. Be honest but encouraging. Keep it under 80 words."
)


async def add_log(
    db: AsyncSession, user_id: UUID, data: FoodLogCreate
) -> FoodLogResponse:
    entry = await repo.create(db, user_id, data, ai_comment=None)
    return FoodLogResponse.model_validate(entry)


async def get_logs_by_date(
    db: AsyncSession, user_id: UUID, date: datetime.date
) -> list[FoodLogResponse]:
    entries = await repo.get_by_date(db, user_id, date)
    return [FoodLogResponse.model_validate(e) for e in entries]


async def delete_log(db: AsyncSession, user_id: UUID, id: UUID) -> dict[str, str]:
    deleted = await repo.delete(db, user_id, id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Food log entry not found")
    return {"message": "deleted"}


async def get_water(
    db: AsyncSession, user_id: UUID, date: datetime.date
) -> WaterIntakeResponse:
    row = await repo.get_water(db, user_id, date)
    if row is None:
        return WaterIntakeResponse(date=date, glasses=0)
    return WaterIntakeResponse.model_validate(row)


async def increment_water(
    db: AsyncSession, user_id: UUID, date: datetime.date
) -> WaterIntakeResponse:
    row = await repo.get_water(db, user_id, date)
    current = row.glasses if row else 0
    updated = await repo.upsert_water(db, user_id, date, current + 1)
    return WaterIntakeResponse.model_validate(updated)


async def decrement_water(
    db: AsyncSession, user_id: UUID, date: datetime.date
) -> WaterIntakeResponse:
    row = await repo.get_water(db, user_id, date)
    current = row.glasses if row else 0
    new_val = max(0, current - 1)
    if new_val == current:
        return WaterIntakeResponse(date=date, glasses=0)
    updated = await repo.upsert_water(db, user_id, date, new_val)
    return WaterIntakeResponse.model_validate(updated)


async def get_daily_summary(
    db: AsyncSession, user_id: UUID, date: datetime.date
) -> FoodDailySummaryResponse | None:
    row = await repo.get_daily_summary(db, user_id, date)
    if row is None:
        return None
    return FoodDailySummaryResponse.model_validate(row)


async def generate_daily_summary(
    db: AsyncSession, user_id: UUID, date: datetime.date
) -> FoodDailySummaryResponse:
    entries = await repo.get_by_date(db, user_id, date)
    if not entries:
        raise HTTPException(status_code=400, detail="No food logged for this date")

    foods = ", ".join(e.food_item for e in entries)
    summary_text = await _call_openai_summary(foods)

    row = await repo.upsert_daily_summary(db, user_id, date, summary_text)
    return FoodDailySummaryResponse.model_validate(row)


async def _call_openai_summary(foods: str) -> str:
    if not settings.OPENAI_API_KEY:
        return f"Foods logged: {foods}. (AI summary unavailable — no API key configured.)"
    try:
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        prompt = _SUMMARY_PROMPT.format(foods=foods)
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        logger.warning("Daily summary generation failed: %s", exc)
        raise HTTPException(status_code=502, detail="AI summary generation failed") from exc
