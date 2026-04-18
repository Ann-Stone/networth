from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import create_db_and_tables
from app.routers.assets import router as assets_router
from app.routers.dashboard import router as dashboard_router
from app.routers.monthly_report import router as monthly_report_router
from app.routers.reports import router as reports_router
from app.routers.settings import router as settings_router
from app.routers.utilities import router as utilities_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    create_db_and_tables()
    yield


app = FastAPI(title="Networth API", lifespan=lifespan)

app.include_router(settings_router)
app.include_router(monthly_report_router)
app.include_router(assets_router)
app.include_router(reports_router)
app.include_router(dashboard_router)
app.include_router(utilities_router)
