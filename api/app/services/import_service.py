"""Background-task workers for stock-price, FX-rate, and invoice imports.

All workers create their own `Session(engine)` per `api/CLAUDE.md §6` — they
must not reuse the request session. Failures are logged and never raise.
"""
from __future__ import annotations

import csv
import json
import logging
import random
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable

from sqlmodel import Session, select

from app.config import settings
from app.database import engine
from app.models.assets.stock import StockJournal
from app.models.dashboard.fx_rate import FXRate
from app.models.dashboard.stock_price_history import StockPriceHistory
from app.models.monthly_report.journal import Journal
from app.models.settings.credit_card import CreditCard
from app.models.utilities.imports import InvoiceImportError, InvoiceImportResult

logger = logging.getLogger(__name__)


# ---------- Config loaders ----------


def load_invoice_skip_list(path: str) -> list[str]:
    p = Path(path)
    if not p.exists():
        logger.warning("Invoice skip list not found: %s", path)
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [str(x) for x in data]
        logger.error("Invoice skip list must be a JSON array: %s", path)
        return []
    except json.JSONDecodeError as e:
        logger.error("Invoice skip list invalid JSON (%s): %s", path, e)
        return []


def load_merchant_mapping(path: str) -> dict[str, str]:
    p = Path(path)
    if not p.exists():
        logger.warning("Merchant mapping not found: %s", path)
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return {str(k): str(v) for k, v in data.items()}
        logger.error("Merchant mapping must be a JSON object: %s", path)
        return {}
    except json.JSONDecodeError as e:
        logger.error("Merchant mapping invalid JSON (%s): %s", path, e)
        return {}


# ---------- Period helpers ----------


def _period_to_last_day(period: str) -> str:
    """Return YYYYMMDD of the last day of the requested YYYYMM, or today."""
    if not period:
        return date.today().strftime("%Y%m%d")
    base = datetime.strptime(period, "%Y%m").replace(day=28) + timedelta(days=4)
    last = base - timedelta(days=base.day)
    return last.strftime("%Y%m%d")


def _yfinance_ticker(stock_code: str) -> str:
    """Heuristic: digits-only codes are TW listed → append .TW; others as-is.

    StockJournal does not store vesting_nation; this heuristic mirrors the
    legacy behavior in `globalRouter.py` which treated TW codes by suffix.
    """
    return f"{stock_code}.TW" if stock_code.isdigit() else stock_code


# ---------- Stock price import ----------


def _fetch_one_stock_price(session: Session, stock_code: str, fetch_date: str) -> bool:
    """Fetch + upsert a single ticker. Return True if a row was inserted/updated."""
    try:
        import yfinance as yf  # imported lazily to keep test startup fast
    except ImportError:  # pragma: no cover
        logger.error("yfinance is required for import_stock_prices")
        return False

    ticker = _yfinance_ticker(stock_code)
    delay = 1.0
    for attempt in range(3):
        try:
            data = yf.download(ticker, period="1d", progress=False)
            break
        except Exception as e:  # noqa: BLE001 — third-party flake
            msg = str(e)
            if "404" in msg:
                logger.warning("Stock 404, skipping: %s", ticker)
                return False
            if "429" in msg and attempt < 2:
                sleep_for = 2**attempt + random.uniform(1, 3)
                logger.warning("429 on %s, retry %d in %.1fs", ticker, attempt + 1, sleep_for)
                time.sleep(sleep_for)
                continue
            logger.error("Stock fetch failed for %s: %s", ticker, e)
            return False
    else:  # pragma: no cover — exhausted retries
        return False

    if data is None or len(data) == 0:
        return False
    row = data.iloc[-1]
    open_p = float(row["Open"]) if "Open" in row else 0.0
    high_p = float(row["High"]) if "High" in row else 0.0
    low_p = float(row["Low"]) if "Low" in row else 0.0
    close_p = float(row["Close"]) if "Close" in row else 0.0

    existing = session.exec(
        select(StockPriceHistory).where(
            StockPriceHistory.stock_code == stock_code,
            StockPriceHistory.fetch_date == fetch_date,
        )
    ).first()
    if existing is not None:
        existing.open_price = open_p
        existing.highest_price = high_p
        existing.lowest_price = low_p
        existing.close_price = close_p
        session.add(existing)
    else:
        session.add(
            StockPriceHistory(
                stock_code=stock_code,
                fetch_date=fetch_date,
                open_price=open_p,
                highest_price=high_p,
                lowest_price=low_p,
                close_price=close_p,
            )
        )
    session.commit()
    return True


def import_stock_prices(period: str) -> None:
    """Background worker: fetch + upsert daily prices for every distinct ticker."""
    fetch_date = _period_to_last_day(period)
    with Session(engine) as session:
        codes = list(
            {row.stock_code for row in session.exec(select(StockJournal)).all()}
        )
        for i, stock_code in enumerate(sorted(codes), start=1):
            try:
                _fetch_one_stock_price(session, stock_code, fetch_date)
            except Exception as e:  # noqa: BLE001
                logger.error("Unexpected stock import error for %s: %s", stock_code, e)
            if i % 10 == 0:
                time.sleep(3)


# ---------- FX rate import ----------


def _sinopac_url() -> str:
    ts = int(time.time() * 1000)
    return (
        "https://mma.sinopac.com/ws/share/rate/ws_exchange.ashx"
        f"?exchangeType=REMIT&_={ts}"
    )


def _upsert_fx(session: Session, import_date: str, code: str, buy_rate: float) -> None:
    existing = session.exec(
        select(FXRate).where(FXRate.import_date == import_date, FXRate.code == code)
    ).first()
    if existing is not None:
        existing.buy_rate = buy_rate
        session.add(existing)
    else:
        session.add(FXRate(import_date=import_date, code=code, buy_rate=buy_rate))


def import_fx_rates(period: str) -> None:
    """Background worker: fetch FX rates from Sinopac and upsert into FXRate."""
    import_date = _period_to_last_day(period)
    try:
        import httpx

        with httpx.Client(verify=False, timeout=30.0) as cli:
            resp = cli.get(_sinopac_url())
            resp.raise_for_status()
            payload = resp.json()
    except Exception as e:  # noqa: BLE001
        logger.error("FX rate fetch failed: %s", e)
        return

    sub_info: Iterable[dict] = payload.get("SubInfo", []) or []
    with Session(engine) as session:
        for entry in sub_info:
            code = entry.get("DataValue4")
            buy_raw = entry.get("DataValue2")
            if not code or buy_raw in (None, ""):
                continue
            try:
                buy_rate = float(buy_raw)
            except (TypeError, ValueError):
                continue
            _upsert_fx(session, import_date, code, buy_rate)
        session.commit()


# ---------- Invoice CSV import ----------


def _match_merchant(shop_name: str, mapping: dict[str, str]) -> str | None:
    """Case-insensitive substring match; first match wins (insertion order)."""
    if not shop_name:
        return None
    haystack = shop_name.lower()
    for keyword, target in mapping.items():
        if keyword and keyword.lower() in haystack:
            return target
    return None


def _append_error_log(message: str) -> None:
    log_path = Path(settings.invoice_error_log)
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as fp:
            fp.write(message + "\n")
    except OSError as e:
        logger.error("Cannot write invoice error log: %s", e)


def import_invoices(period: str) -> InvoiceImportResult:
    """Background worker: import an invoice CSV into Journal."""
    skip_list = load_invoice_skip_list(settings.invoice_skip_path)
    mapping = load_merchant_mapping(settings.merchant_mapping_path)
    csv_path = Path(settings.import_csv)
    if not csv_path.exists():
        _append_error_log(f"invoice.csv missing at {csv_path}")
        return InvoiceImportResult(
            imported=0,
            skipped=0,
            failed=0,
            errors=[InvoiceImportError(line=0, reason="invoice.csv missing")],
        )

    imported = 0
    skipped = 0
    failed = 0
    errors: list[InvoiceImportError] = []
    pending_items: dict[str, list[str]] = {}

    with Session(engine) as session:
        cards = session.exec(select(CreditCard)).all()
        # Map last-4-digits of card_no → CreditCard for a best-effort carrier
        # match. CreditCard.carrier_no was dropped per README Decision Log;
        # this is a best-effort fallback.
        card_by_last4: dict[str, CreditCard] = {}
        for c in cards:
            if c.card_no:
                tail = "".join(ch for ch in c.card_no if ch.isdigit())[-4:]
                if tail:
                    card_by_last4[tail] = c

        try:
            with csv_path.open("r", encoding="utf-8", newline="") as fp:
                reader = csv.reader(fp, delimiter="|")
                m_rows: list[tuple[int, list[str]]] = []
                for line_no, row in enumerate(reader, start=1):
                    if not row:
                        continue
                    kind = row[0].strip() if row else ""
                    if kind == "M":
                        m_rows.append((line_no, row))
                    elif kind == "D" and len(row) >= 4:
                        inv = row[1].strip()
                        pending_items.setdefault(inv, []).append(row[3].strip())

                for line_no, row in m_rows:
                    try:
                        if len(row) < 8:
                            raise ValueError("M-row missing columns")
                        carrier_no = row[2].strip()
                        invoice_date = row[3].strip()
                        shop_name = row[5].strip() if len(row) > 5 else ""
                        invoice_number = row[6].strip() if len(row) > 6 else ""
                        amount = int(row[7]) * -1
                        vesting_month = invoice_date[:6]
                        if not vesting_month or len(vesting_month) != 6:
                            raise ValueError("invoice_date missing")
                        if period and vesting_month != period:
                            continue
                        if carrier_no in skip_list:
                            skipped += 1
                            continue
                        existing = session.exec(
                            select(Journal).where(
                                Journal.invoice_number == invoice_number,
                                Journal.vesting_month == vesting_month,
                            )
                        ).first()
                        if existing is not None:
                            skipped += 1
                            continue

                        spend_way = ""
                        spend_way_type = ""
                        spend_way_table = ""
                        carrier_tail = "".join(
                            ch for ch in carrier_no if ch.isdigit()
                        )[-4:]
                        card = card_by_last4.get(carrier_tail) if carrier_tail else None
                        if card is not None:
                            spend_way = card.credit_card_id
                            spend_way_type = "credit_card"
                            spend_way_table = "Credit_Card"

                        action_main = _match_merchant(shop_name, mapping) or ""
                        item_names = pending_items.get(invoice_number, [])
                        note = ", ".join(filter(None, item_names)) or shop_name

                        journal = Journal(
                            vesting_month=vesting_month,
                            spend_date=invoice_date,
                            spend_way=spend_way,
                            spend_way_type=spend_way_type,
                            spend_way_table=spend_way_table,
                            action_main=action_main,
                            action_main_type="Floating" if action_main else "",
                            action_main_table="Code_Data",
                            action_sub=None,
                            action_sub_type=None,
                            action_sub_table=None,
                            spending=float(amount),
                            invoice_number=invoice_number or None,
                            note=note or None,
                        )
                        session.add(journal)
                        imported += 1
                    except Exception as e:  # noqa: BLE001
                        failed += 1
                        errors.append(InvoiceImportError(line=line_no, reason=str(e)))
                        _append_error_log(f"line {line_no}: {e}")
                session.commit()
        except OSError as e:
            _append_error_log(f"invoice.csv read failed: {e}")
            return InvoiceImportResult(
                imported=imported,
                skipped=skipped,
                failed=failed + 1,
                errors=[*errors, InvoiceImportError(line=0, reason=str(e))],
            )

    return InvoiceImportResult(
        imported=imported, skipped=skipped, failed=failed, errors=errors
    )
