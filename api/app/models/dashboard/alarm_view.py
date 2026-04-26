"""Alarm response schema for dashboard view (BE-028)."""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


class AlarmItem(SQLModel):
    date: str = Field(
        ...,
        description="Display date: MM/DD for monthly-recurring, raw alarm_date otherwise",
        schema_extra={"examples": ["05/15"]},
    )
    content: str = Field(
        ..., description="Alarm content", schema_extra={"examples": ["Pay credit card bill"]}
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"date": "05/15", "content": "Pay credit card bill"}}
    )
