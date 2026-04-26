"""Dashboard summary response schemas (BE-026)."""
from __future__ import annotations

from enum import Enum

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


class SummaryType(str, Enum):
    spending = "spending"
    freedom_ratio = "freedom_ratio"
    asset_debt_trend = "asset_debt_trend"


class SummaryPoint(SQLModel):
    period: str = Field(..., description="YYYYMM", schema_extra={"examples": ["202403"]})
    value: float = Field(..., description="Aggregated value for the period", schema_extra={"examples": [12345.67]})

    model_config = ConfigDict(json_schema_extra={"example": {"period": "202403", "value": 12345.67}})


class SummaryRead(SQLModel):
    type: SummaryType = Field(
        ..., description="Summary variant", schema_extra={"examples": ["spending"]}
    )
    points: list[SummaryPoint] = Field(
        ..., description="Time series, oldest first", schema_extra={"examples": [[]]}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "spending",
                "points": [
                    {"period": "202301", "value": 32000.0},
                    {"period": "202302", "value": 41000.0},
                ],
            }
        }
    )
