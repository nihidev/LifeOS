import calendar
import datetime
import json
import logging
import re
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
    AIPlanMonth,
    CheckInCreate,
    CheckInResponse,
    ProgressLogCreate,
    ProgressLogResponse,
    ResolutionCreate,
    ResolutionResponse,
    ResolutionUpdate,
)

logger = logging.getLogger(__name__)

_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


def _strip_fences(text: str) -> str:
    return _FENCE_RE.sub("", text).strip()


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


async def log_progress(
    db: AsyncSession, user_id: UUID, resolution_id: UUID, data: ProgressLogCreate
) -> ProgressLogResponse:
    resolution = await repo.get_by_id(db, user_id, resolution_id)
    if resolution is None:
        raise HTTPException(status_code=404, detail="Resolution not found")

    log = await repo.create_progress_log(db, user_id, resolution_id, data)
    await repo.update(db, user_id, resolution_id, ResolutionUpdate(progress_percent=data.progress_percent))
    return ProgressLogResponse.model_validate(log)


async def generate_plan(
    db: AsyncSession, user_id: UUID, resolution_id: UUID
) -> ResolutionResponse:
    resolution = await repo.get_by_id(db, user_id, resolution_id)
    if resolution is None:
        raise HTTPException(status_code=404, detail="Resolution not found")
    if resolution.target_date is None:
        raise HTTPException(status_code=400, detail="A target date is required to generate a plan")
    if not settings.OPENAI_API_KEY:
        raise HTTPException(status_code=400, detail="OpenAI API key not configured")

    today = datetime.date.today()
    # Build month labels from today's month to target month
    start = today.replace(day=1)
    end = resolution.target_date.replace(day=1)
    months = []
    cur = start
    while cur <= end and len(months) < 12:
        months.append(cur.strftime("%B %Y"))
        # advance one month
        if cur.month == 12:
            cur = cur.replace(year=cur.year + 1, month=1)
        else:
            cur = cur.replace(month=cur.month + 1)

    start_month_label = months[0] if months else today.strftime("%B %Y")
    end_month_label = months[-1] if months else resolution.target_date.strftime("%B %Y")

    prompt = (
        f"You are a personal goal coach. The user has set this resolution:\n"
        f"Title: {resolution.title}\n"
        f"Description: {resolution.description or 'none'}\n"
        f"Start: {today.isoformat()}\n"
        f"Target date: {resolution.target_date.isoformat()}\n\n"
        f"Create a month-by-month action plan from {start_month_label} to {end_month_label}.\n"
        "For each month: a clear monthly goal (1 sentence) + 2-3 concrete actions.\n\n"
        'Respond with a JSON array only — no prose:\n'
        '[{"month_label": "January 2026", "goal": "...", "actions": ["...", "...", "..."]}, ...]\n\n'
        "Rules: be specific and realistic; each month builds on the previous; "
        "final month achieves the resolution; max 12 months."
    )

    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=2048,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a personal goal coach. Respond with valid JSON only — no prose. "
                    'Wrap the array in an object: {"plan": [...]}'
                ),
            },
            {"role": "user", "content": prompt},
        ],
    )

    try:
        raw = _strip_fences(response.choices[0].message.content or "")
        parsed = json.loads(raw)
        plan_data = parsed.get("plan", parsed) if isinstance(parsed, dict) else parsed
        plan = [AIPlanMonth(**item) for item in plan_data]
    except Exception as exc:
        logger.error("Failed to parse plan from OpenAI response: %s", exc)
        raise HTTPException(status_code=502, detail="Failed to parse AI response — please try again")

    updated = await repo.update(
        db, user_id, resolution_id, ResolutionUpdate(ai_plan=[m.model_dump() for m in plan])
    )
    return ResolutionResponse.model_validate(updated)


async def calculate_progress(
    db: AsyncSession, user_id: UUID, resolution_id: UUID
) -> ResolutionResponse:
    resolution = await repo.get_by_id(db, user_id, resolution_id)
    if resolution is None:
        raise HTTPException(status_code=404, detail="Resolution not found")
    if not resolution.ai_plan:
        raise HTTPException(status_code=400, detail="Generate a plan first before calculating progress")

    # Check-ins with notes
    noted_check_ins = [ci for ci in resolution.check_ins if ci.note]
    if not noted_check_ins:
        updated = await repo.update(
            db, user_id, resolution_id, ResolutionUpdate(progress_percent=0)
        )
        return ResolutionResponse.model_validate(updated)

    if not settings.OPENAI_API_KEY:
        raise HTTPException(status_code=400, detail="OpenAI API key not configured")

    plan_text = "\n".join(
        f"• {m['month_label']}: {m['goal']}" for m in resolution.ai_plan
    )
    checkins_text = "\n".join(
        f"• {calendar.month_name[ci.month]} {ci.year} (rating {ci.rating}/5): {ci.note}"
        for ci in sorted(noted_check_ins, key=lambda c: (c.year, c.month))
    )

    prompt = (
        f"You are a personal progress analyst.\n"
        f"Resolution: {resolution.title}\n"
        f"Target date: {resolution.target_date}\n\n"
        f"Monthly plan:\n{plan_text}\n\n"
        f"User check-ins (what they actually did):\n{checkins_text}\n\n"
        "Calculate how much of the plan has been completed (0-100).\n"
        'Respond with JSON only: {"percentage": 75, "reasoning": "..."}\n\n'
        "Rules: base % on reported progress vs planned milestones; no check-ins = 0%; "
        "give credit for partial progress; reasoning max 1 sentence."
    )

    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=256,
        messages=[
            {
                "role": "system",
                "content": "You are a personal progress analyst. Respond with valid JSON only.",
            },
            {"role": "user", "content": prompt},
        ],
    )

    try:
        raw = _strip_fences(response.choices[0].message.content or "")
        result = json.loads(raw)
        percentage = max(0, min(100, int(result["percentage"])))
    except Exception as exc:
        logger.error("Failed to parse progress from OpenAI response: %s", exc)
        raise HTTPException(status_code=502, detail="Failed to parse AI response — please try again")

    updated = await repo.update(
        db, user_id, resolution_id, ResolutionUpdate(progress_percent=percentage)
    )
    return ResolutionResponse.model_validate(updated)


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

    # Auto-recalculate progress if plan exists
    if resolution.ai_plan:
        try:
            await calculate_progress(db, user_id, resolution_id)
        except Exception as exc:
            logger.warning("Auto progress calculation failed: %s", exc)

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
