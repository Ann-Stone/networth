"""Budget management endpoints (Settings domain)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.models.settings.budget import BudgetRead, BudgetUpdate
from app.schemas.response import ApiResponse
from app.services.setting_service import (
    bulk_update_budgets,
    copy_budget_from_previous,
    list_budget_year_range,
    list_budgets_by_year,
)

router = APIRouter(prefix="/budgets", tags=["settings:budgets"])


@router.get(
    "/year-range",
    summary="Available budget years",
    description="Return distinct budget_year values present in Budget, ascending.",
    response_model=ApiResponse[list[int]],
    responses={},
)
def list_budget_year_range_endpoint(
    session: Session = Depends(get_session),
) -> ApiResponse[list[int]]:
    return ApiResponse(data=list_budget_year_range(session))


@router.get(
    "/{year}",
    summary="Budgets for a year",
    description="Return all Budget rows for the given year ordered by category_code.",
    response_model=ApiResponse[list[BudgetRead]],
    responses={422: {"description": "Invalid year"}},
)
def list_budgets_by_year_endpoint(
    year: int,
    session: Session = Depends(get_session),
) -> ApiResponse[list[BudgetRead]]:
    rows = list_budgets_by_year(session, year)
    return ApiResponse(data=[BudgetRead.model_validate(r, from_attributes=True) for r in rows])


@router.put(
    "",
    summary="Bulk update budgets",
    description=(
        "Update multiple Budget rows in one call. Each item is matched by "
        "(budget_year, category_code). Transactional — if any row is missing, "
        "all updates are rolled back."
    ),
    response_model=ApiResponse[list[BudgetRead]],
    responses={
        404: {"description": "One or more budget rows not found"},
        422: {"description": "Validation error"},
    },
)
def bulk_update_budgets_endpoint(
    payload: list[BudgetUpdate],
    session: Session = Depends(get_session),
) -> ApiResponse[list[BudgetRead]]:
    rows = bulk_update_budgets(session, payload)
    return ApiResponse(data=[BudgetRead.model_validate(r, from_attributes=True) for r in rows])


@router.post(
    "/{year}/copy-from-previous",
    summary="Copy budget from previous year journal",
    description=(
        "Compute budget for {year} by averaging the previous year's Journal "
        "amounts per action_main_type across 12 months, then upsert into Budget."
    ),
    response_model=ApiResponse[list[BudgetRead]],
    responses={422: {"description": "Invalid year"}},
)
def copy_budget_from_previous_endpoint(
    year: int,
    session: Session = Depends(get_session),
) -> ApiResponse[list[BudgetRead]]:
    rows = copy_budget_from_previous(session, year)
    return ApiResponse(data=[BudgetRead.model_validate(r, from_attributes=True) for r in rows])
