from fastapi import APIRouter

from app.routers.monthly_report.journals import router as journals_router

router = APIRouter(prefix="/monthly-report", tags=["monthly_report"])
router.include_router(journals_router, prefix="/journals", tags=["monthly-report"])
