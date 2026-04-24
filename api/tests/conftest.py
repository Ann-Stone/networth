"""Shared pytest fixtures for the networth-api tests."""
from __future__ import annotations

from collections.abc import Generator

import pytest
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401  registers every table on SQLModel.metadata


@pytest.fixture
def session() -> Generator[Session, None, None]:
    """Yield a throw-away SQLModel session backed by in-memory SQLite."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        yield s
