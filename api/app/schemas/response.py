"""Unified response envelopes used by every endpoint."""
from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Successful response envelope."""

    status: int = Field(
        1,
        description="1 = success, 0 = fail",
        examples=[1],
    )
    data: T | None = Field(
        None,
        description="Response payload. Shape depends on the endpoint.",
    )
    msg: str = Field(
        "success",
        description="Human-readable status message",
        examples=["success"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"status": 1, "data": None, "msg": "success"},
        }
    )


class ApiError(BaseModel):
    """Failure response envelope."""

    status: int = Field(
        0,
        description="Always 0 for failure",
        examples=[0],
    )
    error: dict | list | str | None = Field(
        None,
        description="Error payload. A string for simple errors, or a list/dict for validation details.",
        examples=["ValueError: bad input"],
    )
    msg: str = Field(
        "fail",
        description="Human-readable status message",
        examples=["fail"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": 0,
                "error": "ValueError: bad input",
                "msg": "fail",
            },
        }
    )
