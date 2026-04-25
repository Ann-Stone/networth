"""Journal CRUD + analytics endpoints (Monthly Report domain)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.models.monthly_report.analytics import (
    ExpenditureBudgetResponse,
    ExpenditureRatioResponse,
    InvestRatioResponse,
    LiabilityResponse,
)
from app.models.monthly_report.journal import (
    Journal,
    JournalCreate,
    JournalMonthRead,
    JournalRead,
    JournalUpdate,
)
from app.schemas.response import ApiResponse
from app.services.monthly_report_service import (
    compute_expenditure_budget,
    compute_expenditure_ratio,
    compute_gain_loss,
    compute_invest_ratio,
    compute_liability,
    create_journal,
    delete_journal,
    list_journals_by_month,
    update_journal,
)

router = APIRouter()


@router.get(
    "/{vesting_month}",
    summary="List journals for a month with gain/loss",
    description=(
        "Return all Journal entries whose vesting_month matches the path parameter, "
        "ordered by spend_date. The response also includes the FX-converted gain/loss "
        "total for the month."
    ),
    response_model=ApiResponse[JournalMonthRead],
    responses={200: {"description": "Journal list and gain/loss for the month"}},
)
def get_journals_by_month(
    vesting_month: str, session: Session = Depends(get_session)
) -> ApiResponse[JournalMonthRead]:
    journals = list_journals_by_month(session, vesting_month)
    gain_loss = compute_gain_loss(session, journals)
    payload = JournalMonthRead(
        items=[JournalRead.model_validate(j, from_attributes=True) for j in journals],
        gain_loss=gain_loss,
    )
    return ApiResponse(data=payload)


@router.post(
    "",
    summary="Create a journal entry",
    description="Persist a new Journal row. distinct_number is auto-assigned.",
    response_model=ApiResponse[JournalRead],
    status_code=201,
    responses={
        201: {"description": "Journal created"},
        422: {"description": "Validation error"},
    },
)
def post_journal(
    payload: JournalCreate, session: Session = Depends(get_session)
) -> ApiResponse[JournalRead]:
    row = create_journal(session, payload)
    return ApiResponse(data=JournalRead.model_validate(row, from_attributes=True))


@router.put(
    "/{journal_id}",
    summary="Update a journal entry",
    description="Partial update of a Journal identified by distinct_number.",
    response_model=ApiResponse[JournalRead],
    responses={
        200: {"description": "Journal updated"},
        404: {"description": "Journal not found"},
        422: {"description": "Validation error"},
    },
)
def put_journal(
    journal_id: int,
    payload: JournalUpdate,
    session: Session = Depends(get_session),
) -> ApiResponse[JournalRead]:
    row = update_journal(session, journal_id, payload)
    return ApiResponse(data=JournalRead.model_validate(row, from_attributes=True))


@router.delete(
    "/{journal_id}",
    summary="Delete a journal entry",
    description="Delete a Journal identified by distinct_number.",
    response_model=ApiResponse[dict],
    responses={
        200: {"description": "Journal deleted"},
        404: {"description": "Journal not found"},
    },
)
def delete_journal_endpoint(
    journal_id: int, session: Session = Depends(get_session)
) -> ApiResponse[dict]:
    delete_journal(session, journal_id)
    return ApiResponse(data={"deleted": journal_id})


# ---------- Analytics (BE-017) ----------


@router.get(
    "/{vesting_month}/expenditure-ratio",
    summary="Monthly expenditure ratio (inner/outer pie)",
    description=(
        "Return outer/inner aggregations of journal spending for the given month. "
        "Outer = grouped by action_main_type; inner = grouped by action_sub_type. "
        "Excludes 'invest' and 'transfer' main types."
    ),
    response_model=ApiResponse[ExpenditureRatioResponse],
    responses={
        200: {"description": "Expenditure ratio aggregation"},
        404: {"description": "No data for the month"},
    },
)
def get_expenditure_ratio(
    vesting_month: str, session: Session = Depends(get_session)
) -> ApiResponse[ExpenditureRatioResponse]:
    return ApiResponse(data=compute_expenditure_ratio(session, vesting_month))


@router.get(
    "/{vesting_month}/invest-ratio",
    summary="Monthly invest ratio",
    description="Aggregate journal spending whose action_main_type == 'invest', grouped by action_sub_type.",
    response_model=ApiResponse[InvestRatioResponse],
    responses={
        200: {"description": "Invest ratio aggregation"},
        404: {"description": "No data for the month"},
    },
)
def get_invest_ratio(
    vesting_month: str, session: Session = Depends(get_session)
) -> ApiResponse[InvestRatioResponse]:
    return ApiResponse(data=compute_invest_ratio(session, vesting_month))


@router.get(
    "/{vesting_month}/expenditure-budget",
    summary="Actual vs budget per category",
    description=(
        "Compare expected (Budget.expected<MM>) vs actual (Journal.spending sum) per "
        "category, returning diff and usage_rate."
    ),
    response_model=ApiResponse[ExpenditureBudgetResponse],
    responses={
        200: {"description": "Budget comparison rows"},
        404: {"description": "No data for the month"},
    },
)
def get_expenditure_budget(
    vesting_month: str, session: Session = Depends(get_session)
) -> ApiResponse[ExpenditureBudgetResponse]:
    return ApiResponse(data=compute_expenditure_budget(session, vesting_month))


@router.get(
    "/{vesting_month}/liability",
    summary="Credit-card liability breakdown",
    description="Aggregate journal spending whose spend_way_type == 'credit_card', grouped by credit card.",
    response_model=ApiResponse[LiabilityResponse],
    responses={
        200: {"description": "Liability breakdown"},
        404: {"description": "No data for the month"},
    },
)
def get_liability(
    vesting_month: str, session: Session = Depends(get_session)
) -> ApiResponse[LiabilityResponse]:
    return ApiResponse(data=compute_liability(session, vesting_month))


__all__ = ["router"]
