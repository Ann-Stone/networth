"""Stock price management endpoints (Monthly Report domain, BE-018)."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlmodel import Session

from app.database import get_session
from app.models.monthly_report.stock_price import (
    StockPriceCreate,
    StockPriceMonthRead,
    StockPriceRead,
)
from app.schemas.response import ApiResponse
from app.services.stock_service import insert_stock_price, list_month_stock_prices

router = APIRouter()


_VESTING_MONTH = Annotated[
    str,
    Path(
        ...,
        pattern=r"^\d{6}$",
        description="YYYYMM",
        examples=["202604"],
    ),
]


@router.get(
    "/{vesting_month}",
    summary="Month-level closing prices for held stocks",
    description=(
        "For every stock present in the holdings table, return the most recent "
        "StockPriceHistory close on or before month-end (falling back to the "
        "latest prior row when the month has none)."
    ),
    response_model=ApiResponse[list[StockPriceMonthRead]],
    responses={
        200: {"description": "Per-stock month close-price list"},
        422: {"description": "Invalid vesting_month format"},
    },
)
def get_stock_prices_by_month(
    vesting_month: _VESTING_MONTH,
    session: Session = Depends(get_session),
) -> ApiResponse[list[StockPriceMonthRead]]:
    return ApiResponse(data=list_month_stock_prices(session, vesting_month))


@router.post(
    "",
    summary="Insert a stock price record (optionally fetch yfinance)",
    description=(
        "Persist a new StockPriceHistory row. When trigger_yfinance is True the "
        "close price is overwritten by yfinance."
    ),
    response_model=ApiResponse[StockPriceRead],
    status_code=201,
    responses={
        201: {"description": "Stock price record created"},
        422: {"description": "Validation error"},
        502: {"description": "yfinance fetch failed"},
    },
)
def post_stock_price(
    payload: StockPriceCreate, session: Session = Depends(get_session)
) -> ApiResponse[StockPriceRead]:
    row = insert_stock_price(session, payload)
    return ApiResponse(data=StockPriceRead.model_validate(row, from_attributes=True))


__all__ = ["router"]
