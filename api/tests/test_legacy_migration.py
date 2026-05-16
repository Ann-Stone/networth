"""BE-005 — Migrator tests against the hand-crafted ``legacy_tiny.db`` fixture.

These tests never touch real legacy data. They use only
``tests/fixtures/legacy_tiny.db`` (rebuilt via
``tests/fixtures/build_legacy_tiny.py``).

Granular acceptance commands map to tests in this file as follows:

* sub-task 4   → ``test_migration_is_idempotent``
* sub-task 5   → ``test_account_migration_drops_carrier_no``
* sub-task 6   → ``test_credit_card_migration_drops_carrier_no``
* sub-task 7   → ``test_settings_tables_row_counts``
* sub-task 8   → ``test_journal_dates_iso`` (assertion: YYYYMMDD / YYYYMM,
                 per plan deviation — see plan file)
* sub-task 9   → ``test_asset_tables_row_counts``
* sub-task 10  → ``test_dashboard_tables_row_counts``
* sub-task 11  → ``test_initial_setting_skipped``
* sub-task 12  → ``test_camel_to_snake_normalization``
* sub-task 13  → ``test_end_to_end_row_counts_match``
* sub-task 14  → ``test_golden_fixture_migration``
* (expansion)  → ``test_snapshot_tables_row_counts``
"""
from __future__ import annotations

import re
import sqlite3
from pathlib import Path

import pytest
from sqlalchemy import inspect
from sqlmodel import Session, func, select

from scripts import migrate_from_legacy
from tests.fixtures import build_legacy_tiny
from scripts.migrate_from_legacy import (
    MigrationCountMismatch,
    _snake,
    _to_yyyymm,
    _to_yyyymmdd,
    run_migration,
)
from app.models.assets.estate import Estate, EstateJournal
from app.models.assets.insurance import Insurance, InsuranceJournal
from app.models.assets.loan import Loan, LoanJournal
from app.models.assets.other_asset import OtherAsset
from app.models.assets.stock import StockDetail, StockJournal
from app.models.dashboard.fx_rate import FXRate
from app.models.dashboard.stock_price_history import StockPriceHistory
from app.models.dashboard.target_setting import TargetSetting
from app.models.monthly_report.account_balance import AccountBalance
from app.models.monthly_report.credit_card_balance import CreditCardBalance
from app.models.monthly_report.estate_net_value_history import EstateNetValueHistory
from app.models.monthly_report.insurance_net_value_history import (
    InsuranceNetValueHistory,
)
from app.models.monthly_report.journal import Journal
from app.models.monthly_report.loan_balance import LoanBalance
from app.models.monthly_report.stock_net_value_history import StockNetValueHistory
from app.models.settings.account import Account
from app.models.settings.alarm import Alarm
from app.models.settings.budget import Budget
from app.models.settings.code_data import CodeData
from app.models.settings.credit_card import CreditCard


FIXTURE = Path(__file__).resolve().parent / "fixtures" / "legacy_tiny.db"


def _scalar(n) -> int:
    if isinstance(n, tuple):
        return int(n[0])
    return int(n)


def _count(session: Session, model) -> int:
    return _scalar(session.exec(select(func.count()).select_from(model)).one())


@pytest.fixture
def target_engine(tmp_path: Path):
    """Per-test SQLite file engine; isolated from any real DB."""
    db_path = tmp_path / "target_test.db"
    engine = migrate_from_legacy._build_engine(f"sqlite:///{db_path}")
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture(scope="session")
def _legacy_fixture_path() -> Path:
    """Build ``legacy_tiny.db`` once per session (it isn't committed; api/.gitignore drops *.db)."""
    build_legacy_tiny.build(FIXTURE)
    return FIXTURE


@pytest.fixture
def legacy_conn(_legacy_fixture_path: Path):
    uri = f"file:{_legacy_fixture_path}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# sub-task 4: idempotency
# ---------------------------------------------------------------------------

def test_migration_is_idempotent(legacy_conn, target_engine) -> None:
    first = run_migration(legacy_conn, target_engine, wipe=True)
    second = run_migration(legacy_conn, target_engine, wipe=True)
    assert first == second


# ---------------------------------------------------------------------------
# sub-task 5: Account drops carrier_no
# ---------------------------------------------------------------------------

def test_account_migration_drops_carrier_no(legacy_conn, target_engine) -> None:
    run_migration(legacy_conn, target_engine, wipe=True)
    insp = inspect(target_engine)
    cols = {c["name"] for c in insp.get_columns("Account")}
    assert "carrier_no" not in cols
    with Session(target_engine) as session:
        assert _count(session, Account) == 2


# ---------------------------------------------------------------------------
# sub-task 6: Credit_Card drops carrier_no
# ---------------------------------------------------------------------------

def test_credit_card_migration_drops_carrier_no(legacy_conn, target_engine) -> None:
    run_migration(legacy_conn, target_engine, wipe=True)
    insp = inspect(target_engine)
    cols = {c["name"] for c in insp.get_columns("Credit_Card")}
    assert "carrier_no" not in cols
    with Session(target_engine) as session:
        assert _count(session, CreditCard) == 2


# ---------------------------------------------------------------------------
# sub-task 7: settings tables row counts
# ---------------------------------------------------------------------------

def test_settings_tables_row_counts(legacy_conn, target_engine) -> None:
    run_migration(legacy_conn, target_engine, wipe=True)
    with Session(target_engine) as session:
        assert _count(session, CodeData) == 2
        assert _count(session, Account) == 2
        assert _count(session, CreditCard) == 2
        assert _count(session, Budget) == 2
        assert _count(session, Alarm) == 2


# ---------------------------------------------------------------------------
# sub-task 8: Journal dates normalized to YYYYMMDD / YYYYMM
# (Plan deviates from granular's "ISO 8601" wording — see plan file.)
# ---------------------------------------------------------------------------

def test_journal_dates_iso(legacy_conn, target_engine) -> None:
    run_migration(legacy_conn, target_engine, wipe=True)
    yyyymmdd = re.compile(r"^\d{8}$")
    yyyymm = re.compile(r"^\d{6}$")
    with Session(target_engine) as session:
        for j in session.exec(select(Journal)).all():
            assert yyyymmdd.fullmatch(j.spend_date), j.spend_date
            assert yyyymm.fullmatch(j.vesting_month), j.vesting_month


# ---------------------------------------------------------------------------
# sub-task 9: asset-domain row counts
# ---------------------------------------------------------------------------

def test_asset_tables_row_counts(legacy_conn, target_engine) -> None:
    run_migration(legacy_conn, target_engine, wipe=True)
    with Session(target_engine) as session:
        assert _count(session, OtherAsset) == 2
        assert _count(session, StockJournal) == 2
        assert _count(session, StockDetail) == 2
        assert _count(session, Insurance) == 2
        assert _count(session, InsuranceJournal) == 2
        assert _count(session, Estate) == 2
        assert _count(session, EstateJournal) == 2
        assert _count(session, Loan) == 2
        assert _count(session, LoanJournal) == 2


# ---------------------------------------------------------------------------
# sub-task 10: dashboard-domain row counts
# ---------------------------------------------------------------------------

def test_dashboard_tables_row_counts(legacy_conn, target_engine) -> None:
    run_migration(legacy_conn, target_engine, wipe=True)
    with Session(target_engine) as session:
        assert _count(session, FXRate) == 2
        assert _count(session, StockPriceHistory) == 2
        assert _count(session, TargetSetting) == 2


# ---------------------------------------------------------------------------
# Plan scope expansion: snapshot tables row counts
# ---------------------------------------------------------------------------

def test_snapshot_tables_row_counts(legacy_conn, target_engine) -> None:
    run_migration(legacy_conn, target_engine, wipe=True)
    with Session(target_engine) as session:
        assert _count(session, LoanBalance) == 2
        assert _count(session, StockNetValueHistory) == 2
        assert _count(session, InsuranceNetValueHistory) == 2
        assert _count(session, EstateNetValueHistory) == 2
        # Also verify monthly-report balance tables migrated.
        assert _count(session, AccountBalance) == 2
        assert _count(session, CreditCardBalance) == 2


# ---------------------------------------------------------------------------
# sub-task 11: Initial_Setting is skipped
# ---------------------------------------------------------------------------

def test_initial_setting_skipped(legacy_conn, target_engine) -> None:
    # Fixture has Initial_Setting with 1 row.
    src_count = legacy_conn.execute(
        "SELECT COUNT(*) AS n FROM Initial_Setting"
    ).fetchone()["n"]
    assert src_count == 1, "Fixture should contain 1 Initial_Setting row"

    run_migration(legacy_conn, target_engine, wipe=True)

    insp = inspect(target_engine)
    target_tables = set(insp.get_table_names())
    assert "Initial_Setting" not in target_tables


# ---------------------------------------------------------------------------
# sub-task 12: camelCase → snake_case helper
# ---------------------------------------------------------------------------

def test_camel_to_snake_normalization() -> None:
    assert _snake("creditCardIndex") == "credit_card_index"
    assert _snake("alreadySnakeCase") == "already_snake_case"
    assert _snake("XMLHttpRequest") == "x_m_l_http_request"  # naive helper is fine
    # Already snake-case input is preserved.
    assert _snake("account_id") == "account_id"
    assert _snake("expected_spend") == "expected_spend"


# ---------------------------------------------------------------------------
# sub-task 13: orchestrator row-count assertion
# ---------------------------------------------------------------------------

def test_end_to_end_row_counts_match(legacy_conn, target_engine) -> None:
    counts = run_migration(legacy_conn, target_engine, wipe=True)
    # Every retained table inserted exactly 2 rows from the fixture.
    for table_name in (
        "Code_Data", "Account", "Credit_Card", "Budget", "Alarm",
        "Other_Asset", "Loan", "Loan_Journal", "Loan_Balance",
        "Stock_Journal", "Stock_Detail", "Stock_Net_Value_History",
        "Insurance", "Insurance_Journal", "Insurance_Net_Value_History",
        "Estate", "Estate_Journal", "Estate_Net_Value_History",
        "Journal", "Account_Balance", "Credit_Card_Balance",
        "FX_Rate", "Stock_Price_History", "Target_Setting",
    ):
        assert counts.get(table_name) == 2, f"{table_name} count mismatch: {counts.get(table_name)}"


def test_orchestrator_raises_on_count_mismatch(legacy_conn, target_engine, monkeypatch) -> None:
    """Sanity check: if a migrator under-inserts, MigrationCountMismatch fires."""
    def bad_migrator(src, session):
        # Insert nothing — but fixture has 2 rows for Code_Data.
        return 0
    monkeypatch.setattr(migrate_from_legacy, "migrate_codes", bad_migrator)
    with pytest.raises(MigrationCountMismatch):
        run_migration(legacy_conn, target_engine, wipe=True)


# ---------------------------------------------------------------------------
# sub-task 14: golden fixture
# ---------------------------------------------------------------------------

def test_golden_fixture_migration(legacy_conn, target_engine) -> None:
    """Holistic check: full migration against the hand-crafted fixture."""
    counts = run_migration(legacy_conn, target_engine, wipe=True)

    # Every retained table → exactly 2 rows.
    expected = {name: 2 for name in (
        "Code_Data", "Account", "Credit_Card", "Budget", "Alarm",
        "Other_Asset", "Loan", "Loan_Journal", "Loan_Balance",
        "Stock_Journal", "Stock_Detail", "Stock_Net_Value_History",
        "Insurance", "Insurance_Journal", "Insurance_Net_Value_History",
        "Estate", "Estate_Journal", "Estate_Net_Value_History",
        "Journal", "Account_Balance", "Credit_Card_Balance",
        "FX_Rate", "Stock_Price_History", "Target_Setting",
    )}
    assert counts == expected

    # carrier_no must not appear in the target schema.
    insp = inspect(target_engine)
    assert "carrier_no" not in {c["name"] for c in insp.get_columns("Account")}
    assert "carrier_no" not in {c["name"] for c in insp.get_columns("Credit_Card")}

    # Initial_Setting must not have been created.
    assert "Initial_Setting" not in set(insp.get_table_names())

    # Account's legacy `carrier_no="DROP-ME-1"` must not leak into any text column.
    with Session(target_engine) as session:
        accounts = session.exec(select(Account)).all()
        for a in accounts:
            for value in (a.name, a.memo or "", a.owner or ""):
                assert "DROP-ME" not in value, f"Leaked carrier_no into {a!r}"
        cards = session.exec(select(CreditCard)).all()
        for c in cards:
            for value in (c.card_name, c.note or ""):
                assert "DROP" not in value, f"Leaked carrier_no into {c!r}"

        # FK reference translation: Loan.account_id should be the business
        # account_id string (FAKE-ACCT-01), not the legacy int "1".
        loans = session.exec(select(Loan).where(Loan.loan_id == "1")).all()
        assert loans, "Loan id=1 missing"
        assert loans[0].account_id == "FAKE-ACCT-01"

        # Insurance translates in_account_id/out_account_id INT → account_id str.
        ins = session.exec(select(Insurance).where(Insurance.insurance_id == "1")).all()
        assert ins, "Insurance id=1 missing"
        assert ins[0].in_account == "FAKE-ACCT-01"
        assert ins[0].out_account == "FAKE-ACCT-01"

        # Date normalization: Loan.apply_date "2020-01-01" → "20200101".
        loan_one = loans[0]
        assert loan_one.apply_date == "20200101"
        assert loan_one.grace_expire_date == "20200401"

        # Loan.repayed semantics: legacy 'N' flag → new 0.0 float.
        assert loan_one.repayed == 0.0


# ---------------------------------------------------------------------------
# Date helper unit tests (support sub-task 8)
# ---------------------------------------------------------------------------

def test_to_yyyymmdd_handles_iso_and_passthrough() -> None:
    assert _to_yyyymmdd("2026-04-18") == "20260418"
    assert _to_yyyymmdd("20260418") == "20260418"
    assert _to_yyyymmdd("2026-04-18 00:00:00") == "20260418"
    assert _to_yyyymmdd(None) is None
    assert _to_yyyymmdd("") is None


def test_to_yyyymm_handles_iso_and_passthrough() -> None:
    assert _to_yyyymm("202604") == "202604"
    assert _to_yyyymm("2026-04-18") == "202604"
    assert _to_yyyymm(None) is None
