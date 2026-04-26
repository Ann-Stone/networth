"""Global health-check endpoint."""
from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from fastapi import APIRouter

from app.models.utilities.health import HealthPayload
from app.schemas.response import ApiResponse


def _resolve_version() -> str:
    try:
        return version("networth-api")
    except PackageNotFoundError:
        return "0.0.0"


APP_VERSION: str = _resolve_version()

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    summary="Server health check",
    description=(
        "Returns alive=true and the running app version. "
        "Does not depend on the database."
    ),
    response_model=ApiResponse[HealthPayload],
    responses={200: {"description": "Service is alive"}},
)
def health() -> ApiResponse[HealthPayload]:
    return ApiResponse(data=HealthPayload(alive=True, version=APP_VERSION))
