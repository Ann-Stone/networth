"""BE-028 — alarms endpoint tests."""
from __future__ import annotations

from datetime import datetime

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.settings.alarm import Alarm
from app.services.dashboard_service import get_upcoming_alarms


def test_get_upcoming_alarms_monthly_expansion(session: Session) -> None:
    # Frozen "now" = 2026-04-15
    now = datetime(2026, 4, 15)
    session.add(
        Alarm(
            alarm_type="M",
            alarm_date="15",
            content="Pay credit card",
            due_date="20260631",  # not relevant; treat as YYYYMM prefix
        )
    )
    session.commit()

    out = get_upcoming_alarms(session, now=now)
    # 6 months expansion: 04, 05, 06 then truncated by due_date (06)
    dates = [item.date for item in out]
    assert "04/15" in dates
    assert "05/15" in dates
    assert "06/15" in dates
    # Months past due_date 202606 are skipped
    assert "07/15" not in dates


def test_get_upcoming_alarms_non_recurring(session: Session) -> None:
    now = datetime(2026, 4, 15)
    session.add(
        Alarm(
            alarm_type="O",
            alarm_date="20260620",
            content="One-off reminder",
        )
    )
    session.add(
        Alarm(
            alarm_type="O",
            alarm_date="20251231",
            content="Past reminder",
        )
    )
    session.commit()

    out = get_upcoming_alarms(session, now=now)
    assert any(item.date == "20260620" for item in out)
    assert all(item.date != "20251231" for item in out)


def test_list_alarms_happy(client: TestClient, session: Session) -> None:
    session.add(
        Alarm(alarm_type="O", alarm_date="20260620", content="Visit dentist")
    )
    session.commit()
    r = client.get("/dashboard/alarms")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == 1


def test_list_alarms_returns_empty(client: TestClient) -> None:
    r = client.get("/dashboard/alarms")
    assert r.status_code == 200
    assert r.json()["data"] == []
