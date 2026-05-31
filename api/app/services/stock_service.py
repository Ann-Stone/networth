"""Stock service: month close-price selection, holdings projection, manual/yfinance insert.

Used by the BE-018 stock-price endpoints and reused by the BE-019 stock
settlement step.
"""
from __future__ import annotations

import time

from sqlmodel import Session, select

from app.models.assets.stock import StockJournal
from app.models.dashboard.stock_price_history import StockPriceHistory
from app.models.monthly_report.stock_price import (
    StockPriceCreate,
    StockPriceMonthRead,
)


def _month_end(vesting_month: str) -> str:
    return f"{vesting_month}31"


def _month_start(vesting_month: str) -> str:
    return f"{vesting_month}01"


def select_in_month_close_price(
    session: Session, stock_code: str, vesting_month: str
) -> StockPriceHistory | None:
    """Pick the most recent ``StockPriceHistory`` row *within* the requested month.

    Unlike :func:`select_month_close_price`, this never falls back to prior
    months. Returns ``None`` when the month itself has no price row, so callers
    can surface a blank and know a fetch is needed.
    """
    stmt = (
        select(StockPriceHistory)
        .where(StockPriceHistory.stock_code == stock_code)
        .where(StockPriceHistory.fetch_date >= _month_start(vesting_month))
        .where(StockPriceHistory.fetch_date <= _month_end(vesting_month))
        .order_by(StockPriceHistory.fetch_date.desc())
    )
    return session.exec(stmt).first()


def select_month_close_price(
    session: Session, stock_code: str, vesting_month: str
) -> StockPriceHistory | None:
    """Pick the most recent ``StockPriceHistory`` row for a ticker on or before month-end.

    If the month has no row, fall back to the most recent prior row. Returns
    ``None`` only when no row at all exists for that ticker.
    """
    in_month = (
        select(StockPriceHistory)
        .where(StockPriceHistory.stock_code == stock_code)
        .where(StockPriceHistory.fetch_date <= _month_end(vesting_month))
        .order_by(StockPriceHistory.fetch_date.desc())
    )
    row = session.exec(in_month).first()
    if row is not None:
        return row
    fallback = (
        select(StockPriceHistory)
        .where(StockPriceHistory.stock_code == stock_code)
        .order_by(StockPriceHistory.fetch_date.desc())
    )
    return session.exec(fallback).first()


def list_month_stock_prices(
    session: Session, vesting_month: str
) -> list[StockPriceMonthRead]:
    """Return each held stock's in-month close price for the requested month.

    The price window is strictly the requested month: only a row whose
    ``fetch_date`` falls within ``{vesting_month}01``..``{vesting_month}31`` is
    used (no fallback to prior months). When the month has no row for a holding
    the row is still emitted with ``close_price`` / ``fetch_date`` set to
    ``None`` — that blank tells the caller to fetch a fresh price for that month.
    """
    holdings = list(session.exec(select(StockJournal)).all())
    out: list[StockPriceMonthRead] = []
    for h in holdings:
        price = select_in_month_close_price(session, h.stock_code, vesting_month)
        out.append(
            StockPriceMonthRead(
                stock_code=h.stock_code,
                stock_name=h.stock_name,
                close_price=price.close_price if price is not None else None,
                fetch_date=price.fetch_date if price is not None else None,
            )
        )
    return out


def fetch_yfinance_price(stock_code: str, fetch_date: str) -> float:
    """Fetch the close price for ``stock_code`` on ``fetch_date`` (YYYYMMDD).

    Retries up to 3 times with exponential backoff. Raises ``RuntimeError``
    after all retries are exhausted.
    """
    import yfinance  # local import; mocked in tests

    last_exc: Exception | None = None
    for attempt in range(3):
        try:
            ticker = yfinance.Ticker(stock_code)
            iso = f"{fetch_date[:4]}-{fetch_date[4:6]}-{fetch_date[6:8]}"
            history = ticker.history(start=iso, end=iso, interval="1d")
            if history is None or len(history) == 0:
                raise RuntimeError(f"No yfinance data for {stock_code} on {fetch_date}")
            close = float(history["Close"].iloc[-1])
            return close
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            time.sleep(0.1 * (2 ** attempt))
    raise RuntimeError(f"yfinance fetch failed for {stock_code}: {last_exc}")


def insert_stock_price(
    session: Session, payload: StockPriceCreate
) -> StockPriceHistory:
    """Persist a ``StockPriceHistory`` row, optionally overwriting close via yfinance."""
    from fastapi import HTTPException

    data = payload.model_dump()
    trigger = data.pop("trigger_yfinance", False)
    if trigger:
        try:
            data["close_price"] = fetch_yfinance_price(
                data["stock_code"], data["fetch_date"]
            )
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=502, detail=f"yfinance fetch failed: {exc}")
    row = StockPriceHistory(**data)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row
