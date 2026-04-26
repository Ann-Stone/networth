from fastapi import APIRouter

from app.routers.reports.assets import router as assets_router
from app.routers.reports.balance import router as balance_router
from app.routers.reports.expenditure import router as expenditure_router

router = APIRouter(prefix="/reports", tags=["reports"])
router.include_router(balance_router)
router.include_router(expenditure_router)
router.include_router(assets_router)
