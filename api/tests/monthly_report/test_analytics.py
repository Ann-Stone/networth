"""BE-017 — Journal analytics tests."""
from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.monthly_report.analytics import (
    ExpenditureBudgetResponse,
    ExpenditureRatioResponse,
    InvestRatioResponse,
    LiabilityResponse,
)
from app.services.monthly_report_service import (
    compute_expenditure_budget,
    compute_expenditure_ratio,
    compute_invest_ratio,
    compute_liability,
)

GOLDEN_PATH = Path(__file__).resolve().parent.parent / "fixtures" / "analytics_golden.json"


def _golden() -> dict:
    return json.loads(GOLDEN_PATH.read_text())


def _normalise_items(items: list[dict], key: str = "name") -> list[dict]:
    return sorted(items, key=lambda x: x[key])


# ---- Sub-task 1-4: schemas ----


def test_expenditure_ratio_schema() -> None:
    js = ExpenditureRatioResponse.model_json_schema()
    assert "example" in js
    for n, p in js["properties"].items():
        assert "description" in p, n


def test_invest_ratio_schema() -> None:
    js = InvestRatioResponse.model_json_schema()
    assert "example" in js


def test_expenditure_budget_schema() -> None:
    js = ExpenditureBudgetResponse.model_json_schema()
    assert "example" in js


def test_liability_schema() -> None:
    js = LiabilityResponse.model_json_schema()
    assert "example" in js


# ---- Sub-task 5-8: golden tests ----


def test_expenditure_ratio_golden(analytics_fixture_session: Session) -> None:
    expected = _golden()["expenditure_ratio"]
    actual = compute_expenditure_ratio(analytics_fixture_session, "202603")
    actual_dict = actual.model_dump()
    assert _normalise_items(actual_dict["outer"]) == _normalise_items(expected["outer"])
    assert _normalise_items(actual_dict["inner"]) == _normalise_items(expected["inner"])


def test_invest_ratio_golden(analytics_fixture_session: Session) -> None:
    expected = _golden()["invest_ratio"]
    actual = compute_invest_ratio(analytics_fixture_session, "202603").model_dump()
    assert _normalise_items(actual["items"]) == _normalise_items(expected["items"])


def test_expenditure_budget_golden(analytics_fixture_session: Session) -> None:
    expected = _golden()["expenditure_budget"]
    actual = compute_expenditure_budget(analytics_fixture_session, "202603").model_dump()
    assert _normalise_items(actual["rows"], key="action_main_type") == _normalise_items(
        expected["rows"], key="action_main_type"
    )


def test_liability_golden(analytics_fixture_session: Session) -> None:
    expected = _golden()["liability"]
    actual = compute_liability(analytics_fixture_session, "202603").model_dump()
    assert _normalise_items(actual["items"], key="credit_card_id") == _normalise_items(
        expected["items"], key="credit_card_id"
    )


# ---- Sub-task 9-12: endpoint smoke tests ----


def test_get_expenditure_ratio_endpoint(client: TestClient) -> None:
    r = client.get("/monthly-report/journals/202603/expenditure-ratio")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == 1
    assert "outer" in body["data"] and "inner" in body["data"]


def test_get_invest_ratio_endpoint(client: TestClient) -> None:
    r = client.get("/monthly-report/journals/202603/invest-ratio")
    assert r.status_code == 200
    assert "items" in r.json()["data"]


def test_get_expenditure_budget_endpoint(client: TestClient) -> None:
    r = client.get("/monthly-report/journals/202603/expenditure-budget")
    assert r.status_code == 200
    assert "rows" in r.json()["data"]


def test_get_liability_endpoint(client: TestClient) -> None:
    r = client.get("/monthly-report/journals/202603/liability")
    assert r.status_code == 200
    assert "items" in r.json()["data"]


# ---- Sub-task 13: empty month returns valid empty structures ----


def test_analytics_empty_month_returns_empty_structures(client: TestClient) -> None:
    for sub in ("expenditure-ratio", "invest-ratio", "expenditure-budget", "liability"):
        r = client.get(f"/monthly-report/journals/209912/{sub}")
        assert r.status_code == 200, sub
        data = r.json()["data"]
        if sub == "expenditure-ratio":
            assert data == {"outer": [], "inner": []}
        elif sub == "expenditure-budget":
            assert data == {"rows": []}
        else:
            assert data == {"items": []}
