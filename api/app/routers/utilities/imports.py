"""Data import endpoints: stock prices, FX rates, invoice CSV."""
from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks

from app.models.utilities.imports import ImportAcceptedResponse, ImportRequest
from app.schemas.response import ApiResponse
from app.services.import_service import (
    import_fx_rates,
    import_invoices,
    import_stock_prices,
)

router = APIRouter(prefix="/import", tags=["utilities:imports"])

_ACCEPTED_RESPONSES = {
    202: {"description": "Import scheduled as a background task."},
    422: {"description": "Validation error (e.g. malformed period)."},
}


@router.post(
    "/stock-prices",
    summary="Fetch stock prices via yfinance",
    description=(
        "Kicks off a background task that pulls daily OHLC for every distinct "
        "ticker in StockJournal and upserts into Stock_Price_History."
    ),
    response_model=ApiResponse[ImportAcceptedResponse],
    responses=_ACCEPTED_RESPONSES,
    status_code=202,
)
def trigger_stock_import(
    body: ImportRequest, tasks: BackgroundTasks
) -> ApiResponse[ImportAcceptedResponse]:
    tasks.add_task(import_stock_prices, body.period)
    return ApiResponse(data=ImportAcceptedResponse(message="stock import started"))


@router.post(
    "/fx-rates",
    summary="Fetch FX buy rates from Sinopac",
    description=(
        "Kicks off a background task that pulls today's (or last-day-of-period) "
        "FX rates from Sinopac and upserts into FX_Rate."
    ),
    response_model=ApiResponse[ImportAcceptedResponse],
    responses=_ACCEPTED_RESPONSES,
    status_code=202,
)
def trigger_fx_import(
    body: ImportRequest, tasks: BackgroundTasks
) -> ApiResponse[ImportAcceptedResponse]:
    tasks.add_task(import_fx_rates, body.period)
    return ApiResponse(data=ImportAcceptedResponse(message="fx import started"))


@router.post(
    "/invoices",
    summary="Import government invoice CSV",
    description=(
        "Kicks off a background task that parses the configured pipe-delimited "
        "invoice CSV and inserts deduplicated journal rows."
    ),
    response_model=ApiResponse[ImportAcceptedResponse],
    responses=_ACCEPTED_RESPONSES,
    status_code=202,
)
def trigger_invoice_import(
    body: ImportRequest, tasks: BackgroundTasks
) -> ApiResponse[ImportAcceptedResponse]:
    tasks.add_task(import_invoices, body.period)
    return ApiResponse(data=ImportAcceptedResponse(message="invoice import started"))
