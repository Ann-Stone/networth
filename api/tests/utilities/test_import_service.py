"""Service-layer tests for import_service."""
from __future__ import annotations

from pathlib import Path

import pytest
from sqlmodel import Session, select

import app.services.import_service as svc
from app.models.dashboard.fx_rate import FXRate
from app.models.dashboard.stock_price_history import StockPriceHistory
from app.models.assets.stock import StockJournal
from app.models.monthly_report.journal import Journal


# ---------- Config loaders ----------


def test_load_config_files_missing_tolerated(tmp_path: Path) -> None:
    assert svc.load_invoice_skip_list(str(tmp_path / "missing.json")) == []
    assert svc.load_merchant_mapping(str(tmp_path / "missing.json")) == {}


def test_load_config_files_invalid_json(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("not json", encoding="utf-8")
    assert svc.load_invoice_skip_list(str(bad)) == []
    assert svc.load_merchant_mapping(str(bad)) == {}


def test_load_config_files_happy(tmp_path: Path) -> None:
    skip = tmp_path / "skip.json"
    skip.write_text('["A", "B"]', encoding="utf-8")
    assert svc.load_invoice_skip_list(str(skip)) == ["A", "B"]

    mapping = tmp_path / "map.json"
    mapping.write_text('{"foo": "bar"}', encoding="utf-8")
    assert svc.load_merchant_mapping(str(mapping)) == {"foo": "bar"}


# ---------- Period helpers ----------


def test_period_to_last_day_known_month() -> None:
    assert svc._period_to_last_day("202602") == "20260228"
    assert svc._period_to_last_day("202601") == "20260131"


def test_period_to_last_day_empty_uses_today() -> None:
    out = svc._period_to_last_day("")
    assert len(out) == 8 and out.isdigit()


def test_yfinance_ticker_heuristic() -> None:
    assert svc._yfinance_ticker("2330") == "2330.TW"
    assert svc._yfinance_ticker("AAPL") == "AAPL"


# ---------- Stock price import ----------


class _FakeRow(dict):
    def __getitem__(self, key):
        return super().__getitem__(key)

    def __contains__(self, key) -> bool:
        return super().__contains__(key)


class _FakeFrame:
    def __init__(self, rows: list[dict]):
        self._rows = rows

    def __len__(self):
        return len(self._rows)

    @property
    def iloc(self):
        rows = self._rows

        class _Iloc:
            def __getitem__(self, idx):
                return _FakeRow(rows[idx])

        return _Iloc()


def _patch_yfinance(monkeypatch, frame):
    class _Yf:
        @staticmethod
        def download(*args, **kwargs):
            return frame

    monkeypatch.setitem(__import__("sys").modules, "yfinance", _Yf)


def test_import_stock_prices_upserts_and_skips_duplicates(
    session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    session.add(
        StockJournal(
            stock_id="STK1",
            stock_code="AAPL",
            stock_name="Apple",
            asset_id="AS1",
            expected_spend=0.0,
        )
    )
    session.commit()

    frame = _FakeFrame(
        [{"Open": 100.0, "High": 105.0, "Low": 95.0, "Close": 102.0}]
    )
    _patch_yfinance(monkeypatch, frame)

    # Worker creates its own session(engine); patch the engine to ours.
    engine = session.get_bind()
    monkeypatch.setattr(svc, "engine", engine)

    svc.import_stock_prices("202601")
    fetch_date = svc._period_to_last_day("202601")
    rows = session.exec(
        select(StockPriceHistory).where(StockPriceHistory.stock_code == "AAPL")
    ).all()
    assert len(rows) == 1
    assert rows[0].close_price == 102.0
    assert rows[0].fetch_date == fetch_date

    # Re-run with new prices: idempotent upsert (still 1 row, updated values).
    frame2 = _FakeFrame(
        [{"Open": 110.0, "High": 115.0, "Low": 105.0, "Close": 112.0}]
    )
    _patch_yfinance(monkeypatch, frame2)
    svc.import_stock_prices("202601")
    session.expire_all()
    rows = session.exec(
        select(StockPriceHistory).where(StockPriceHistory.stock_code == "AAPL")
    ).all()
    assert len(rows) == 1
    assert rows[0].close_price == 112.0


# ---------- FX rate import ----------


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


class _FakeClient:
    def __init__(self, payload):
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def get(self, url):
        return _FakeResponse(self._payload)


def test_import_fx_rates_idempotent(
    session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    payload = {
        "SubInfo": [
            {"DataValue4": "USD", "DataValue2": "31.50"},
            {"DataValue4": "JPY", "DataValue2": "0.21"},
            {"DataValue4": "BAD", "DataValue2": ""},
        ]
    }
    import httpx

    monkeypatch.setattr(httpx, "Client", lambda **kw: _FakeClient(payload))

    engine = session.get_bind()
    monkeypatch.setattr(svc, "engine", engine)

    svc.import_fx_rates("202601")
    rows = session.exec(select(FXRate)).all()
    assert {(r.code, r.buy_rate) for r in rows} == {("USD", 31.5), ("JPY", 0.21)}

    # Re-run; counts unchanged.
    svc.import_fx_rates("202601")
    rows = session.exec(select(FXRate)).all()
    assert len(rows) == 2


def test_fx_upsert_is_idempotent(session: Session) -> None:
    svc._upsert_fx(session, "20260131", "USD", 31.5)
    session.commit()
    svc._upsert_fx(session, "20260131", "USD", 31.6)
    session.commit()
    rows = session.exec(select(FXRate)).all()
    assert len(rows) == 1
    assert rows[0].buy_rate == 31.6


# ---------- Invoice CSV import ----------


def _invoice_csv(rows: list[list[str]]) -> str:
    return "\n".join("|".join(r) for r in rows) + "\n"


def _configure_invoice_paths(monkeypatch, skip_path, map_path, log_path):
    # Patch the settings object that import_service holds a reference to.
    live = svc.settings

    monkeypatch.setattr(live, "invoice_skip_path", str(skip_path))
    monkeypatch.setattr(live, "merchant_mapping_path", str(map_path))
    monkeypatch.setattr(live, "invoice_error_log", str(log_path))


def test_import_invoices_partial_success_and_dedup(
    session: Session, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    skip_path = tmp_path / "skip.json"
    map_path = tmp_path / "map.json"
    log_path = tmp_path / "logs" / "errors.log"
    skip_path.write_text('["SKIPME"]', encoding="utf-8")
    map_path.write_text('{"Coffee": "FOOD-01"}', encoding="utf-8")
    _configure_invoice_paths(monkeypatch, skip_path, map_path, log_path)

    engine = session.get_bind()
    monkeypatch.setattr(svc, "engine", engine)

    rows = [
        # (M, carrier_name, carrier_no, invoice_date, shop_id, shop_name, invoice_number, total)
        ["M", "Carrier", "CAR1", "20260105", "S1", "Coffee Shop", "INV-1", "150", "OK", ""],
        ["D", "INV-1", "150", "Latte", ""],
        # malformed (amount) → failed
        ["M", "Carrier", "CAR1", "20260106", "S1", "Bad Shop", "INV-2", "abc", "OK", ""],
        # in skip-list → skipped
        ["M", "Carrier", "SKIPME", "20260107", "S1", "Skipped", "INV-3", "100", "OK", ""],
        # a different month — now imported too, since the period filter is gone
        ["M", "Carrier", "CAR1", "20260205", "S1", "Other", "INV-4", "200", "OK", ""],
    ]
    content = _invoice_csv(rows)

    result = svc.import_invoices(content)
    assert result.imported == 2  # INV-1 + INV-4
    assert result.skipped == 1  # SKIPME
    assert result.failed == 1  # INV-2 bad amount
    assert any(e.line == 3 for e in result.errors)

    # Per-month breakdown: INV-1 imported + INV-3 skip-list in 202601, INV-4 in
    # 202602. INV-2 failed before vesting_month was derived, so it's omitted.
    months = {m.month: m for m in result.months}
    assert set(months) == {"202601", "202602"}
    assert (months["202601"].imported, months["202601"].skipped) == (1, 1)
    assert (months["202602"].imported, months["202602"].skipped) == (1, 0)

    # Re-run: previously-imported INV-1 + INV-4 now dedup → skipped goes up.
    result2 = svc.import_invoices(content)
    assert result2.imported == 0
    assert result2.skipped == 3  # INV-1 dedup + INV-4 dedup + SKIPME
    months2 = {m.month: m for m in result2.months}
    assert (months2["202601"].imported, months2["202601"].skipped) == (0, 2)
    assert (months2["202602"].imported, months2["202602"].skipped) == (0, 1)

    journals = session.exec(select(Journal)).all()
    assert len(journals) == 2
    inv1 = next(j for j in journals if j.invoice_number == "INV-1")
    assert inv1.action_main == "FOOD-01"
    assert "Latte" in (inv1.note or "")


def test_import_invoices_empty_content(
    session: Session, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    skip_path = tmp_path / "skip.json"
    map_path = tmp_path / "map.json"
    log_path = tmp_path / "logs" / "errors.log"
    skip_path.write_text("[]", encoding="utf-8")
    map_path.write_text("{}", encoding="utf-8")
    _configure_invoice_paths(monkeypatch, skip_path, map_path, log_path)

    engine = session.get_bind()
    monkeypatch.setattr(svc, "engine", engine)

    result = svc.import_invoices("")
    assert result.imported == 0
    assert result.skipped == 0
    assert result.failed == 0
    assert result.months == []
    assert result.errors == []


def test_invoice_dedup_and_partial_success(
    session: Session, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Alias for the granular spec's named assertion (spec sub-task 9)."""
    test_import_invoices_partial_success_and_dedup(session, monkeypatch, tmp_path)
