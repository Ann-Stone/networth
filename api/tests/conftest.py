"""Shared pytest fixtures for the networth-api tests."""
from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401  registers every table on SQLModel.metadata
from app.database import get_session
from app.main import app


@pytest.fixture
def session() -> Generator[Session, None, None]:
    """Yield a throw-away SQLModel session backed by in-memory SQLite."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


@pytest.fixture
def client(session: Session) -> Generator[TestClient, None, None]:
    """Yield a TestClient whose get_session dependency returns ``session``."""

    def _override() -> Generator[Session, None, None]:
        yield session

    app.dependency_overrides[get_session] = _override
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.pop(get_session, None)
