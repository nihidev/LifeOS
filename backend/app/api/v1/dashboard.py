from fastapi import APIRouter

from app.core.deps import CurrentUser, DB
from app.schemas.dashboard import DashboardResponse
from app.services import dashboard_service

router = APIRouter()


@router.get("/", response_model=DashboardResponse)
async def get_dashboard(
    db: DB,
    user_id: CurrentUser,
) -> DashboardResponse:
    return await dashboard_service.get_dashboard(db, user_id)
