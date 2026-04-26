from fastapi import APIRouter

from app.routers.dashboard.budget import router as budget_router
from app.routers.dashboard.summary import router as summary_router

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
router.include_router(summary_router)
router.include_router(budget_router)
