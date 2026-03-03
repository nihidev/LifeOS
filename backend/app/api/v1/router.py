from fastapi import APIRouter

router = APIRouter()

# Feature routers — uncomment as each phase is implemented:

from .small_wins import router as small_wins_router
router.include_router(small_wins_router, prefix="/small-wins", tags=["Small Wins"])

from .workouts import router as workouts_router
router.include_router(workouts_router, prefix="/workouts", tags=["Workouts"])

from .self_assessment import router as self_assessment_router
router.include_router(self_assessment_router, prefix="/self-assessment", tags=["Self Assessment"])

from .expenses import router as expenses_router
router.include_router(expenses_router, prefix="/expenses", tags=["Expenses"])

from .resolutions import router as resolutions_router
router.include_router(resolutions_router, prefix="/resolutions", tags=["Resolutions"])

from .dashboard import router as dashboard_router
router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])

from .admin import router as admin_router
router.include_router(admin_router, prefix="/admin", tags=["Admin"])

from .food_logs import router as food_logs_router
router.include_router(food_logs_router, prefix="/food-logs", tags=["Food Logs"])

from .grocery import router as grocery_router
router.include_router(grocery_router, prefix="/grocery", tags=["Grocery"])
