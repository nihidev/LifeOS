import datetime
import json
import logging
from uuid import UUID

from fastapi import HTTPException
from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.small_win import SmallWin
from app.repositories import resolution_repository as repo
from app.schemas.resolution import (
    AIAnalysisItem,
    AIAnalysisResponse,
    CheckInCreate,
    CheckInResponse,
    ResolutionCreate,
    ResolutionResponse,
    ResolutionUpdate,
)

logger = logging.getLogger(__name__)


async def create_resolution(
    db: AsyncSession, user_id: UUID, data: ResolutionCreate
) -> ResolutionResponse:
    resolution = await repo.create(db, user_id, data)
    return ResolutionResponse.model_validate(resolution)


async def list_resolutions(
    db: AsyncSession, user_id: UUID, status: str | None = None
) -> list[ResolutionResponse]:
    resolutions = await repo.get_all(db, user_id, status)
    return [ResolutionResponse.model_validate(r) for r in resolutions]


async def update_resolution(
    db: AsyncSession, user_id: UUID, id: UUID, data: ResolutionUpdate
) -> ResolutionResponse:
    # Auto-set progress_percent=100 when status is completed
    if data.status == "completed":
        data = data.model_copy(update={"progress_percent": 100})

    resolution = await repo.update(db, user_id, id, data)
    if resolution is None:
        raise HTTPException(status_code=404, detail="Resolution not found")
    return ResolutionResponse.model_validate(resolution)


async def delete_resolution(db: AsyncSession, user_id: UUID, id: UUID) -> None:
    deleted = await repo.delete(db, user_id, id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Resolution not found")


async def log_check_in(
    db: AsyncSession, user_id: UUID, resolution_id: UUID, data: CheckInCreate
) -> CheckInResponse:
    # Verify resolution exists and belongs to user
    resolution = await repo.get_by_id(db, user_id, resolution_id)
    if resolution is None:
        raise HTTPException(status_code=404, detail="Resolution not found")

    check_in = await repo.upsert_check_in(db, user_id, resolution_id, data)

    # Auto-advance not_started → in_progress on first check-in
    if resolution.status == "not_started":
        update_data = ResolutionUpdate(status="in_progress")
        await repo.update(db, user_id, resolution_id, update_data)

    return CheckInResponse.model_validate(check_in)


async def get_analysis(db: AsyncSession, user_id: UUID) -> AIAnalysisResponse:
    today = datetime.date.today()

    # 1. Check cache for today
    cached = await repo.get_ai_cache(db, user_id, today)
    if cached is not None:
        return AIAnalysisResponse.model_validate(cached.analysis)

    # 2. Fetch resolutions
    resolutions = await repo.get_all(db, user_id)

    # 3. Build no_signal fallback for all resolutions
    def _no_signal_response() -> AIAnalysisResponse:
        analyses = [
            AIAnalysisItem(
                resolution_id=str(r.id),
                resolution_title=r.title,
                signal="no_signal",
                evidence=[],
                suggestion="No analysis available — add your OpenAI API key to enable AI insights.",
            )
            for r in resolutions
        ]
        return AIAnalysisResponse(
            generated_at=today.isoformat(),
            analyses=analyses,
        )

    if not resolutions:
        return AIAnalysisResponse(generated_at=today.isoformat(), analyses=[])

    # 4. If no API key, return no_signal
    if not settings.OPENAI_API_KEY:
        return _no_signal_response()

    # 5. Fetch small wins from last 30 days
    thirty_days_ago = today - datetime.timedelta(days=30)
    result = await db.execute(
        select(SmallWin)
        .where(
            SmallWin.user_id == user_id,
            SmallWin.date >= thirty_days_ago,
            SmallWin.date <= today,
            SmallWin.entry_type == "win",
        )
        .order_by(SmallWin.date.desc())
    )
    wins = list(result.scalars().all())

    # 6. Call OpenAI API
    try:
        resolutions_text = "\n".join(
            f"- id={r.id} title='{r.title}' status={r.status} progress={r.progress_percent}%"
            for r in resolutions
        )
        wins_text = (
            "\n".join(f"- {w.date}: {w.text}" for w in wins)
            if wins
            else "(none)"
        )

        prompt = (
            f"Resolutions:\n{resolutions_text}\n\n"
            f"Small wins (last 30 days):\n{wins_text}\n\n"
            "For each resolution output a JSON array:\n"
            '[{"resolution_id":"...","resolution_title":"...","signal":"on_track|at_risk|no_signal",'
            '"evidence":["..."],"suggestion":"..."}]\n\n'
            "signal rules:\n"
            "- on_track: ≥1 win clearly relates to this goal\n"
            "- at_risk: resolution has been started (in_progress) but zero related wins\n"
            "- no_signal: not_started OR fewer than 3 total wins logged"
        )

        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=1024,
            messages=[
                {
                    "role": "system",
                    "content": "You are a personal progress analyst. Respond with valid JSON only — no prose.",
                },
                {"role": "user", "content": prompt},
            ],
        )

        raw = response.choices[0].message.content.strip()
        analyses_data = json.loads(raw)

        analyses = [AIAnalysisItem(**item) for item in analyses_data]
        response = AIAnalysisResponse(
            generated_at=today.isoformat(),
            analyses=analyses,
        )

        # 7. Save to cache
        await repo.save_ai_cache(db, user_id, today, response.model_dump())
        return response

    except Exception as exc:
        logger.warning("AI analysis failed: %s", exc)
        return _no_signal_response()
