"""Cash-flow statement (現金流量表) response schemas — Reports domain.

Personal cash flow split into three activities, mirroring the standard statement:
operating (生活: income − living expenses − loan interest), investing (投資:
buy/sell of holdings), financing (債務: loan principal repayment / new borrowing).
Self-transfers are excluded (net-zero); credit-card spend is counted once as an
operating outflow and never re-counted at settlement. All amounts are
FX-converted and signed (positive = cash in, negative = cash out).
"""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

_ITEM_EXAMPLE = {"label": "收入", "amount": 960000.0}


class CashFlowItem(SQLModel):
    label: str = Field(..., description="Component label", schema_extra={"examples": ["收入"]})
    amount: float = Field(
        ...,
        description="Signed cash flow (positive = in, negative = out)",
        schema_extra={"examples": [960000.0]},
    )

    model_config = ConfigDict(json_schema_extra={"example": _ITEM_EXAMPLE})


_ACTIVITY_EXAMPLE = {
    "key": "operating",
    "label": "生活",
    "net": 444000.0,
    "items": [_ITEM_EXAMPLE, {"label": "生活支出", "amount": -516000.0}],
}


class CashFlowActivity(SQLModel):
    key: str = Field(
        ..., description="operating | investing | financing", schema_extra={"examples": ["operating"]}
    )
    label: str = Field(
        ..., description="Display label: 生活 / 投資 / 債務", schema_extra={"examples": ["生活"]}
    )
    net: float = Field(
        ..., description="Signed net cash flow for the activity", schema_extra={"examples": [444000.0]}
    )
    items: list[CashFlowItem] = Field(
        ..., description="Signed sub-components", schema_extra={"examples": [[_ITEM_EXAMPLE]]}
    )

    model_config = ConfigDict(json_schema_extra={"example": _ACTIVITY_EXAMPLE})


class CashFlowRead(SQLModel):
    activities: list[CashFlowActivity] = Field(
        ...,
        description="[operating, investing, financing] in order",
        schema_extra={"examples": [[_ACTIVITY_EXAMPLE]]},
    )
    net_change: float = Field(
        ...,
        description="Sum of the three activities' net flows (overall change in cash)",
        schema_extra={"examples": [123000.0]},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"activities": [_ACTIVITY_EXAMPLE], "net_change": 123000.0}
        }
    )
