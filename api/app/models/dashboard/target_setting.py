"""TargetSetting model — annual target value tracker."""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


_EXAMPLE = {
    "distinct_number": "T-2026-01",
    "target_year": "2026",
    "setting_value": 1000000.0,
    "is_done": "N",
}


class TargetSetting(SQLModel, table=True):
    __tablename__ = "Target_Setting"

    distinct_number: str = Field(..., primary_key=True, description="Target row business ID", schema_extra={"examples": ["T-2026-01"]})
    target_year: str = Field(..., description="YYYY", schema_extra={"examples": ["2026"]})
    setting_value: float = Field(..., description="Target amount", schema_extra={"examples": [1000000.0]})
    is_done: str = Field(..., description="Y/N", schema_extra={"examples": ["N"]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})


class TargetSettingCreate(SQLModel):
    distinct_number: str = Field(..., description="Target row business ID", schema_extra={"examples": ["T-2026-01"]})
    setting_value: float = Field(..., description="Target amount", schema_extra={"examples": [1000000.0]})
    target_year: str | None = Field(
        default=None,
        description="YYYY; defaults to the current year when omitted",
        schema_extra={"examples": ["2026"]},
    )
    is_done: str | None = Field(
        default=None,
        description="Y/N; defaults to N when omitted",
        schema_extra={"examples": ["N"]},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"distinct_number": "T-2026-01", "setting_value": 1000000.0}
        }
    )


class TargetSettingUpdate(SQLModel):
    target_year: str | None = Field(default=None, description="YYYY", schema_extra={"examples": ["2026"]})
    setting_value: float | None = Field(default=None, description="Target amount", schema_extra={"examples": [1200000.0]})
    is_done: str | None = Field(default=None, description="Y/N", schema_extra={"examples": ["Y"]})

    model_config = ConfigDict(json_schema_extra={"example": {"is_done": "Y"}})


class TargetSettingRead(SQLModel):
    distinct_number: str = Field(..., description="Target row business ID", schema_extra={"examples": ["T-2026-01"]})
    target_year: str = Field(..., description="YYYY", schema_extra={"examples": ["2026"]})
    setting_value: float = Field(..., description="Target amount", schema_extra={"examples": [1000000.0]})
    is_done: str = Field(..., description="Y/N", schema_extra={"examples": ["N"]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})
