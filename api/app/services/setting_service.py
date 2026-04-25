"""Settings domain service functions (flat, session-as-parameter)."""
from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import func
from sqlmodel import Session, select

from app.models.settings.account import Account, AccountCreate, AccountUpdate


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
