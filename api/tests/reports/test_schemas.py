"""BE-025 — schema example smoke tests."""
from __future__ import annotations

from app.models.reports.asset_breakdown import AssetBreakdownRead, AssetShare
from app.models.reports.balance import (
    BalanceAssets,
    BalanceLiabilities,
    BalanceLine,
    BalanceSheetRead,
)
from app.models.reports.expenditure import ExpenditurePoint, ExpenditureTrendRead


def _has_example_and_field_docs(cls) -> None:
    js = cls.model_json_schema()
    assert "example" in js, cls.__name__
    for n, p in js["properties"].items():
        assert "description" in p, f"{cls.__name__}.{n}"


def test_balance_sheet_schema_example() -> None:
    for cls in (BalanceLine, BalanceAssets, BalanceLiabilities, BalanceSheetRead):
        _has_example_and_field_docs(cls)


def test_expenditure_schema_example() -> None:
    for cls in (ExpenditurePoint, ExpenditureTrendRead):
        _has_example_and_field_docs(cls)


def test_asset_breakdown_schema_example() -> None:
    for cls in (AssetShare, AssetBreakdownRead):
        _has_example_and_field_docs(cls)
