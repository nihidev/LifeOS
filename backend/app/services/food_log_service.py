import datetime
import logging
from uuid import UUID

from fastapi import HTTPException
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repositories import food_log_repository as repo
from app.schemas.food_log import FoodLogCreate, FoodLogResponse, WaterIntakeResponse

logger = logging.getLogger(__name__)


async def _get_ai_comment(food_item: str) -> str | None:
    if not settings.OPENAI_API_KEY:
        return None
    try:
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        prompt = (
            f"In 1-2 sentences, give a brief nutritional note about: {food_item}. "
            "Be positive and informative. No disclaimers."
        )
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=128,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        logger.warning("AI comment failed for '%s': %s", food_item, exc)
        return None


async def add_log(
    db: AsyncSession, user_id: UUID, data: FoodLogCreate
) -> FoodLogResponse:
    ai_comment = await _get_ai_comment(data.food_item)
    entry = await repo.create(db, user_id, data, ai_comment)
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
        # Already 0, return as-is without a DB write
        return WaterIntakeResponse(date=date, glasses=0)
    updated = await repo.upsert_water(db, user_id, date, new_val)
    return WaterIntakeResponse.model_validate(updated)
