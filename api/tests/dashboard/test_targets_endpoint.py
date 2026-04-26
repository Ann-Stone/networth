"""BE-027 — targets endpoint tests."""
from __future__ import annotations

from datetime import datetime

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.dashboard.target_setting import TargetSetting


def test_list_targets_happy(client: TestClient, session: Session) -> None:
    session.add(TargetSetting(distinct_number="T1", target_year="2026", setting_value=1.0, is_done="N"))
    session.commit()

    r = client.get("/dashboard/targets")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == 1
    assert body["data"][0]["distinct_number"] == "T1"


def test_create_target_happy(client: TestClient) -> None:
    r = client.post(
        "/dashboard/targets",
        json={"distinct_number": "T-A", "setting_value": 500.0},
    )
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["target_year"] == datetime.now().strftime("%Y")
    assert data["is_done"] == "N"


def test_update_target_happy(client: TestClient, session: Session) -> None:
    session.add(TargetSetting(distinct_number="T1", target_year="2026", setting_value=1.0, is_done="N"))
    session.commit()
    r = client.put("/dashboard/targets/T1", json={"setting_value": 2000.0})
    assert r.status_code == 200
    assert r.json()["data"]["setting_value"] == 2000.0


def test_update_target_is_done_only(client: TestClient, session: Session) -> None:
    session.add(TargetSetting(distinct_number="T1", target_year="2026", setting_value=1.0, is_done="N"))
    session.commit()
    r = client.put("/dashboard/targets/T1", json={"is_done": "Y"})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["is_done"] == "Y"
    assert data["setting_value"] == 1.0
    assert data["target_year"] == "2026"


def test_delete_target_happy(client: TestClient, session: Session) -> None:
    session.add(TargetSetting(distinct_number="T1", target_year="2026", setting_value=1.0, is_done="N"))
    session.commit()
    r = client.delete("/dashboard/targets/T1")
    assert r.status_code == 200


def test_update_target_missing_returns_404(client: TestClient) -> None:
    r = client.put("/dashboard/targets/9999", json={"is_done": "Y"})
    assert r.status_code == 404


def test_delete_target_missing_returns_404(client: TestClient) -> None:
    r = client.delete("/dashboard/targets/9999")
    assert r.status_code == 404


def test_create_target_invalid_body_returns_422(client: TestClient) -> None:
    r = client.post(
        "/dashboard/targets",
        json={"distinct_number": "T-X", "setting_value": "not-a-number"},
    )
    assert r.status_code == 422
