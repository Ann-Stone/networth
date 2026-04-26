"""Export OpenAPI spec + render api-reference.md.

Used as the `export-docs` console script (see `pyproject.toml`). Both
artifacts at `api/docs/` are committed and consumed by the frontend refactor;
the CI step (BE-032 sub-task 16) re-runs this and fails on any drift.
"""
from __future__ import annotations

import argparse
import filecmp
import json
import shutil
import sys
import tempfile
from pathlib import Path

from fastapi import FastAPI


_DOMAIN_ORDER = [
    ("Settings", ("/settings",)),
    ("Monthly Report", ("/monthly-report",)),
    ("Assets", ("/assets",)),
    ("Reports", ("/reports",)),
    ("Dashboard", ("/dashboard",)),
    ("Utilities", ("/utilities",)),
    ("Health", ("/health",)),
]


def load_app() -> FastAPI:
    """Import the live FastAPI app without starting uvicorn or touching the DB."""
    from app.main import app

    return app


def dump_openapi(app: FastAPI, out_path: Path) -> dict:
    """Write spec to `out_path` with deterministic ordering."""
    spec = app.openapi()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fp:
        json.dump(spec, fp, indent=2, sort_keys=True, ensure_ascii=False)
        fp.write("\n")
    return spec


def _is_envelope_response(operation: dict) -> bool:
    """True if operation has a 200 (or 202) JSON response with a $ref schema."""
    responses = operation.get("responses", {}) or {}
    for code in ("200", "201", "202"):
        resp = responses.get(code)
        if not resp:
            continue
        content = resp.get("content", {}) or {}
        for media in content.values():
            schema = media.get("schema") or {}
            if "$ref" in schema:
                return True
            if (
                schema.get("type") == "array"
                and isinstance(schema.get("items"), dict)
                and ("$ref" in schema["items"] or schema["items"].get("type"))
            ):
                return True
            if schema.get("type") in {"object", "string", "integer", "number", "boolean"}:
                return True
    return False


def validate_discipline(spec: dict) -> list[str]:
    """Return a list of discipline violations; empty list = clean."""
    errors: list[str] = []

    paths = spec.get("paths", {}) or {}
    for path, methods in sorted(paths.items()):
        for method, operation in sorted(methods.items()):
            if method.lower() not in {"get", "post", "put", "patch", "delete"}:
                continue
            ident = f"{method.upper()} {path}"
            if not operation.get("summary"):
                errors.append(f"{ident}: missing summary")
            if not operation.get("description"):
                errors.append(f"{ident}: missing description")
            if not _is_envelope_response(operation):
                errors.append(f"{ident}: missing response_model")

    # FastAPI auto-injects HTTPValidationError/ValidationError for any route
    # with a request body or path/query params. They are framework-owned and
    # not subject to our discipline rules.
    framework_owned = {"HTTPValidationError", "ValidationError"}
    schemas = (spec.get("components", {}) or {}).get("schemas", {}) or {}
    for name, schema in sorted(schemas.items()):
        if name in framework_owned:
            continue
        for prop_name, prop in (schema.get("properties", {}) or {}).items():
            if "$ref" in prop:
                continue
            if not prop.get("description"):
                errors.append(f"schema {name}.{prop_name}: missing description")
    return errors


def _domain_for(path: str) -> str:
    for label, prefixes in _DOMAIN_ORDER:
        if any(path.startswith(p) for p in prefixes):
            return label
    return "Other"


def _resolve_ref(spec: dict, ref: str) -> dict:
    if not ref.startswith("#/components/schemas/"):
        return {}
    name = ref.split("/")[-1]
    return (spec.get("components", {}) or {}).get("schemas", {}).get(name, {}) or {}


def _params_table(parameters: list[dict]) -> str:
    if not parameters:
        return ""
    rows = ["| name | in | type | required | description |", "| --- | --- | --- | --- | --- |"]
    for p in parameters:
        schema = p.get("schema", {}) or {}
        type_ = schema.get("type", "")
        rows.append(
            f"| {p.get('name', '')} | {p.get('in', '')} | {type_} | "
            f"{'yes' if p.get('required') else 'no'} | "
            f"{p.get('description', '')} |"
        )
    return "\n".join(rows)


def _request_body_table(spec: dict, request_body: dict) -> str:
    if not request_body:
        return ""
    content = request_body.get("content", {}) or {}
    media = content.get("application/json")
    if not media:
        return ""
    schema = media.get("schema", {}) or {}
    if "$ref" in schema:
        schema = _resolve_ref(spec, schema["$ref"])
    props = schema.get("properties", {}) or {}
    if not props:
        return ""
    required = set(schema.get("required", []) or [])
    rows = ["| name | type | required | description |", "| --- | --- | --- | --- |"]
    for name, prop in props.items():
        if "$ref" in prop:
            type_ = prop["$ref"].split("/")[-1]
        else:
            type_ = prop.get("type", "")
        rows.append(
            f"| {name} | {type_} | {'yes' if name in required else 'no'} | "
            f"{prop.get('description', '')} |"
        )
    return "\n".join(rows)


def _response_table(spec: dict, operation: dict) -> str:
    responses = operation.get("responses", {}) or {}
    for code in ("200", "201", "202"):
        resp = responses.get(code)
        if not resp:
            continue
        content = resp.get("content", {}) or {}
        media = content.get("application/json") or next(iter(content.values()), None)
        if not media:
            continue
        schema = media.get("schema", {}) or {}
        if "$ref" in schema:
            schema = _resolve_ref(spec, schema["$ref"])
        props = schema.get("properties", {}) or {}
        if not props:
            return ""
        rows = ["| name | type | description |", "| --- | --- | --- |"]
        for name, prop in props.items():
            if "$ref" in prop:
                type_ = prop["$ref"].split("/")[-1]
            else:
                type_ = prop.get("type", "")
            rows.append(f"| {name} | {type_} | {prop.get('description', '')} |")
        return "\n".join(rows)
    return ""


def render_markdown(spec: dict) -> str:
    """Render a deterministic api-reference.md from the OpenAPI spec."""
    lines: list[str] = []
    info = spec.get("info", {}) or {}
    lines.append("# Networth API Reference")
    lines.append("")
    lines.append(
        "Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. "
        "Do not edit by hand."
    )
    lines.append("")
    lines.append(f"- OpenAPI version: `{spec.get('openapi', '')}`")
    if info.get("version"):
        lines.append(f"- API version: `{info['version']}`")
    lines.append("")

    paths = spec.get("paths", {}) or {}
    grouped: dict[str, list[tuple[str, str, dict]]] = {}
    for path, methods in sorted(paths.items()):
        for method, operation in sorted(methods.items()):
            if method.lower() not in {"get", "post", "put", "patch", "delete"}:
                continue
            grouped.setdefault(_domain_for(path), []).append(
                (method.upper(), path, operation)
            )

    # Table of contents
    lines.append("## Table of Contents")
    lines.append("")
    for label, _ in _DOMAIN_ORDER:
        if label in grouped:
            lines.append(f"- [{label}](#{label.lower().replace(' ', '-')})")
    if "Other" in grouped:
        lines.append("- [Other](#other)")
    lines.append("")

    # Per-domain sections
    domain_labels = [lbl for lbl, _ in _DOMAIN_ORDER if lbl in grouped]
    if "Other" in grouped:
        domain_labels.append("Other")
    for label in domain_labels:
        lines.append(f"## {label}")
        lines.append("")
        for method, path, op in grouped[label]:
            lines.append(f"### {method} {path}")
            lines.append("")
            if op.get("summary"):
                lines.append(f"**{op['summary']}**")
                lines.append("")
            if op.get("description"):
                lines.append(op["description"])
                lines.append("")
            params_md = _params_table(op.get("parameters", []) or [])
            body_md = _request_body_table(spec, op.get("requestBody", {}) or {})
            if params_md or body_md:
                lines.append("#### Request")
                lines.append("")
                if params_md:
                    lines.append(params_md)
                    lines.append("")
                if body_md:
                    lines.append("Body:")
                    lines.append("")
                    lines.append(body_md)
                    lines.append("")
            resp_md = _response_table(spec, op)
            if resp_md:
                lines.append("#### Response (200)")
                lines.append("")
                lines.append(resp_md)
                lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def dump_markdown(markdown: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    text = markdown if markdown.endswith("\n") else markdown + "\n"
    out_path.write_text(text, encoding="utf-8", newline="\n")


def _output_dir() -> Path:
    """`api/docs/` resolved from this file's location."""
    return Path(__file__).resolve().parents[2] / "docs"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export OpenAPI + api-reference.md.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Re-export to a temp dir and fail on diff vs committed files.",
    )
    args = parser.parse_args(argv)

    app = load_app()
    spec = app.openapi()
    errors = validate_discipline(spec)
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1

    out_dir = _output_dir()
    json_path = out_dir / "openapi.json"
    md_path = out_dir / "api-reference.md"

    if args.check:
        with tempfile.TemporaryDirectory() as td:
            tmp_dir = Path(td)
            tmp_json = tmp_dir / "openapi.json"
            tmp_md = tmp_dir / "api-reference.md"
            dump_openapi(app, tmp_json)
            dump_markdown(render_markdown(spec), tmp_md)
            if not (json_path.exists() and md_path.exists()):
                print("docs/openapi.json or api-reference.md missing", file=sys.stderr)
                return 1
            if not filecmp.cmp(tmp_json, json_path, shallow=False):
                print("openapi.json drift", file=sys.stderr)
                return 1
            if not filecmp.cmp(tmp_md, md_path, shallow=False):
                print("api-reference.md drift", file=sys.stderr)
                return 1
        return 0

    dump_openapi(app, json_path)
    dump_markdown(render_markdown(spec), md_path)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
