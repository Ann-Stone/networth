"""Utility selection endpoints (dropdown helpers)."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlmodel import Session

from app.database import get_session
from app.models.utilities.selection import SelectionGroup
from app.schemas.response import ApiResponse
from app.services.utility_service import (
    get_account_selection_groups,
    get_code_selection_groups,
    get_credit_card_selection_groups,
    get_insurance_selection_groups,
    get_loan_selection_groups,
    get_sub_code_selection_groups,
)

router = APIRouter(prefix="/selections", tags=["utilities:selections"])

_COMMON_RESPONSES = {
    200: {"description": "Grouped options for a frontend dropdown."},
    500: {"description": "Unexpected server error"},
}


@router.get(
    "/accounts",
    summary="List accounts grouped by type",
    description="Return active accounts grouped by account_type, ordered by account_index ASC.",
    response_model=ApiResponse[list[SelectionGroup]],
    responses=_COMMON_RESPONSES,
)
def list_account_selections(
    session: Session = Depends(get_session),
) -> ApiResponse[list[SelectionGroup]]:
    return ApiResponse(data=get_account_selection_groups(session))


@router.get(
    "/credit-cards",
    summary="List credit cards as a single group",
    description="Return active credit cards in one group labelled 'Credit_Card'.",
    response_model=ApiResponse[list[SelectionGroup]],
    responses=_COMMON_RESPONSES,
)
def list_credit_card_selections(
    session: Session = Depends(get_session),
) -> ApiResponse[list[SelectionGroup]]:
    return ApiResponse(data=get_credit_card_selection_groups(session))


@router.get(
    "/loans",
    summary="List loans as a single group",
    description="Return loans in one group labelled 'Loan'.",
    response_model=ApiResponse[list[SelectionGroup]],
    responses=_COMMON_RESPONSES,
)
def list_loan_selections(
    session: Session = Depends(get_session),
) -> ApiResponse[list[SelectionGroup]]:
    return ApiResponse(data=get_loan_selection_groups(session))


@router.get(
    "/insurances",
    summary="List insurance policies as a single group",
    description="Return open insurance policies (has_closed != 'Y') in one group labelled 'Insurance'.",
    response_model=ApiResponse[list[SelectionGroup]],
    responses=_COMMON_RESPONSES,
)
def list_insurance_selections(
    session: Session = Depends(get_session),
) -> ApiResponse[list[SelectionGroup]]:
    return ApiResponse(data=get_insurance_selection_groups(session))


@router.get(
    "/codes",
    summary="List top-level codes grouped by code_type",
    description="Return codes whose parent_id is NULL, grouped by code_type and ordered by code_index ASC.",
    response_model=ApiResponse[list[SelectionGroup]],
    responses=_COMMON_RESPONSES,
)
def list_code_selections(
    session: Session = Depends(get_session),
) -> ApiResponse[list[SelectionGroup]]:
    return ApiResponse(data=get_code_selection_groups(session))


@router.get(
    "/codes/{code_group}",
    summary="List sub-codes for a parent code",
    description="Return children of the parent code identified by code_group as a single 'sub' group.",
    response_model=ApiResponse[list[SelectionGroup]],
    responses={**_COMMON_RESPONSES, 404: {"description": "Parent code has no children"}},
)
def list_sub_code_selections(
    code_group: Annotated[
        str,
        Path(..., description="Parent code_id", examples=["92"]),
    ],
    session: Session = Depends(get_session),
) -> ApiResponse[list[SelectionGroup]]:
    return ApiResponse(data=get_sub_code_selection_groups(session, code_group))
