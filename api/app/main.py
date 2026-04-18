from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import create_db_and_tables
from app.routers.assets import router as assets_router
from app.routers.dashboard import router as dashboard_router
from app.routers.monthly_report import router as monthly_report_router
from app.routers.reports import router as reports_router
from app.routers.settings import router as settings_router
from app.routers.utilities import router as utilities_router
from app.schemas.response import ApiError


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    create_db_and_tables()
    yield


app = FastAPI(title="Networth API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def on_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiError(error=exc.detail).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def on_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=ApiError(error=exc.errors()).model_dump(),
    )


@app.exception_handler(ValueError)
async def on_value_error(request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content=ApiError(error=str(exc)).model_dump(),
    )


@app.exception_handler(Exception)
async def on_exception(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=ApiError(error=str(exc)).model_dump(),
    )


app.include_router(settings_router)
app.include_router(monthly_report_router)
app.include_router(assets_router)
app.include_router(reports_router)
app.include_router(dashboard_router)
app.include_router(utilities_router)
