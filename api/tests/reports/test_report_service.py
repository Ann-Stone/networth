"""BE-025 — report_service unit tests."""
from __future__ import annotations

from sqlmodel import Session

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
from app.services.report_service import (
    get_asset_breakdown,
    get_balance_sheet,
    get_expenditure_trend,
    get_latest_fx_rate,
)


def test_get_latest_fx_rate_fallback(session: Session) -> None:
    # No row at all → 1.0
    assert get_latest_fx_rate(session, "USD", "202604") == 1.0
    # Row outside the window → fallback
    session.add(FXRate(import_date="20270101", code="USD", buy_rate=33.0))
    session.commit()
    assert get_latest_fx_rate(session, "USD", "202604") == 33.0
    # Row inside window beats fallback
    session.add(FXRate(import_date="20260415", code="USD", buy_rate=31.5))
    session.commit()
    assert get_latest_fx_rate(session, "USD", "202604") == 31.5
    # Base currency short-circuits to 1.0
    assert get_latest_fx_rate(session, "TWD", "202604") == 1.0


def _seed_balance_fixture(session: Session) -> None:
    session.add(
        AccountBalance(
            vesting_month="202604",
            id="A1",
            name="TWD Bank",
            balance=100000.0,
            fx_code="TWD",
            fx_rate=1.0,
            is_calculate="Y",
        )
    )
    session.add(
        AccountBalance(
            vesting_month="202604",
            id="A2",
            name="USD Bank",
            balance=1000.0,
            fx_code="USD",
            fx_rate=32.0,
            is_calculate="Y",
        )
    )
    session.add(
        StockNetValueHistory(
            vesting_month="202604",
            id="S1",
            asset_id="AC1",
            stock_code="AAPL",
            stock_name="Apple",
            amount=10.0,
            price=2000.0,  # market value already
            cost=1500.0,
            fx_code="USD",
            fx_rate=32.0,
        )
    )
    session.add(
        EstateNetValueHistory(
            vesting_month="202604",
            id="E1",
            asset_id="AC2",
            name="Condo",
            market_value=500000.0,
            cost=400000.0,
            estate_status="hold",
        )
    )
    session.add(
        InsuranceNetValueHistory(
            vesting_month="202604",
            id="I1",
            asset_id="AC3",
            name="Whole Life",
            surrender_value=2000.0,
            cost=1500.0,
            fx_code="USD",
            fx_rate=32.0,
        )
    )
    session.add(
        LoanBalance(
            vesting_month="202604",
            id="L1",
            name="Mortgage",
            balance=-200000.0,
            cost=0.0,
        )
    )
    session.add(
        CreditCardBalance(
            vesting_month="202604",
            id="CC1",
            name="Visa",
            balance=-3000.0,
            fx_rate=1.0,
        )
    )
    session.commit()


def test_get_balance_sheet_golden(session: Session) -> None:
    _seed_balance_fixture(session)

    sheet = get_balance_sheet(session)
    # accounts: 100000 + 1000*32 = 132000
    accounts_total = sum(line.amount for line in sheet.assets.accounts)
    assert accounts_total == 132000.0
    # stocks: 2000 * 32 = 64000
    assert sheet.assets.stocks[0].amount == 64000.0
    # estates: 500000
    assert sheet.assets.estates[0].amount == 500000.0
    # insurances: 2000 * 32 = 64000
    assert sheet.assets.insurances[0].amount == 64000.0
    # loans + cc: -200000 + -3000
    loans_total = sum(line.amount for line in sheet.liabilities.loans)
    cc_total = sum(line.amount for line in sheet.liabilities.credit_cards)
    assert loans_total == -200000.0
    assert cc_total == -3000.0
    # net worth = 132000 + 64000 + 500000 + 64000 - 200000 - 3000 = 557000
    assert sheet.net_worth == 557000.0


def test_get_balance_sheet_picks_latest_month(session: Session) -> None:
    session.add(
        AccountBalance(
            vesting_month="202603",
            id="A1",
            name="TWD Bank",
            balance=50000.0,
            fx_code="TWD",
            fx_rate=1.0,
            is_calculate="Y",
        )
    )
    session.add(
        AccountBalance(
            vesting_month="202604",
            id="A1",
            name="TWD Bank",
            balance=70000.0,
            fx_code="TWD",
            fx_rate=1.0,
            is_calculate="Y",
        )
    )
    session.commit()

    sheet = get_balance_sheet(session)
    assert sheet.assets.accounts[0].amount == 70000.0


def test_get_expenditure_trend_monthly_golden(session: Session) -> None:
    # Anchor 202604 → window 202505..202604
    session.add(
        Journal(
            vesting_month="202604",
            spend_date="20260410",
            spend_way="A1",
            spend_way_type="account",
            spend_way_table="Account",
            action_main="E01",
            action_main_type="Floating",
            action_main_table="Code_Data",
            spending=-100.0,
        )
    )
    session.add(
        Journal(
            vesting_month="202604",
            spend_date="20260411",
            spend_way="A1",
            spend_way_type="account",
            spend_way_table="Account",
            action_main="F01",
            action_main_type="Fixed",
            action_main_table="Code_Data",
            spending=-200.0,
        )
    )
    # Income excluded
    session.add(
        Journal(
            vesting_month="202604",
            spend_date="20260412",
            spend_way="A1",
            spend_way_type="account",
            spend_way_table="Account",
            action_main="I01",
            action_main_type="Income",
            action_main_table="Code_Data",
            spending=5000.0,
        )
    )
    # Out-of-window month
    session.add(
        Journal(
            vesting_month="202410",
            spend_date="20241010",
            spend_way="A1",
            spend_way_type="account",
            spend_way_table="Account",
            action_main="E01",
            action_main_type="Floating",
            action_main_table="Code_Data",
            spending=-999.0,
        )
    )
    session.commit()

    trend = get_expenditure_trend(session, "monthly", "202604")
    assert trend.type == "monthly"
    assert len(trend.points) == 12
    by_period = {p.period: p.amount for p in trend.points}
    assert by_period["202604"] == 300.0
    assert by_period["202603"] == 0.0
    assert "202410" not in by_period


def test_get_expenditure_trend_yearly_golden(session: Session) -> None:
    session.add(
        Journal(
            vesting_month="202508",
            spend_date="20250810",
            spend_way="A1",
            spend_way_type="account",
            spend_way_table="Account",
            action_main="E01",
            action_main_type="Floating",
            action_main_table="Code_Data",
            spending=-150.0,
        )
    )
    session.add(
        Journal(
            vesting_month="202412",
            spend_date="20241210",
            spend_way="A1",
            spend_way_type="account",
            spend_way_table="Account",
            action_main="F01",
            action_main_type="Fixed",
            action_main_table="Code_Data",
            spending=-50.0,
        )
    )
    session.commit()

    trend = get_expenditure_trend(session, "yearly", "202604")
    assert trend.type == "yearly"
    assert len(trend.points) == 10
    by_period = {p.period: p.amount for p in trend.points}
    assert by_period["2025"] == 150.0
    assert by_period["2024"] == 50.0
    assert by_period["2026"] == 0.0


def test_get_asset_breakdown_golden(session: Session) -> None:
    _seed_balance_fixture(session)

    breakdown = get_asset_breakdown(session)
    # totals: 132000 + 64000 + 500000 + 64000 = 760000
    assert breakdown.total == 760000.0
    by_type = {item.type: item for item in breakdown.items}
    assert by_type["accounts"].amount == 132000.0
    assert by_type["stocks"].amount == 64000.0
    assert by_type["estates"].amount == 500000.0
    assert by_type["insurances"].amount == 64000.0
    assert by_type["other"].amount == 0.0
    # Shares sum to ~100
    assert abs(sum(i.share for i in breakdown.items) - 100.0) < 0.05
