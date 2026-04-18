"""Enforces API documentation discipline: every production route must use
ApiResponse[...] as its response_model.

Re-used by every later CRUD ticket — extend the SKIP set sparingly.
"""
from __future__ import annotations

import inspect

from fastapi.routing import APIRoute

from app.main import app
from app.schemas.response import ApiResponse

# FastAPI auto-registers these — they have no custom response_model.
AUTO_PATHS: set[str] = {
    "/openapi.json",
    "/docs",
    "/docs/oauth2-redirect",
    "/redoc",
}

# Internal test-only endpoints registered by test_exception_handlers.py.
TEST_PATH_PREFIX = "/__raise__"


def _is_api_response(model: object) -> bool:
    """Return True iff `model` is ApiResponse or a parametrised subclass of it.

    pydantic v2 materialises `ApiResponse[T]` as a concrete subclass of
    `ApiResponse`, so an `issubclass` check is the correct discipline probe.
    """
    return inspect.isclass(model) and issubclass(model, ApiResponse)


def test_every_route_uses_api_response() -> None:
    offenders: list[str] = []

    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        if route.path in AUTO_PATHS or route.path.startswith(TEST_PATH_PREFIX):
            continue

        model = route.response_model
        if model is None:
            offenders.append(f"{route.path}: missing response_model")
            continue
        if not _is_api_response(model):
            offenders.append(f"{route.path}: response_model is {model!r}, not ApiResponse[...]")

    assert not offenders, "routes missing ApiResponse[...] response_model:\n" + "\n".join(offenders)
