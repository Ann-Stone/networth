from fastapi import APIRouter

from app.routers.monthly_report.journals import router as journals_router
from app.routers.monthly_report.stock_prices import router as stock_prices_router

router = APIRouter(prefix="/monthly-report", tags=["monthly_report"])
router.include_router(journals_router, prefix="/journals", tags=["monthly-report"])
router.include_router(stock_prices_router, prefix="/stock-prices", tags=["monthly-report"])
