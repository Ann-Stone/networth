"""Settings domain service functions (flat, session-as-parameter)."""
from __future__ import annotations

from datetime import date

from fastapi import HTTPException
from sqlalchemy import func
from sqlmodel import Session, select

from app.models.settings.account import Account, AccountCreate, AccountUpdate
from app.models.settings.budget import Budget, BudgetUpdate
from app.models.monthly_report.journal import Journal
from app.models.settings.code_data import (
    CodeData,
    CodeDataCreate,
    CodeDataUpdate,
    CodeWithSubs,
)


# ---------- Account ----------


def list_accounts(
    session: Session,
    name: str | None = None,
    account_type: str | None = None,
    in_use: str | None = None,
) -> list[Account]:
    """Return accounts with optional substring/equality filters."""
    statement = select(Account)
    if name:
        statement = statement.where(Account.name.contains(name))
    if account_type:
        statement = statement.where(Account.account_type == account_type)
    if in_use:
        statement = statement.where(Account.in_use == in_use)
    return list(session.exec(statement).all())


def list_accounts_selection(session: Session) -> list[Account]:
    """Return active accounts ordered for dropdown rendering."""
    statement = (
        select(Account)
        .where(Account.in_use == "Y")
        .order_by(Account.account_index.asc(), Account.id.asc())
    )
    return list(session.exec(statement).all())


def create_account(session: Session, data: AccountCreate) -> Account:
    """Insert a new Account; auto-fill ``account_index`` and reject duplicate ``account_id``."""
    existing = session.exec(
        select(Account).where(Account.account_id == data.account_id)
    ).first()
    if existing is not None:
        raise HTTPException(status_code=409, detail=f"Duplicate account_id: {data.account_id}")

    payload = data.model_dump()
    if payload.get("account_index") is None:
        max_idx = session.exec(select(func.max(Account.account_index))).first() or 0
        payload["account_index"] = (max_idx or 0) + 1

    account = Account(**payload)
    session.add(account)
    session.commit()
    session.refresh(account)
    return account


def update_account(session: Session, id: int, data: AccountUpdate) -> Account:
    account = session.get(Account, id)
    if account is None:
        raise HTTPException(status_code=404, detail=f"Account not found: {id}")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(account, field, value)
    session.add(account)
    session.commit()
    session.refresh(account)
    return account


def delete_account(session: Session, id: int) -> None:
    account = session.get(Account, id)
    if account is None:
        raise HTTPException(status_code=404, detail=f"Account not found: {id}")
    session.delete(account)
    session.commit()


# ---------- CodeData (main + sub) ----------


_BUDGET_TRIGGER_TYPES = {"Fixed", "Floating"}


def _get_main_code(session: Session, code_id: str) -> CodeData:
    row = session.get(CodeData, code_id)
    if row is None or row.parent_id is not None:
        raise HTTPException(status_code=404, detail=f"Main code not found: {code_id}")
    return row


def _get_sub_code(session: Session, code_id: str) -> CodeData:
    row = session.get(CodeData, code_id)
    if row is None or row.parent_id is None:
        raise HTTPException(status_code=404, detail=f"Sub-code not found: {code_id}")
    return row


def list_main_codes(session: Session) -> list[CodeData]:
    statement = (
        select(CodeData)
        .where(CodeData.parent_id.is_(None))
        .order_by(CodeData.code_index.asc(), CodeData.code_id.asc())
    )
    return list(session.exec(statement).all())


def list_codes_with_sub_codes(session: Session) -> list[CodeWithSubs]:
    mains = list_main_codes(session)
    sub_statement = (
        select(CodeData)
        .where(CodeData.parent_id.is_not(None))
        .order_by(CodeData.code_index.asc(), CodeData.code_id.asc())
    )
    subs = list(session.exec(sub_statement).all())
    by_parent: dict[str, list[CodeData]] = {}
    for s in subs:
        by_parent.setdefault(s.parent_id, []).append(s)
    return [
        CodeWithSubs(
            **m.model_dump(),
            sub_codes=[s.model_dump() for s in by_parent.get(m.code_id, [])],
        )
        for m in mains
    ]


def _autofill_code_index(session: Session, payload: dict) -> dict:
    if payload.get("code_index") is None:
        max_idx = session.exec(select(func.max(CodeData.code_index))).first() or 0
        payload["code_index"] = (max_idx or 0) + 1
    return payload


def create_main_code(session: Session, data: CodeDataCreate) -> CodeData:
    if session.get(CodeData, data.code_id) is not None:
        raise HTTPException(status_code=409, detail=f"Duplicate code_id: {data.code_id}")

    payload = _autofill_code_index(session, data.model_dump())
    payload["parent_id"] = None
    code = CodeData(**payload)
    session.add(code)

    if data.code_type in _BUDGET_TRIGGER_TYPES:
        year = str(date.today().year)
        budget = Budget(
            budget_year=year,
            category_code=data.code_id,
            category_name=data.name,
            code_type=data.code_type,
            **{f"expected{m:02d}": 0.0 for m in range(1, 13)},
        )
        session.add(budget)

    session.commit()
    session.refresh(code)
    return code


def update_main_code(session: Session, code_id: str, data: CodeDataUpdate) -> CodeData:
    code = _get_main_code(session, code_id)
    update_data = data.model_dump(exclude_unset=True)
    update_data.pop("parent_id", None)  # cannot turn a main into a sub via update
    for k, v in update_data.items():
        setattr(code, k, v)
    session.add(code)
    session.commit()
    session.refresh(code)
    return code


def delete_main_code(session: Session, code_id: str) -> None:
    code = _get_main_code(session, code_id)
    session.delete(code)
    session.commit()


def list_sub_codes(session: Session, parent_id: str) -> list[CodeData]:
    _get_main_code(session, parent_id)
    statement = (
        select(CodeData)
        .where(CodeData.parent_id == parent_id)
        .order_by(CodeData.code_index.asc(), CodeData.code_id.asc())
    )
    return list(session.exec(statement).all())


def create_sub_code(session: Session, data: CodeDataCreate) -> CodeData:
    if not data.parent_id:
        raise HTTPException(status_code=422, detail="parent_id is required for sub-codes")
    _get_main_code(session, data.parent_id)
    if session.get(CodeData, data.code_id) is not None:
        raise HTTPException(status_code=409, detail=f"Duplicate code_id: {data.code_id}")

    payload = _autofill_code_index(session, data.model_dump())
    code = CodeData(**payload)
    session.add(code)
    session.commit()
    session.refresh(code)
    return code


def update_sub_code(session: Session, code_id: str, data: CodeDataUpdate) -> CodeData:
    code = _get_sub_code(session, code_id)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(code, k, v)
    session.add(code)
    session.commit()
    session.refresh(code)
    return code


def delete_sub_code(session: Session, code_id: str) -> None:
    code = _get_sub_code(session, code_id)
    session.delete(code)
    session.commit()


# ---------- Budget ----------


def list_budgets_by_year(session: Session, year: int) -> list[Budget]:
    statement = (
        select(Budget)
        .where(Budget.budget_year == str(year))
        .order_by(Budget.category_code.asc())
    )
    return list(session.exec(statement).all())


def list_budget_year_range(session: Session) -> list[int]:
    rows = session.exec(
        select(Budget.budget_year).distinct().order_by(Budget.budget_year.asc())
    ).all()
    return [int(r) for r in rows]


def bulk_update_budgets(session: Session, items: list[BudgetUpdate]) -> list[Budget]:
    rows: list[Budget] = []
    for item in items:
        budget = session.get(Budget, (item.budget_year, item.category_code))
        if budget is None:
            session.rollback()
            raise HTTPException(
                status_code=404,
                detail=f"Budget not found: {item.budget_year}/{item.category_code}",
            )
        update_data = item.model_dump(
            exclude_unset=True, exclude={"budget_year", "category_code"}
        )
        for k, v in update_data.items():
            setattr(budget, k, v)
        session.add(budget)
        rows.append(budget)
    session.commit()
    for r in rows:
        session.refresh(r)
    return rows


def copy_budget_from_previous(session: Session, next_year: int) -> list[Budget]:
    prev_year = str(next_year - 1)
    next_year_str = str(next_year)

    journals = session.exec(
        select(Journal).where(Journal.spend_date.like(f"{prev_year}%"))
    ).all()
    if not journals:
        return []

    totals: dict[str, float] = {}
    for j in journals:
        totals[j.action_main_type] = totals.get(j.action_main_type, 0.0) + abs(j.spending or 0.0)

    monthly_avg = {k: v / 12.0 for k, v in totals.items()}

    code_map: dict[str, CodeData] = {
        c.code_id: c
        for c in session.exec(select(CodeData).where(CodeData.code_id.in_(monthly_avg.keys()))).all()
    }

    rows: list[Budget] = []
    for category_code, avg in monthly_avg.items():
        existing = session.get(Budget, (next_year_str, category_code))
        if existing is not None:
            for m in range(1, 13):
                setattr(existing, f"expected{m:02d}", avg)
            session.add(existing)
            rows.append(existing)
        else:
            code = code_map.get(category_code)
            new_row = Budget(
                budget_year=next_year_str,
                category_code=category_code,
                category_name=code.name if code else category_code,
                code_type=code.code_type if code else "",
                **{f"expected{m:02d}": avg for m in range(1, 13)},
            )
            session.add(new_row)
            rows.append(new_row)
    session.commit()
    for r in rows:
        session.refresh(r)
    return rows
