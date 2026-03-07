# Networth API — Developer Conventions

---

## Tech Stack Quick Reference

| What | Where |
|------|-------|
| Framework | FastAPI |
| ORM + Validation | SQLModel (SQLAlchemy + Pydantic v2) |
| Database | SQLite via `app/database.py` |
| Config | pydantic-settings, `.env` file |
| Migration | Alembic, `migrations/` |
| Response format | `app/schemas/response.py` |
| Types/Schemas | Co-located with models in `app/models/<domain>/` |

---

## Key File Locations

```
app/
  main.py                          ← App entry, router mounting, lifespan
  database.py                      ← engine, get_session()
  config.py                        ← Settings class (reads .env)
  schemas/response.py              ← ApiResponse[T], ApiError
  models/<domain>/<entity>.py      ← Table model + Create/Update/Read schemas
  routers/<domain>/<resource>.py   ← Endpoint handlers
  routers/<domain>/__init__.py     ← Sub-router aggregation
  services/<domain>_service.py     ← Business logic functions
```

---

## DO:
- Use `ApiResponse(data=result)` for all success returns
- Use `Depends(get_session)` in every router that touches DB
- Pass `session` as first parameter to all service functions
- Define Create/Update/Read schemas in the same file as the table model
- Use `select()` from sqlmodel for queries — never raw SQL
- Run `uv run alembic revision --autogenerate` after any model change
- Use `BackgroundTasks` for stock/FX/invoice imports

## DO NOT:
- Import `Session` or create sessions inside routers — always use `Depends(get_session)`
- Put business logic in routers — delegate to `services/`
- Create new files in `app/schemas/` — only `response.py` lives there
- Import one store/service from another service (avoid circular deps)
- Use `Optional[X]` — use `X | None = None` instead
- Hardcode config values — use `from app.config import settings`

---

## Common Pitfalls

| Problem | Fix |
|---------|-----|
| BackgroundTask DB error | Background tasks run after response. Create `with Session(engine) as s:` inside the task, not `Depends` |
| SQLModel not creating table | Add `table=True` to class definition |
| Alembic misses new model | Import model in `migrations/env.py` target metadata |
| Composite PK not working | Use `__table_args__ = (PrimaryKeyConstraint("col1", "col2"),)` |
| Pydantic validation error on optional | Use `field: str \| None = None`, not `field: str = None` |
| Model `.from_orm()` deprecated | Use `model_validate()` in Pydantic v2 |
| Date string format mismatch | Always store as `YYYYMMDD` string, parse with `datetime.strptime` |
| Session closed after yield | Never store session reference outside `Depends` scope |
