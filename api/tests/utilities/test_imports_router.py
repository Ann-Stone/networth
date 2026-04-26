"""Router tests for /utilities/import/* endpoints."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


def _capture_tasks(monkeypatch) -> list[tuple]:
    captured: list[tuple] = []

    from fastapi import BackgroundTasks

    def _add(self, fn, *args, **kwargs):
        captured.append((fn.__name__, args, kwargs))

    monkeypatch.setattr(BackgroundTasks, "add_task", _add)
    return captured


def test_all_import_endpoints_return_202(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured = _capture_tasks(monkeypatch)
    for path, expected_msg in (
        ("/utilities/import/stock-prices", "stock import started"),
        ("/utilities/import/fx-rates", "fx import started"),
        ("/utilities/import/invoices", "invoice import started"),
    ):
        resp = client.post(path, json={"period": "202601"})
        assert resp.status_code == 202, path
        body = resp.json()
        assert body["status"] == 1
        assert body["data"]["message"] == expected_msg
    assert len(captured) == 3
    assert {c[0] for c in captured} == {
        "import_stock_prices",
        "import_fx_rates",
        "import_invoices",
    }


def test_stock_import_schedules_background_task(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured = _capture_tasks(monkeypatch)
    resp = client.post("/utilities/import/stock-prices", json={"period": "202601"})
    assert resp.status_code == 202
    assert captured[0][0] == "import_stock_prices"
    assert captured[0][1] == ("202601",)


def test_period_validation_rejects_bad_format(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _capture_tasks(monkeypatch)
    resp = client.post("/utilities/import/stock-prices", json={"period": "2026-01"})
    assert resp.status_code == 422


def test_period_empty_is_accepted(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured = _capture_tasks(monkeypatch)
    resp = client.post("/utilities/import/fx-rates", json={"period": ""})
    assert resp.status_code == 202
    assert captured[0][1] == ("",)
