"""Dev-only admin endpoints. Not exposed in production."""
from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.services.scheduler_service import check_and_remind

router = APIRouter()


def _guard_dev() -> None:
    if settings.ENVIRONMENT != "development":
        raise HTTPException(status_code=404, detail="Not found")


@router.post("/trigger-reminder", status_code=200)
async def trigger_reminder() -> dict[str, str]:
    """Manually trigger the small-wins reminder check. Dev only."""
    _guard_dev()
    result = await check_and_remind(AsyncSessionLocal)
    return {"result": result}
