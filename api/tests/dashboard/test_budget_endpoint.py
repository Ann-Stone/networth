"""BE-026 — budget endpoint tests."""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.monthly_report.journal import Journal
from app.models.settings.budget import Budget


def test_get_budget_monthly_happy(client: TestClient, session: Session) -> None:
    session.add(
        Budget(
            budget_year="2026",
            category_code="F01",
            category_name="Rent",
            code_type="Fixed",
            **{f"expected{m:02d}": 10000.0 if m == 4 else 0.0 for m in range(1, 13)},
        )
    )
    session.commit()

    r = client.get("/dashboard/budget?type=monthly&period=202604")
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["type"] == "monthly"
    assert data["period"] == "202604"
    line = next(l for l in data["lines"] if l["category"] == "Rent")
    assert line["planned"] == 10000.0


def test_get_budget_monthly_golden(client: TestClient, session: Session) -> None:
    session.add(
        Budget(
            budget_year="2026",
            category_code="F01",
            category_name="Rent",
            code_type="Fixed",
            **{f"expected{m:02d}": 10000.0 for m in range(1, 13)},
        )
    )
    session.add(
        Journal(
            vesting_month="202604",
            spend_date="20260410",
            spend_way="A1",
            spend_way_type="account",
            spend_way_table="Account",
            action_main="F01",
            action_main_type="Fixed",
            action_main_table="Code_Data",
            spending=-7500.0,
        )
    )
    session.commit()

    r = client.get("/dashboard/budget?type=monthly&period=202604")
    data = r.json()["data"]
    line = next(l for l in data["lines"] if l["category"] == "Rent")
    assert line["planned"] == 10000.0
    assert line["actual"] == 7500.0
    assert line["usage_pct"] == 75.0


def test_get_budget_invalid_period_returns_422(client: TestClient) -> None:
    r = client.get("/dashboard/budget?type=monthly&period=24-03")
    assert r.status_code == 422
