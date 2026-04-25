"""Monthly Report domain service functions (flat, session-as-parameter)."""
from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.dashboard.fx_rate import FXRate
from app.models.monthly_report.analytics import (
    ExpenditureBudgetResponse,
    ExpenditureBudgetRow,
    ExpenditureRatioItem,
    ExpenditureRatioResponse,
    InvestRatioItem,
    InvestRatioResponse,
    LiabilityItem,
    LiabilityResponse,
)
from app.models.monthly_report.journal import (
    Journal,
    JournalCreate,
    JournalUpdate,
)
from app.models.settings.account import Account
from app.models.settings.budget import Budget
from app.models.settings.credit_card import CreditCard

BASE_CURRENCY = "TWD"


def normalize_spend_date(value: str) -> str:
    """Accept ISO 8601 or `YYYYMMDD` and return canonical `YYYYMMDD`."""
    if not isinstance(value, str) or not value:
        raise ValueError(f"Invalid spend_date: {value!r}")
    if len(value) == 8 and value.isdigit():
        # Validate it's a real date.
        try:
            datetime.strptime(value, "%Y%m%d")
        except ValueError as exc:
            raise ValueError(f"Invalid spend_date: {value!r}") from exc
        return value
    try:
        # Strip Z suffix that fromisoformat doesn't accept on older Python.
        text = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"Invalid spend_date: {value!r}") from exc
    return parsed.strftime("%Y%m%d")


def _month_end(vesting_month: str) -> str:
    return f"{vesting_month}31"


def list_journals_by_month(session: Session, vesting_month: str) -> list[Journal]:
    statement = (
        select(Journal)
        .where(Journal.vesting_month == vesting_month)
        .order_by(Journal.spend_date.asc(), Journal.distinct_number.asc())
    )
    return list(session.exec(statement).all())


def _latest_fx_rate(session: Session, fx_code: str, vesting_month: str) -> float:
    if fx_code == BASE_CURRENCY:
        return 1.0
    statement = (
        select(FXRate)
        .where(FXRate.code == fx_code)
        .where(FXRate.import_date <= _month_end(vesting_month))
        .order_by(FXRate.import_date.desc())
    )
    row = session.exec(statement).first()
    if row is None:
        # Fall back to the most recent prior row of any date.
        any_row = session.exec(
            select(FXRate).where(FXRate.code == fx_code).order_by(FXRate.import_date.desc())
        ).first()
        if any_row is None:
            return 1.0
        return any_row.buy_rate
    return row.buy_rate


def compute_gain_loss(session: Session, journals: list[Journal]) -> float:
    """Sum journal spending across the month, converting non-base currencies via FXRate."""
    if not journals:
        return 0.0
    total = 0.0
    fx_cache: dict[tuple[str, str], float] = {}
    for j in journals:
        fx_code = BASE_CURRENCY
        if j.spend_way_table == "Account":
            account = session.exec(
                select(Account).where(Account.account_id == j.spend_way)
            ).first()
            if account is not None and account.fx_code:
                fx_code = account.fx_code
        rate = 1.0
        if fx_code != BASE_CURRENCY:
            key = (fx_code, j.vesting_month)
            if key not in fx_cache:
                fx_cache[key] = _latest_fx_rate(session, fx_code, j.vesting_month)
            rate = fx_cache[key]
        total += j.spending * rate
    return round(total, 2)


def create_journal(session: Session, payload: JournalCreate) -> Journal:
    data = payload.model_dump()
    data["spend_date"] = normalize_spend_date(data["spend_date"])
    journal = Journal(**data)
    session.add(journal)
    session.commit()
    session.refresh(journal)
    return journal


def update_journal(session: Session, journal_id: int, payload: JournalUpdate) -> Journal:
    journal = session.get(Journal, journal_id)
    if journal is None:
        raise HTTPException(status_code=404, detail=f"Journal not found: {journal_id}")
    updates = payload.model_dump(exclude_unset=True)
    if "spend_date" in updates and updates["spend_date"] is not None:
        updates["spend_date"] = normalize_spend_date(updates["spend_date"])
    for field, value in updates.items():
        setattr(journal, field, value)
    session.add(journal)
    session.commit()
    session.refresh(journal)
    return journal


def delete_journal(session: Session, journal_id: int) -> None:
    journal = session.get(Journal, journal_id)
    if journal is None:
        raise HTTPException(status_code=404, detail=f"Journal not found: {journal_id}")
    session.delete(journal)
    session.commit()


# ---------- Analytics ----------


def compute_expenditure_ratio(session: Session, vesting_month: str) -> ExpenditureRatioResponse:
    """Outer = sum spending grouped by action_main_type; inner = by action_sub_type.

    Excludes ``invest`` and ``transfer`` main-type rows.
    """
    journals = list_journals_by_month(session, vesting_month)
    outer: dict[str, float] = {}
    inner: dict[str, float] = {}
    for j in journals:
        if j.action_main_type in {"invest", "transfer"}:
            continue
        amount = abs(j.spending)
        outer[j.action_main_type] = outer.get(j.action_main_type, 0.0) + amount
        if j.action_sub_type:
            inner[j.action_sub_type] = inner.get(j.action_sub_type, 0.0) + amount
    return ExpenditureRatioResponse(
        outer=[ExpenditureRatioItem(name=k, value=round(v, 2)) for k, v in outer.items()],
        inner=[ExpenditureRatioItem(name=k, value=round(v, 2)) for k, v in inner.items()],
    )


def compute_invest_ratio(session: Session, vesting_month: str) -> InvestRatioResponse:
    journals = list_journals_by_month(session, vesting_month)
    items: dict[str, float] = {}
    for j in journals:
        if j.action_main_type != "invest":
            continue
        key = j.action_sub_type or j.action_main_type
        items[key] = items.get(key, 0.0) + abs(j.spending)
    return InvestRatioResponse(
        items=[InvestRatioItem(name=k, value=round(v, 2)) for k, v in items.items()]
    )


def compute_expenditure_budget(
    session: Session, vesting_month: str
) -> ExpenditureBudgetResponse:
    year = vesting_month[:4]
    mm = vesting_month[-2:]
    budget_field = f"expected{mm}"

    budget_rows = list(session.exec(select(Budget).where(Budget.budget_year == year)).all())
    expected_by_type: dict[str, float] = {}
    for b in budget_rows:
        amt = float(getattr(b, budget_field) or 0.0)
        expected_by_type[b.code_type] = expected_by_type.get(b.code_type, 0.0) + amt

    journals = list_journals_by_month(session, vesting_month)
    actual_by_type: dict[str, float] = {}
    for j in journals:
        actual_by_type[j.action_main_type] = (
            actual_by_type.get(j.action_main_type, 0.0) + abs(j.spending)
        )

    rows: list[ExpenditureBudgetRow] = []
    for action_type in sorted(set(expected_by_type) | set(actual_by_type)):
        expected = round(expected_by_type.get(action_type, 0.0), 2)
        actual = round(actual_by_type.get(action_type, 0.0), 2)
        diff = round(actual - expected, 2)
        usage = round(actual / expected, 4) if expected else 0.0
        rows.append(
            ExpenditureBudgetRow(
                action_main_type=action_type,
                expected=expected,
                actual=actual,
                diff=diff,
                usage_rate=usage,
            )
        )
    return ExpenditureBudgetResponse(rows=rows)


def compute_liability(session: Session, vesting_month: str) -> LiabilityResponse:
    journals = list_journals_by_month(session, vesting_month)
    by_card: dict[str, float] = {}
    for j in journals:
        if j.spend_way_type != "credit_card":
            continue
        by_card[j.spend_way] = by_card.get(j.spend_way, 0.0) + abs(j.spending)

    items: list[LiabilityItem] = []
    for card_id, amount in by_card.items():
        card = session.exec(
            select(CreditCard).where(CreditCard.credit_card_id == card_id)
        ).first()
        items.append(
            LiabilityItem(
                credit_card_id=card_id,
                credit_card_name=card.card_name if card is not None else card_id,
                amount=round(amount, 2),
            )
        )
    return LiabilityResponse(items=items)
