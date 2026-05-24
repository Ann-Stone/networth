"""Composite payloads that write a Journal row together with an asset detail row.

Used by ``POST /monthly-report/journals/stock-transaction`` to record a single
real-world event (e.g. "bought 10 shares of AAPL") as one atomic transaction
spanning the ``Journal`` and ``Stock_Detail`` tables.

The two writes succeed or fail together; on any error the surrounding session
is rolled back by FastAPI's dependency teardown.
"""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

from app.models.assets.stock import StockDetailRead, StockExcuteType
from app.models.monthly_report.journal import JournalCreate, JournalRead, JournalUpdate


_STOCK_TRANSACTION_DETAIL_EXAMPLE = {
    "stock_id": "STK-H-001",
    "excute_type": "buy",
    "excute_amount": 10.0,
    "excute_date": "20260418",
    "memo": "First lot",
}


class StockTransactionDetailCreate(SQLModel):
    """Stock_Detail subset accepted by the composite endpoint.

    ``excute_price`` is intentionally absent: the service copies
    ``journal.spending`` into it verbatim (sign preserved — a buy/outflow
    journal is negative, so the detail's price is negative too).
    ``account_id``/``account_name`` are also absent: they are resolved from
    ``journal.spend_way`` by the service so the two rows stay in sync.

    ``excute_amount`` defaults to 0.0 so cash dividends (no share count)
    can omit it; stock splits / stock dividends can keep amount and rely on
    ``journal.spending`` being 0 to imply ``excute_price = 0``.
    """

    stock_id: str = Field(
        ...,
        description="Existing StockJournal.stock_id this transaction belongs to.",
        schema_extra={"examples": ["STK-H-001"]},
    )
    excute_type: StockExcuteType = Field(
        ...,
        description="buy / sell / stock (split or stock dividend) / cash (cash dividend)",
        schema_extra={"examples": ["buy"]},
    )
    excute_amount: float = Field(
        default=0.0,
        description=(
            "Quantity traded (shares). Defaults to 0 so cash dividends "
            "(excute_type='cash') can omit it."
        ),
        schema_extra={"examples": [10.0]},
    )
    excute_date: str | None = Field(
        default=None,
        description="YYYYMMDD; defaults to journal.spend_date when omitted.",
        schema_extra={"examples": ["20260418"]},
    )
    memo: str | None = Field(
        default=None,
        description="Free-form memo; defaults to journal.note when omitted.",
        schema_extra={"examples": ["First lot"]},
    )

    model_config = ConfigDict(
        json_schema_extra={"example": _STOCK_TRANSACTION_DETAIL_EXAMPLE}
    )


class JournalStockTransactionCreate(SQLModel):
    """Composite payload: Journal + Stock_Detail written atomically."""

    journal: JournalCreate = Field(..., description="Journal row to insert.")
    stock_detail: StockTransactionDetailCreate = Field(
        ..., description="Stock detail row derived from + linked to the journal."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "journal": {
                    "vesting_month": "202604",
                    "spend_date": "20260418",
                    "spend_way": "BANK-CHASE-01",
                    "spend_way_type": "account",
                    "spend_way_table": "Account",
                    "action_main": "INV01",
                    "action_main_type": "Invest",
                    "action_main_table": "Code_Data",
                    "action_sub": None,
                    "action_sub_type": None,
                    "action_sub_table": None,
                    "spending": -1805.0,
                    "invoice_number": None,
                    "note": "Buy AAPL",
                },
                "stock_detail": _STOCK_TRANSACTION_DETAIL_EXAMPLE,
            }
        }
    )


class JournalStockTransactionUpdate(SQLModel):
    """Composite payload for editing a Journal while creating its first Stock_Detail.

    Used when a user edits a previously-untagged journal and now classifies it
    as a stock transaction (e.g. correcting an imported bank entry). The Journal
    is updated in place; the Stock_Detail is always created fresh — partial
    edits of existing details belong on the independent Stock_Detail endpoints.
    """

    journal: JournalUpdate = Field(..., description="Journal fields to update.")
    stock_detail: StockTransactionDetailCreate = Field(
        ..., description="Stock detail row to insert alongside the update."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "journal": {
                    "action_main": "TRA",
                    "action_main_type": "Transfer",
                    "action_main_table": "Code_Data",
                    "action_sub": "Stock",
                    "action_sub_type": "Asset",
                    "action_sub_table": "Stock_Detail",
                    "note": "Re-classified as stock purchase",
                },
                "stock_detail": _STOCK_TRANSACTION_DETAIL_EXAMPLE,
            }
        }
    )


class JournalStockTransactionRead(SQLModel):
    """Response body for the composite endpoint."""

    journal: JournalRead = Field(..., description="Persisted journal row.")
    stock_detail: StockDetailRead = Field(..., description="Persisted stock detail row.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "journal": {
                    "distinct_number": 42,
                    "vesting_month": "202604",
                    "spend_date": "20260418",
                    "spend_way": "BANK-CHASE-01",
                    "spend_way_type": "account",
                    "spend_way_table": "Account",
                    "action_main": "INV01",
                    "action_main_type": "Invest",
                    "action_main_table": "Code_Data",
                    "action_sub": None,
                    "action_sub_type": None,
                    "action_sub_table": None,
                    "spending": -1805.0,
                    "invoice_number": None,
                    "note": "Buy AAPL",
                },
                "stock_detail": {
                    "distinct_number": 17,
                    "stock_id": "STK-H-001",
                    "excute_type": "buy",
                    "excute_amount": 10.0,
                    "excute_price": -1805.0,
                    "excute_date": "20260418",
                    "account_id": "BANK-CHASE-01",
                    "account_name": "Chase Checking",
                    "memo": "First lot",
                },
            }
        }
    )
