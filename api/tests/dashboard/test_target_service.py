"""BE-027 — target service tests."""
from __future__ import annotations

from datetime import datetime

import pytest
from fastapi import HTTPException
from sqlmodel import Session

from app.models.dashboard.target_setting import (
    TargetSettingCreate,
    TargetSettingUpdate,
)
from app.services.dashboard_service import (
    create_target,
    delete_target,
    list_targets,
    update_target,
)


def test_list_targets_returns_all(session: Session) -> None:
    create_target(
        session,
        TargetSettingCreate(distinct_number="T1", setting_value=1.0, target_year="2025"),
    )
    create_target(
        session,
        TargetSettingCreate(distinct_number="T2", setting_value=2.0, target_year="2026"),
    )
    rows = list_targets(session)
    assert [r.distinct_number for r in rows] == ["T2", "T1"]


def test_create_target_defaults_year_and_done(session: Session) -> None:
    out = create_target(
        session, TargetSettingCreate(distinct_number="T-A", setting_value=500.0)
    )
    assert out.target_year == datetime.now().strftime("%Y")
    assert out.is_done == "N"


def test_update_target_is_done_only(session: Session) -> None:
    create_target(
        session,
        TargetSettingCreate(distinct_number="T1", setting_value=1.0, target_year="2026"),
    )
    out = update_target(session, "T1", TargetSettingUpdate(is_done="Y"))
    assert out.is_done == "Y"
    assert out.setting_value == 1.0
    assert out.target_year == "2026"


def test_update_target_missing(session: Session) -> None:
    with pytest.raises(HTTPException) as ei:
        update_target(session, "missing", TargetSettingUpdate(is_done="Y"))
    assert ei.value.status_code == 404


def test_delete_target_missing_returns_404(session: Session) -> None:
    with pytest.raises(HTTPException) as ei:
        delete_target(session, "missing")
    assert ei.value.status_code == 404


def test_create_target_duplicate_409(session: Session) -> None:
    create_target(session, TargetSettingCreate(distinct_number="T1", setting_value=1.0))
    with pytest.raises(HTTPException) as ei:
        create_target(session, TargetSettingCreate(distinct_number="T1", setting_value=2.0))
    assert ei.value.status_code == 409
