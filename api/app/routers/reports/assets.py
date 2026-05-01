"""Asset composition endpoint (BE-025)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.models.reports.asset_breakdown import AssetBreakdownRead
from app.schemas.response import (
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    ApiResponse,
    error_response,
    not_found_error,
)
from app.services.report_service import get_asset_breakdown

router = APIRouter()


@router.get(
    "/assets",
    summary="Get asset composition",
    description=(
        "Returns share (% + absolute) of each asset type, FX-converted to base currency."
    ),
    response_model=ApiResponse[AssetBreakdownRead],
    responses={422: VALIDATION_ERROR, 500: INTERNAL_ERROR},
)
def get_assets(session: Session = Depends(get_session)) -> ApiResponse[AssetBreakdownRead]:
    return ApiResponse(data=get_asset_breakdown(session))
