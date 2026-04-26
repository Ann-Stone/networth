"""Tests for the export-docs script (BE-032)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

from app.scripts import export_docs
from app.scripts.export_docs import (
    dump_markdown,
    dump_openapi,
    load_app,
    main,
    render_markdown,
    validate_discipline,
)
from app.schemas.response import ApiResponse


# ---------- Builder helpers ----------


class _Echo(BaseModel):
    msg: str = Field(..., description="Echo string", examples=["hi"])

    model_config = ConfigDict(json_schema_extra={"example": {"msg": "hi"}})


# ---------- Tests ----------


def test_load_app_returns_fastapi() -> None:
    assert isinstance(load_app(), FastAPI)


def test_dump_openapi_is_deterministic(tmp_path: Path) -> None:
    app = load_app()
    out1 = tmp_path / "1.json"
    out2 = tmp_path / "2.json"
    dump_openapi(app, out1)
    dump_openapi(app, out2)
    assert out1.read_bytes() == out2.read_bytes()


def test_validate_discipline_flags_missing_summary_and_description() -> None:
    spec: dict[str, Any] = {
        "paths": {
            "/x": {
                "get": {
                    # No summary, no description, no responses[200].
                    "responses": {}
                }
            }
        },
        "components": {"schemas": {}},
    }
    errors = validate_discipline(spec)
    assert any("missing summary" in e for e in errors)
    assert any("missing description" in e for e in errors)
    assert any("missing response_model" in e for e in errors)


def test_render_markdown_has_domain_sections() -> None:
    app = load_app()
    md = render_markdown(app.openapi())
    for label in ("Settings", "Monthly Report", "Assets", "Reports", "Dashboard", "Utilities", "Health"):
        assert f"## {label}" in md, label
    assert "## Table of Contents" in md


def test_render_markdown_endpoint_block_shape() -> None:
    app = load_app()
    md = render_markdown(app.openapi())
    assert "### GET /health" in md
    assert "#### Response (200)" in md


def test_dump_markdown_trailing_newline(tmp_path: Path) -> None:
    out = tmp_path / "x.md"
    dump_markdown("hello", out)
    text = out.read_text(encoding="utf-8")
    assert text.endswith("\n")


def test_export_docs_writes_both_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(export_docs, "_output_dir", lambda: tmp_path)
    rc = main([])
    assert rc == 0
    assert (tmp_path / "openapi.json").stat().st_size > 0
    assert (tmp_path / "api-reference.md").stat().st_size > 0


def test_export_docs_is_idempotent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(export_docs, "_output_dir", lambda: tmp_path)
    main([])
    json_a = (tmp_path / "openapi.json").read_bytes()
    md_a = (tmp_path / "api-reference.md").read_bytes()
    main([])
    assert (tmp_path / "openapi.json").read_bytes() == json_a
    assert (tmp_path / "api-reference.md").read_bytes() == md_a


def _build_synthetic_app(
    *, with_summary: bool, with_description: bool, with_response_model: bool
) -> FastAPI:
    app = FastAPI()
    kwargs: dict[str, Any] = {}
    if with_summary:
        kwargs["summary"] = "Echo"
    if with_description:
        kwargs["description"] = "Echo back."
    if with_response_model:
        kwargs["response_model"] = ApiResponse[_Echo]

    @app.get("/echo", **kwargs)
    def _echo() -> Any:
        return {"status": 1, "data": {"msg": "hi"}, "msg": "success"}

    return app


def test_validate_discipline_rejects_route_without_summary() -> None:
    spec = {
        "paths": {
            "/echo": {
                "get": {
                    "description": "Echo back.",
                    "responses": {
                        "200": {
                            "description": "ok",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Echo"}
                                }
                            },
                        }
                    },
                }
            }
        },
        "components": {"schemas": {}},
    }
    errors = validate_discipline(spec)
    assert any("/echo" in e and "summary" in e for e in errors)


def test_validate_discipline_rejects_field_without_description() -> None:
    spec = {
        "paths": {},
        "components": {
            "schemas": {
                "Foo": {
                    "type": "object",
                    "properties": {
                        "x": {"type": "integer"},  # no description
                    },
                }
            }
        },
    }
    errors = validate_discipline(spec)
    assert any("Foo.x" in e and "missing description" in e for e in errors)


def test_validate_discipline_rejects_route_without_response_model() -> None:
    app = FastAPI()

    @app.get("/raw", summary="Raw", description="Raw")
    def _raw() -> dict:
        return {"ok": True}

    errors = validate_discipline(app.openapi())
    # FastAPI auto-generates a 200 schema; we explicitly reject when no schema
    # at all is present (e.g. responses missing 200 entirely).
    # Routes returning raw dict still get an inferred response schema, but
    # ApiResponse envelope check is what we *want* — for now we accept
    # FastAPI's default object schema as valid (matches granular note re:
    # ApiResponse[None]). Confirm validator does not over-reject by
    # inspecting at least one error path elsewhere.
    # This test guards the explicit-no-response-model path:
    # build an OpenAPI dict by hand without any 200 response.
    spec = {
        "paths": {
            "/raw": {
                "get": {
                    "summary": "Raw",
                    "description": "Raw",
                    "responses": {"500": {"description": "boom"}},
                }
            }
        },
        "components": {"schemas": {}},
    }
    errs = validate_discipline(spec)
    assert any("/raw" in e and "missing response_model" in e for e in errs)


def test_full_app_passes_discipline() -> None:
    app = load_app()
    errors = validate_discipline(app.openapi())
    assert errors == [], "\n".join(errors)
