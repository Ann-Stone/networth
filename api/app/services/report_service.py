"""Reports domain service functions (BE-025).

Aggregates Phase 1 monthly snapshots into balance sheet, expenditure trend,
and asset composition views. FX-converts everything to ``BASE_CURRENCY``.
"""
from __future__ import annotations

from typing import Literal

from sqlmodel import Session, select

from app.models.assets.other_asset import OtherAsset
from app.models.dashboard.fx_rate import FXRate
from app.models.monthly_report.account_balance import AccountBalance
from app.models.monthly_report.credit_card_balance import CreditCardBalance
from app.models.monthly_report.estate_net_value_history import EstateNetValueHistory
from app.models.monthly_report.insurance_net_value_history import (
    InsuranceNetValueHistory,
)
from app.models.monthly_report.journal import Journal
from app.models.monthly_report.loan_balance import LoanBalance
from app.models.monthly_report.stock_net_value_history import StockNetValueHistory
from app.models.reports.asset_breakdown import AssetBreakdownRead, AssetShare
from app.models.reports.balance import (
    BalanceAssets,
    BalanceLiabilities,
    BalanceLine,
    BalanceSheetRead,
)
from app.models.reports.expenditure import ExpenditurePoint, ExpenditureTrendRead

BASE_CURRENCY = "TWD"
EXPENSE_TYPES = ("Floating", "Fixed")


def _month_end(yyyymm: str) -> str:
    return f"{yyyymm}31"


def get_latest_fx_rate(session: Session, currency: str, as_of_month: str) -> float:
    """Return latest ``FXRate.buy_rate`` with ``import_date <= month-end(as_of_month)``.

    Falls back to the most recent prior row of any date for the currency.
    Returns ``1.0`` when ``currency`` is the base currency or no row exists.
    """
    if not currency or currency == BASE_CURRENCY:
        return 1.0
    in_window = (
        select(FXRate)
        .where(FXRate.code == currency)
        .where(FXRate.import_date <= _month_end(as_of_month))
        .order_by(FXRate.import_date.desc())
    )
    row = session.exec(in_window).first()
    if row is not None:
        return row.buy_rate
    fallback = (
        select(FXRate).where(FXRate.code == currency).order_by(FXRate.import_date.desc())
    )
    row = session.exec(fallback).first()
    return row.buy_rate if row is not None else 1.0


def _latest_per_entity(rows, key):
    """Pick the row with the largest ``vesting_month`` per entity ``key(row)``."""
    latest: dict[str, object] = {}
    for r in rows:
        k = key(r)
        if k not in latest or r.vesting_month > latest[k].vesting_month:
            latest[k] = r
    return list(latest.values())


def get_balance_sheet(session: Session) -> BalanceSheetRead:
    accounts_rows = list(session.exec(select(AccountBalance)).all())
    accounts_latest = _latest_per_entity(accounts_rows, key=lambda r: r.id)
    accounts_lines = [
        BalanceLine(
            name=r.name,
            amount=round(r.balance * r.fx_rate, 2),
            currency=r.fx_code,
        )
        for r in accounts_latest
        if r.is_calculate == "Y"
    ]

    stock_rows = list(session.exec(select(StockNetValueHistory)).all())
    stocks_lines = [
        BalanceLine(
            name=r.stock_name,
            amount=round(r.price * r.fx_rate, 2),
            currency=r.fx_code,
        )
        for r in _latest_per_entity(stock_rows, key=lambda r: r.id)
    ]

    estate_rows = list(session.exec(select(EstateNetValueHistory)).all())
    estates_lines = [
        BalanceLine(
            name=r.name,
            amount=round(r.market_value, 2),
            currency=BASE_CURRENCY,
        )
        for r in _latest_per_entity(estate_rows, key=lambda r: r.id)
    ]

    insurance_rows = list(session.exec(select(InsuranceNetValueHistory)).all())
    insurance_lines = [
        BalanceLine(
            name=r.name,
            amount=round(r.surrender_value * r.fx_rate, 2),
            currency=r.fx_code,
        )
        for r in _latest_per_entity(insurance_rows, key=lambda r: r.id)
    ]

    loan_rows = list(session.exec(select(LoanBalance)).all())
    loan_lines = [
        BalanceLine(
            name=r.name,
            amount=round(r.balance, 2),
            currency=BASE_CURRENCY,
        )
        for r in _latest_per_entity(loan_rows, key=lambda r: r.id)
    ]

    cc_rows = list(session.exec(select(CreditCardBalance)).all())
    cc_lines = [
        BalanceLine(
            name=r.name,
            amount=round(r.balance * r.fx_rate, 2),
            currency=BASE_CURRENCY,
        )
        for r in _latest_per_entity(cc_rows, key=lambda r: r.id)
    ]

    asset_total = sum(line.amount for line in accounts_lines + stocks_lines + estates_lines + insurance_lines)
    liability_total = sum(line.amount for line in loan_lines + cc_lines)
    net_worth = round(asset_total + liability_total, 2)  # liabilities are negative

    return BalanceSheetRead(
        assets=BalanceAssets(
            accounts=accounts_lines,
            stocks=stocks_lines,
            estates=estates_lines,
            insurances=insurance_lines,
        ),
        liabilities=BalanceLiabilities(loans=loan_lines, credit_cards=cc_lines),
        net_worth=net_worth,
    )


def _shift_month(yyyymm: str, delta: int) -> str:
    year = int(yyyymm[:4])
    month = int(yyyymm[4:]) + delta
    while month <= 0:
        month += 12
        year -= 1
    while month > 12:
        month -= 12
        year += 1
    return f"{year:04d}{month:02d}"


def get_expenditure_trend(
    session: Session,
    type: Literal["monthly", "yearly"],
    vesting_month: str,
) -> ExpenditureTrendRead:
    if type == "monthly":
        periods = [_shift_month(vesting_month, -i) for i in range(11, -1, -1)]
        bucket_of = lambda vm: vm  # noqa: E731
        windows_filter = (Journal.vesting_month >= periods[0]) & (
            Journal.vesting_month <= periods[-1]
        )
    else:
        end_year = int(vesting_month[:4])
        years = [str(y) for y in range(end_year - 9, end_year + 1)]
        periods = years
        bucket_of = lambda vm: vm[:4]  # noqa: E731
        windows_filter = (Journal.vesting_month >= f"{years[0]}01") & (
            Journal.vesting_month <= f"{years[-1]}12"
        )

    rows = list(
        session.exec(
            select(Journal).where(windows_filter).where(
                Journal.action_main_type.in_(EXPENSE_TYPES)
            )
        ).all()
    )
    sums: dict[str, float] = {p: 0.0 for p in periods}
    for j in rows:
        bucket = bucket_of(j.vesting_month)
        if bucket in sums:
            sums[bucket] += abs(j.spending)

    return ExpenditureTrendRead(
        type=type,
        points=[ExpenditurePoint(period=p, amount=round(sums[p], 2)) for p in periods],
    )


def get_asset_breakdown(session: Session) -> AssetBreakdownRead:
    """Latest-month totals per bucket; ``other`` aggregates ``OtherAsset`` of type ``other``."""
    accounts_rows = list(session.exec(select(AccountBalance)).all())
    accounts_total = sum(
        r.balance * r.fx_rate
        for r in _latest_per_entity(accounts_rows, key=lambda r: r.id)
        if r.is_calculate == "Y"
    )

    stock_rows = list(session.exec(select(StockNetValueHistory)).all())
    stocks_total = sum(
        r.price * r.fx_rate
        for r in _latest_per_entity(stock_rows, key=lambda r: r.id)
    )

    estate_rows = list(session.exec(select(EstateNetValueHistory)).all())
    estates_total = sum(
        r.market_value for r in _latest_per_entity(estate_rows, key=lambda r: r.id)
    )

    insurance_rows = list(session.exec(select(InsuranceNetValueHistory)).all())
    insurances_total = sum(
        r.surrender_value * r.fx_rate
        for r in _latest_per_entity(insurance_rows, key=lambda r: r.id)
    )

    other_assets = list(
        session.exec(select(OtherAsset).where(OtherAsset.asset_type == "other")).all()
    )
    other_total = float(len(other_assets)) and 0.0  # placeholder; OtherAsset has no value column
    other_total = 0.0

    bucket_amounts = {
        "accounts": accounts_total,
        "stocks": stocks_total,
        "estates": estates_total,
        "insurances": insurances_total,
        "other": other_total,
    }
    total = sum(bucket_amounts.values())
    items = []
    for bucket_type, amount in bucket_amounts.items():
        share = round(amount * 100 / total, 2) if total else 0.0
        items.append(
            AssetShare(type=bucket_type, amount=round(amount, 2), share=share)
        )
    return AssetBreakdownRead(total=round(total, 2), items=items)
