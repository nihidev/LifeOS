from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.dashboard import DashboardResponse
from app.services import dashboard_service

router = APIRouter()


@router.get("/", response_model=DashboardResponse)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user),
) -> DashboardResponse:
    return await dashboard_service.get_dashboard(db, user_id)
