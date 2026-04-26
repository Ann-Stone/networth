"""Router-level tests for /utilities/selections/* endpoints."""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.settings.account import Account
from app.models.settings.code_data import CodeData


def _seed_account(session: Session) -> None:
    session.add(
        Account(
            account_id="AC1",
            name="Cash NTD",
            account_type="CASH",
            fx_code="TWD",
            is_calculate="Y",
            in_use="Y",
            discount=1.0,
            owner=None,
            memo=None,
            account_index=1,
        )
    )
    session.commit()


def test_all_selection_endpoints_return_envelope(client: TestClient, session: Session) -> None:
    for path in (
        "/utilities/selections/accounts",
        "/utilities/selections/credit-cards",
        "/utilities/selections/loans",
        "/utilities/selections/insurances",
        "/utilities/selections/codes",
    ):
        resp = client.get(path)
        assert resp.status_code == 200, path
        body = resp.json()
        assert body["status"] == 1, path
        assert isinstance(body["data"], list), path


def test_account_selection_groups_happy(client: TestClient, session: Session) -> None:
    _seed_account(session)
    resp = client.get("/utilities/selections/accounts")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == 1
    assert body["data"][0]["label"] == "CASH"
    assert body["data"][0]["options"][0]["label"] == "Cash NTD"
    assert body["data"][0]["options"][0]["value"]  # stringified id


def test_credit_card_selection_empty(client: TestClient, session: Session) -> None:
    resp = client.get("/utilities/selections/credit-cards")
    assert resp.status_code == 200
    assert resp.json()["data"] == []


def test_sub_code_group_not_found_returns_404(client: TestClient, session: Session) -> None:
    resp = client.get("/utilities/selections/codes/UNKNOWN")
    assert resp.status_code == 404
    body = resp.json()
    assert body["status"] == 0


def test_sub_code_group_happy(client: TestClient, session: Session) -> None:
    session.add(
        CodeData(
            code_id="MAIN-A",
            code_type="Floating",
            name="Food",
            parent_id=None,
            in_use="Y",
            code_index=1,
        )
    )
    session.add(
        CodeData(
            code_id="SUB-1",
            code_type="Floating",
            name="Groceries",
            parent_id="MAIN-A",
            in_use="Y",
            code_index=2,
        )
    )
    session.commit()

    resp = client.get("/utilities/selections/codes/MAIN-A")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == 1
    assert body["data"][0]["label"] == "sub"
    assert body["data"][0]["options"][0]["value"] == "SUB-1"
