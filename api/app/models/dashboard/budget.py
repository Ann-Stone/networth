"""Dashboard budget response schemas (BE-026)."""
from __future__ import annotations

from enum import Enum

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


class BudgetType(str, Enum):
    monthly = "monthly"
    yearly = "yearly"


class BudgetLine(SQLModel):
    category: str = Field(
        ..., description="Budget category code", schema_extra={"examples": ["Food"]}
    )
    planned: float = Field(..., description="Planned amount", schema_extra={"examples": [10000.0]})
    actual: float = Field(..., description="Actual spend", schema_extra={"examples": [8700.0]})
    usage_pct: float = Field(
        ...,
        description="actual / planned * 100, 0 when planned == 0",
        schema_extra={"examples": [87.0]},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"category": "Food", "planned": 10000.0, "actual": 8700.0, "usage_pct": 87.0}
        }
    )


class BudgetRead(SQLModel):
    type: BudgetType = Field(..., description="Aggregation granularity", schema_extra={"examples": ["monthly"]})
    period: str = Field(..., description="YYYYMM for monthly, YYYY for yearly", schema_extra={"examples": ["202403"]})
    lines: list[BudgetLine] = Field(..., description="Per-category rows", schema_extra={"examples": [[]]})
    total_planned: float = Field(..., description="Sum of planned across lines", schema_extra={"examples": [10000.0]})
    total_actual: float = Field(..., description="Sum of actual across lines", schema_extra={"examples": [8700.0]})

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "monthly",
                "period": "202403",
                "lines": [
                    {"category": "Food", "planned": 10000.0, "actual": 8700.0, "usage_pct": 87.0}
                ],
                "total_planned": 10000.0,
                "total_actual": 8700.0,
            }
        }
    )
