"""BE-012 — Budget management endpoint tests."""
from __future__ import annotations

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.monthly_report.journal import Journal
from app.models.settings.budget import Budget, BudgetCreate, BudgetRead, BudgetUpdate
from app.models.settings.code_data import CodeData
from app.services.setting_service import (
    bulk_update_budgets,
    copy_budget_from_previous,
    list_budget_year_range,
    list_budgets_by_year,
)


def _zero_months() -> dict[str, float]:
    return {f"expected{m:02d}": 0.0 for m in range(1, 13)}


def _seed_budget(session: Session, year: str, code: str, **months) -> Budget:
    payload = _zero_months()
    payload.update(months)
    b = Budget(
        budget_year=year,
        category_code=code,
        category_name=code,
        code_type="Floating",
        **payload,
    )
    session.add(b)
    session.commit()
    session.refresh(b)
    return b


def _seed_code(session: Session, code_id: str, name: str = "X", code_type: str = "Floating") -> CodeData:
    c = CodeData(code_id=code_id, code_type=code_type, name=name, in_use="Y", code_index=1)
    session.add(c)
    session.commit()
    session.refresh(c)
    return c


def _seed_journal(session: Session, spend_date: str, action_main_type: str, spending: float) -> None:
    j = Journal(
        vesting_month=spend_date[:6],
        spend_date=spend_date,
        spend_way="A",
        spend_way_type="account",
        spend_way_table="Account",
        action_main="X",
        action_main_type=action_main_type,
        action_main_table="Code_Data",
        spending=spending,
    )
    session.add(j)
    session.commit()


def test_schema_examples() -> None:
    for cls in (Budget, BudgetCreate, BudgetUpdate, BudgetRead):
        js = cls.model_json_schema()
        assert "example" in js
        for n, p in js["properties"].items():
            assert "description" in p, f"{cls.__name__}.{n}"
            assert "examples" in p, f"{cls.__name__}.{n}"


def test_list_by_year(session: Session) -> None:
    _seed_budget(session, "2026", "B")
    _seed_budget(session, "2026", "A")
    _seed_budget(session, "2025", "C")
    rows = list_budgets_by_year(session, 2026)
    assert [r.category_code for r in rows] == ["A", "B"]


def test_year_range_distinct(session: Session) -> None:
    _seed_budget(session, "2024", "A")
    _seed_budget(session, "2026", "A")
    _seed_budget(session, "2025", "A")
    assert list_budget_year_range(session) == [2024, 2025, 2026]


def test_bulk_update_partial(session: Session) -> None:
    _seed_budget(session, "2026", "A")
    _seed_budget(session, "2026", "B")
    rows = bulk_update_budgets(
        session,
        [
            BudgetUpdate(budget_year="2026", category_code="A", expected01=100.0),
            BudgetUpdate(budget_year="2026", category_code="B", expected12=200.0),
        ],
    )
    assert len(rows) == 2
    assert rows[0].expected01 == 100.0
    assert rows[1].expected12 == 200.0


def test_bulk_update_404_rolls_back(session: Session) -> None:
    _seed_budget(session, "2026", "A")
    with pytest.raises(HTTPException) as ei:
        bulk_update_budgets(
            session,
            [
                BudgetUpdate(budget_year="2026", category_code="A", expected01=999.0),
                BudgetUpdate(budget_year="2026", category_code="MISSING", expected01=1.0),
            ],
        )
    assert ei.value.status_code == 404
    refreshed = session.get(Budget, ("2026", "A"))
    assert refreshed.expected01 == 0.0


def test_copy_from_previous_math(session: Session) -> None:
    _seed_code(session, "expense", "Expense", "Floating")
    _seed_journal(session, "20250115", "expense", -120.0)
    _seed_journal(session, "20250215", "expense", -120.0)
    rows = copy_budget_from_previous(session, 2026)
    assert len(rows) == 1
    avg = 240.0 / 12.0
    for m in range(1, 13):
        assert getattr(rows[0], f"expected{m:02d}") == avg


def test_copy_from_previous_upserts(session: Session) -> None:
    _seed_code(session, "expense")
    _seed_budget(session, "2026", "expense", expected01=999.0)
    _seed_journal(session, "20250101", "expense", -1200.0)
    rows = copy_budget_from_previous(session, 2026)
    assert len(rows) == 1
    assert rows[0].expected01 == 100.0


# ---- routers ----


def test_router_mounted(client: TestClient) -> None:
    paths = set(client.app.openapi()["paths"].keys())
    assert {
        "/settings/budgets/year-range",
        "/settings/budgets/{year}",
        "/settings/budgets",
        "/settings/budgets/{year}/copy-from-previous",
    } <= paths


def test_year_range_endpoint(client: TestClient, session: Session) -> None:
    _seed_budget(session, "2025", "A")
    _seed_budget(session, "2026", "A")
    res = client.get("/settings/budgets/year-range")
    assert res.status_code == 200
    assert res.json()["data"] == [2025, 2026]


def test_get_by_year_happy(client: TestClient, session: Session) -> None:
    _seed_budget(session, "2026", "A")
    res = client.get("/settings/budgets/2026")
    assert res.status_code == 200
    body = res.json()["data"]
    assert len(body) == 1 and body[0]["category_code"] == "A"


def test_get_by_year_invalid_422(client: TestClient) -> None:
    res = client.get("/settings/budgets/notayear")
    assert res.status_code == 422


def test_put_bulk_happy(client: TestClient, session: Session) -> None:
    _seed_budget(session, "2026", "A")
    res = client.put(
        "/settings/budgets",
        json=[{"budget_year": "2026", "category_code": "A", "expected03": 333.0}],
    )
    assert res.status_code == 200
    assert res.json()["data"][0]["expected03"] == 333.0


def test_put_bulk_404(client: TestClient) -> None:
    res = client.put(
        "/settings/budgets",
        json=[{"budget_year": "2099", "category_code": "Z", "expected01": 1.0}],
    )
    assert res.status_code == 404


def test_copy_endpoint_happy(client: TestClient, session: Session) -> None:
    _seed_code(session, "expense")
    _seed_journal(session, "20250115", "expense", -1200.0)
    res = client.post("/settings/budgets/2026/copy-from-previous")
    assert res.status_code == 200
    body = res.json()["data"]
    assert len(body) == 1
    assert body[0]["expected01"] == 100.0
