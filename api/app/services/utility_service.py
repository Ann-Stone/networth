"""Utility domain service functions — dropdown selection groups."""
from __future__ import annotations


from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.assets.insurance import Insurance
from app.models.assets.loan import Loan
from app.models.settings.account import Account
from app.models.settings.code_data import CodeData
from app.models.settings.credit_card import CreditCard
from app.models.utilities.selection import SelectionGroup, SelectionOption


def get_account_selection_groups(session: Session) -> list[SelectionGroup]:
    """Active accounts consolidated into one group per account_type.

    Rows are queried ordered by account_index so options inside each group
    follow that order; group order is the first-seen account_type.
    """
    rows = session.exec(
        select(Account)
        .where(Account.in_use == "Y")
        .order_by(Account.account_index.asc(), Account.id.asc())
    ).all()
    grouped: dict[str, list[Account]] = {}
    for a in rows:
        grouped.setdefault(a.account_type, []).append(a)
    return [
        SelectionGroup(
            label=key,
            options=[SelectionOption(value=str(a.id), label=a.name) for a in items],
        )
        for key, items in grouped.items()
    ]


def get_credit_card_selection_groups(session: Session) -> list[SelectionGroup]:
    """Active credit cards as a single group labelled 'Credit_Card'."""
    rows = session.exec(
        select(CreditCard)
        .where(CreditCard.in_use == "Y")
        .order_by(CreditCard.credit_card_index.asc(), CreditCard.credit_card_id.asc())
    ).all()
    if not rows:
        return []
    return [
        SelectionGroup(
            label="Credit_Card",
            options=[
                SelectionOption(value=c.credit_card_id, label=c.card_name) for c in rows
            ],
        )
    ]


def get_loan_selection_groups(session: Session) -> list[SelectionGroup]:
    """Active loans as a single group labelled 'Loan'.

    Loan has no `in_use` column; legacy semantics treat all rows as active. The
    granular ticket text uses `in_use == "Y"` as a placeholder; we degrade to
    "all loans, ordered by loan_index" to match the actual model.
    """
    rows = session.exec(
        select(Loan).order_by(Loan.loan_index.asc(), Loan.loan_id.asc())
    ).all()
    if not rows:
        return []
    return [
        SelectionGroup(
            label="Loan",
            options=[SelectionOption(value=l.loan_id, label=l.loan_name) for l in rows],
        )
    ]


def get_insurance_selection_groups(session: Session) -> list[SelectionGroup]:
    """Open insurance policies as a single group labelled 'Insurance'.

    Insurance uses `has_closed` (Y/N) instead of `in_use`; active = not closed.
    """
    rows = session.exec(
        select(Insurance)
        .where(Insurance.has_closed != "Y")
        .order_by(Insurance.insurance_id.asc())
    ).all()
    if not rows:
        return []
    return [
        SelectionGroup(
            label="Insurance",
            options=[
                SelectionOption(value=i.insurance_id, label=i.insurance_name)
                for i in rows
            ],
        )
    ]


def get_code_selection_groups(session: Session) -> list[SelectionGroup]:
    """Top-level codes (parent_id IS NULL) consolidated into one group per code_type.

    Rows are queried ordered by code_index so options inside each group follow
    that order; group order is the first-seen code_type.
    """
    rows = session.exec(
        select(CodeData)
        .where(CodeData.in_use == "Y")
        .where(CodeData.parent_id.is_(None))
        .order_by(CodeData.code_index.asc(), CodeData.code_id.asc())
    ).all()
    grouped: dict[str, list[CodeData]] = {}
    for c in rows:
        grouped.setdefault(c.code_type, []).append(c)
    return [
        SelectionGroup(
            label=key,
            options=[SelectionOption(value=c.code_id, label=c.name) for c in items],
        )
        for key, items in grouped.items()
    ]


def get_sub_code_selection_groups(
    session: Session, parent_id: str
) -> list[SelectionGroup]:
    """Children of a parent code, returned as a single 'sub' group.

    Raises 404 when the parent has no children.
    """
    rows = session.exec(
        select(CodeData)
        .where(CodeData.parent_id == parent_id)
        .where(CodeData.in_use == "Y")
        .order_by(CodeData.code_index.asc(), CodeData.code_id.asc())
    ).all()
    if not rows:
        raise HTTPException(
            status_code=404,
            detail=f"No sub-codes for parent: {parent_id}",
        )
    return [
        SelectionGroup(
            label="sub",
            options=[SelectionOption(value=c.code_id, label=c.name) for c in rows],
        )
    ]
