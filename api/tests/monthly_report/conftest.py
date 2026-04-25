"""Shared monthly_report fixtures: in-memory factory sessions seeded for analytics
and settlement golden tests.
"""
from __future__ import annotations

from collections.abc import Generator

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401  registers tables on SQLModel.metadata


def _new_session() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return Session(engine)


@pytest.fixture
def analytics_fixture_session() -> Generator[Session, None, None]:
    """Factory session pre-seeded for BE-017 analytics golden tests.

    Seeds vesting_month=202603 with:
      - Two credit cards: CC-A (charged 1500), CC-B (charged 500)
      - Account journals across action_main_type 'expense', 'income', 'invest', 'transfer'
      - Budget for 2026 with expected03 set per code_type

    Tables touched: Journal, Budget, CreditCard. Sufficient for the four
    analytics endpoints' golden assertions.
    """
    from app.models.monthly_report.journal import JournalCreate
    from app.models.settings.budget import Budget
    from app.models.settings.credit_card import CreditCard
    from app.services.monthly_report_service import create_journal

    session = _new_session()
    try:
        session.add(
            CreditCard(
                credit_card_id="CC-A",
                card_name="Card A",
                fx_code="USD",
                in_use="Y",
                credit_card_index=1,
            )
        )
        session.add(
            CreditCard(
                credit_card_id="CC-B",
                card_name="Card B",
                fx_code="USD",
                in_use="Y",
                credit_card_index=2,
            )
        )
        session.add(
            Budget(
                budget_year="2026",
                category_code="EXP01",
                category_name="Living",
                code_type="expense",
                **{f"expected{m:02d}": (3000.0 if m == 3 else 0.0) for m in range(1, 13)},
            )
        )
        session.add(
            Budget(
                budget_year="2026",
                category_code="INC01",
                category_name="Salary",
                code_type="income",
                **{f"expected{m:02d}": (5000.0 if m == 3 else 0.0) for m in range(1, 13)},
            )
        )
        session.commit()

        def j(**ov):
            base = dict(
                vesting_month="202603",
                spend_date="20260315",
                spend_way="ACC-1",
                spend_way_type="account",
                spend_way_table="Account",
                action_main="EXP01",
                action_main_type="expense",
                action_main_table="Code_Data",
                action_sub=None,
                action_sub_type=None,
                action_sub_table=None,
                spending=-100.0,
                invoice_number=None,
                note=None,
            )
            base.update(ov)
            create_journal(session, JournalCreate(**base))

        # Expenditure rows (excluded types are 'invest' / 'transfer')
        j(action_main_type="expense", action_sub_type="food", spending=-1000.0)
        j(action_main_type="expense", action_sub_type="utility", spending=-500.0)
        j(action_main_type="income", action_sub_type="salary", spending=4000.0)
        # Invest rows
        j(action_main_type="invest", action_sub_type="stock", spending=-800.0)
        j(action_main_type="invest", action_sub_type="bond", spending=-200.0)
        # Excluded for ratio
        j(action_main_type="transfer", action_sub_type="self", spending=-300.0)
        # Credit-card spend
        j(spend_way="CC-A", spend_way_type="credit_card", spending=-1000.0,
          action_main_type="expense", action_sub_type="food")
        j(spend_way="CC-A", spend_way_type="credit_card", spending=-500.0,
          action_main_type="expense", action_sub_type="food")
        j(spend_way="CC-B", spend_way_type="credit_card", spending=-500.0,
          action_main_type="expense", action_sub_type="utility")

        yield session
    finally:
        session.close()
