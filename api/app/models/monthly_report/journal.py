"""Journal (transaction) model and CRUD schemas (Monthly Report domain)."""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


_JOURNAL_EXAMPLE = {
    "distinct_number": 1,
    "vesting_month": "202604",
    "spend_date": "20260418",
    "spend_way": "BANK-CHASE-01",
    "spend_way_type": "account",
    "spend_way_table": "Account",
    "action_main": "EXP01",
    "action_main_type": "expense",
    "action_main_table": "Code_Data",
    "action_sub": None,
    "action_sub_type": None,
    "action_sub_table": None,
    "spending": -123.45,
    "invoice_number": None,
    "note": "Lunch",
}


class Journal(SQLModel, table=True):
    __tablename__ = "Journal"

    distinct_number: int | None = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"autoincrement": True},
        description="Autoincrement PK",
        schema_extra={"examples": [1]},
    )
    vesting_month: str = Field(..., description="YYYYMM", schema_extra={"examples": ["202604"]})
    spend_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20260418"]})
    spend_way: str = Field(..., description="Account or credit card id used for payment", schema_extra={"examples": ["BANK-CHASE-01"]})
    spend_way_type: str = Field(..., description="account / credit_card", schema_extra={"examples": ["account"]})
    spend_way_table: str = Field(..., description="Source table name of spend_way", schema_extra={"examples": ["Account"]})
    action_main: str = Field(..., description="Main code for classification", schema_extra={"examples": ["EXP01"]})
    action_main_type: str = Field(..., description="Main code type", schema_extra={"examples": ["expense"]})
    action_main_table: str = Field(..., description="Source table of action_main", schema_extra={"examples": ["Code_Data"]})
    action_sub: str | None = Field(default=None, description="Secondary code, if any", schema_extra={"examples": [None]})
    action_sub_type: str | None = Field(default=None, description="Secondary code type", schema_extra={"examples": [None]})
    action_sub_table: str | None = Field(default=None, description="Secondary code source table", schema_extra={"examples": [None]})
    spending: float = Field(..., description="Positive = income, negative = expense", schema_extra={"examples": [-123.45]})
    invoice_number: str | None = Field(default=None, description="Invoice number, populated by invoice CSV import", schema_extra={"examples": ["AB12345678"]})
    note: str | None = Field(default=None, description="Free-form note", schema_extra={"examples": ["Lunch"]})

    model_config = ConfigDict(json_schema_extra={"example": _JOURNAL_EXAMPLE})


class JournalCreate(SQLModel):
    vesting_month: str = Field(..., description="YYYYMM", schema_extra={"examples": ["202604"]})
    spend_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20260418"]})
    spend_way: str = Field(..., description="Payment source id", schema_extra={"examples": ["BANK-CHASE-01"]})
    spend_way_type: str = Field(..., description="account / credit_card", schema_extra={"examples": ["account"]})
    spend_way_table: str = Field(..., description="Source table of spend_way", schema_extra={"examples": ["Account"]})
    action_main: str = Field(..., description="Main code", schema_extra={"examples": ["EXP01"]})
    action_main_type: str = Field(..., description="Main code type", schema_extra={"examples": ["expense"]})
    action_main_table: str = Field(..., description="Source table of action_main", schema_extra={"examples": ["Code_Data"]})
    action_sub: str | None = Field(default=None, description="Secondary code", schema_extra={"examples": [None]})
    action_sub_type: str | None = Field(default=None, description="Secondary code type", schema_extra={"examples": [None]})
    action_sub_table: str | None = Field(default=None, description="Secondary code source table", schema_extra={"examples": [None]})
    spending: float = Field(..., description="Positive = income, negative = expense", schema_extra={"examples": [-123.45]})
    invoice_number: str | None = Field(default=None, description="Invoice number", schema_extra={"examples": ["AB12345678"]})
    note: str | None = Field(default=None, description="Free-form note", schema_extra={"examples": ["Lunch"]})

    model_config = ConfigDict(
        json_schema_extra={"example": {k: v for k, v in _JOURNAL_EXAMPLE.items() if k != "distinct_number"}}
    )


class JournalUpdate(SQLModel):
    vesting_month: str | None = Field(default=None, description="YYYYMM", schema_extra={"examples": ["202604"]})
    spend_date: str | None = Field(default=None, description="YYYYMMDD", schema_extra={"examples": ["20260418"]})
    spend_way: str | None = Field(default=None, description="Payment source id", schema_extra={"examples": ["BANK-CHASE-01"]})
    spend_way_type: str | None = Field(default=None, description="account / credit_card", schema_extra={"examples": ["account"]})
    spend_way_table: str | None = Field(default=None, description="Source table of spend_way", schema_extra={"examples": ["Account"]})
    action_main: str | None = Field(default=None, description="Main code", schema_extra={"examples": ["EXP01"]})
    action_main_type: str | None = Field(default=None, description="Main code type", schema_extra={"examples": ["expense"]})
    action_main_table: str | None = Field(default=None, description="Source table of action_main", schema_extra={"examples": ["Code_Data"]})
    action_sub: str | None = Field(default=None, description="Secondary code", schema_extra={"examples": [None]})
    action_sub_type: str | None = Field(default=None, description="Secondary code type", schema_extra={"examples": [None]})
    action_sub_table: str | None = Field(default=None, description="Secondary code source table", schema_extra={"examples": [None]})
    spending: float | None = Field(default=None, description="Signed amount", schema_extra={"examples": [-123.45]})
    invoice_number: str | None = Field(default=None, description="Invoice number", schema_extra={"examples": ["AB12345678"]})
    note: str | None = Field(default=None, description="Free-form note", schema_extra={"examples": ["Updated"]})

    model_config = ConfigDict(json_schema_extra={"example": {"note": "Updated note"}})


class JournalRead(SQLModel):
    distinct_number: int = Field(..., description="Autoincrement PK", schema_extra={"examples": [1]})
    vesting_month: str = Field(..., description="YYYYMM", schema_extra={"examples": ["202604"]})
    spend_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20260418"]})
    spend_way: str = Field(..., description="Payment source id", schema_extra={"examples": ["BANK-CHASE-01"]})
    spend_way_type: str = Field(..., description="account / credit_card", schema_extra={"examples": ["account"]})
    spend_way_table: str = Field(..., description="Source table of spend_way", schema_extra={"examples": ["Account"]})
    action_main: str = Field(..., description="Main code", schema_extra={"examples": ["EXP01"]})
    action_main_type: str = Field(..., description="Main code type", schema_extra={"examples": ["expense"]})
    action_main_table: str = Field(..., description="Source table of action_main", schema_extra={"examples": ["Code_Data"]})
    action_sub: str | None = Field(default=None, description="Secondary code", schema_extra={"examples": [None]})
    action_sub_type: str | None = Field(default=None, description="Secondary code type", schema_extra={"examples": [None]})
    action_sub_table: str | None = Field(default=None, description="Secondary code source table", schema_extra={"examples": [None]})
    spending: float = Field(..., description="Signed amount", schema_extra={"examples": [-123.45]})
    invoice_number: str | None = Field(default=None, description="Invoice number", schema_extra={"examples": ["AB12345678"]})
    note: str | None = Field(default=None, description="Free-form note", schema_extra={"examples": ["Lunch"]})

    model_config = ConfigDict(json_schema_extra={"example": _JOURNAL_EXAMPLE})
