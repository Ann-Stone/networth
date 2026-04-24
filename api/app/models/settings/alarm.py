"""Alarm / reminder model and CRUD schemas (Settings domain)."""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


_ALARM_EXAMPLE = {
    "alarm_id": 1,
    "alarm_type": "credit-card-charge",
    "alarm_date": "20260115",
    "content": "Chase Sapphire autopay",
    "due_date": "20260120",
}


class Alarm(SQLModel, table=True):
    __tablename__ = "Alarm"

    alarm_id: int | None = Field(
        default=None, primary_key=True, description="Autoincrement PK", schema_extra={"examples": [1]}
    )
    alarm_type: str = Field(
        ..., description="Reminder category", schema_extra={"examples": ["credit-card-charge"]}
    )
    alarm_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20260115"]})
    content: str = Field(..., description="Free-form reminder text", schema_extra={"examples": ["Chase Sapphire autopay"]})
    due_date: str | None = Field(default=None, description="YYYYMMDD", schema_extra={"examples": ["20260120"]})

    model_config = ConfigDict(json_schema_extra={"example": _ALARM_EXAMPLE})


class AlarmCreate(SQLModel):
    alarm_type: str = Field(..., description="Reminder category", schema_extra={"examples": ["credit-card-charge"]})
    alarm_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20260115"]})
    content: str = Field(..., description="Reminder text", schema_extra={"examples": ["Chase Sapphire autopay"]})
    due_date: str | None = Field(default=None, description="YYYYMMDD", schema_extra={"examples": ["20260120"]})

    model_config = ConfigDict(json_schema_extra={"example": {k: v for k, v in _ALARM_EXAMPLE.items() if k != "alarm_id"}})


class AlarmUpdate(SQLModel):
    alarm_type: str | None = Field(default=None, description="Reminder category", schema_extra={"examples": ["credit-card-charge"]})
    alarm_date: str | None = Field(default=None, description="YYYYMMDD", schema_extra={"examples": ["20260115"]})
    content: str | None = Field(default=None, description="Reminder text", schema_extra={"examples": ["Updated text"]})
    due_date: str | None = Field(default=None, description="YYYYMMDD", schema_extra={"examples": ["20260125"]})

    model_config = ConfigDict(json_schema_extra={"example": {"content": "Updated text"}})


class AlarmRead(SQLModel):
    alarm_id: int = Field(..., description="Autoincrement PK", schema_extra={"examples": [1]})
    alarm_type: str = Field(..., description="Reminder category", schema_extra={"examples": ["credit-card-charge"]})
    alarm_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20260115"]})
    content: str = Field(..., description="Reminder text", schema_extra={"examples": ["Chase Sapphire autopay"]})
    due_date: str | None = Field(default=None, description="YYYYMMDD", schema_extra={"examples": ["20260120"]})

    model_config = ConfigDict(json_schema_extra={"example": _ALARM_EXAMPLE})
