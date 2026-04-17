# Networth API — Architecture & Conventions

---

## Architecture Principles

### 1. Three-layer: Router → Service → Model
- **Routers** handle HTTP concerns: request parsing, response formatting, status codes
- **Services** handle business logic: calculations, cross-domain queries, data transformation
- **Models** handle data: SQLModel table definitions, Create/Update/Read schemas

### 2. SQLModel models — domain-scoped, schemas co-located
Each domain has its own model directory. Table models and their CRUD schemas live in the same file.

```
app/models/
  settings/           ← Account, CodeData, Budget, CreditCard, Alarm
  monthly_report/     ← Journal, AccountBalance, CreditCardBalance, *NetValueHistory
  assets/             ← Stock, Insurance, Estate, Loan, OtherAsset + journals
  dashboard/          ← FXRate, StockPriceHistory, TargetSetting
```

> Note: the legacy `InitialSetting` table is intentionally not ported — see `refactoring-tickets/README.md` "Decision Log".

**Model pattern:**
```python
class Account(SQLModel, table=True):
    __tablename__ = "Account"
    id: int | None = Field(default=None, primary_key=True)
    name: str
    # ...

class AccountCreate(SQLModel):
    name: str
    # ... (no id)

class AccountUpdate(SQLModel):
    name: str | None = None
    # ... (all optional)

class AccountRead(SQLModel):
    id: int
    name: str
    # ... (full fields)
```

### 3. Service layer — flat, function-based
Services are plain functions in `app/services/`. No classes. Session passed as parameter.

```python
# app/services/setting_service.py
def get_accounts(session: Session, name: str | None = None) -> list[Account]:
    statement = select(Account)
    if name:
        statement = statement.where(Account.name.contains(name))
    return session.exec(statement).all()
```

Cross-domain services (e.g., settlement) import models from multiple domains directly.

### 4. FastAPI Depends() for DB session
All routers receive session via dependency injection. Never create sessions manually in routers.

```python
@router.get("/accounts")
def list_accounts(session: Session = Depends(get_session)):
    return ApiResponse(data=get_accounts(session))
```

### 5. Unified response envelope
All endpoints return `ApiResponse[T]` on success, `ApiError` on failure.
Defined in `app/schemas/response.py` — the only file in `schemas/`.

```python
ApiResponse(data=result)          # { status: 1, data: ..., msg: "success" }
ApiError(error=str(e))            # { status: 0, error: ..., msg: "fail" }
```

### 6. BackgroundTasks for async imports
Stock price, FX rate, and invoice CSV imports run as FastAPI BackgroundTasks.
Background tasks must create their own `Session(engine)` — never reuse the request session.

---

## Directory & File Responsibilities

```
app/
  main.py              ← FastAPI app, lifespan, mount 6 domain routers
  database.py          ← engine, get_session() generator
  config.py            ← pydantic-settings Settings class
  schemas/response.py  ← ApiResponse[T], ApiError, global exception handler
  models/<domain>/     ← SQLModel table + Create/Update/Read schemas
  routers/<domain>/    ← APIRouter per resource, __init__.py aggregates sub-routers
  services/            ← Business logic functions (flat, one file per domain or feature)
migrations/            ← Alembic migration versions
scripts/               ← One-off scripts (e.g., migrate_from_legacy.py)
docs/                  ← Generated openapi.json + api-reference.md (committed)
tests/                 ← pytest tests organized by domain
```

> The production SQLite DB is NOT stored inside the repo. Default path is `~/.networth/networth.db`; users can override via `DATABASE_URL` in `.env` or env var. The `api/` directory must not contain `*.db` files — `.gitignore` enforces this.

### Router aggregation
Each domain `routers/<domain>/__init__.py` creates a parent router and includes sub-routers:

```python
# app/routers/settings/__init__.py
router = APIRouter(prefix="/settings", tags=["settings"])
router.include_router(accounts_router)
router.include_router(codes_router)
# ...
```

Then `main.py` mounts 6 domain routers + 1 health check.

---

## Naming Conventions

| What | Convention | Example |
|------|-----------|---------|
| Python files | snake_case | `account.py`, `code_data.py` |
| Model classes | PascalCase | `Account`, `CodeData`, `StockJournal` |
| Schema classes | Model + suffix | `AccountCreate`, `AccountUpdate`, `AccountRead` |
| Router files | plural noun | `accounts.py`, `codes.py`, `journals.py` |
| Service files | domain_service | `setting_service.py`, `settlement_service.py` |
| Functions | verb_noun | `get_accounts()`, `create_journal()`, `settle_month()` |
| URL paths | kebab-case | `/settings/credit-cards`, `/monthly-report/journals` |

---

## Project Overview

**Networth API** — personal finance REST API for tracking monthly cash flow, annual balance sheet, and asset management (stocks, real estate, insurance, loans).

No authentication. Single-user. SQLite database.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI |
| ORM | SQLModel |
| Migration | Alembic |
| Validation | Pydantic v2 (built-in) |
| Package Manager | uv |
| Config | pydantic-settings + .env |
| Database | SQLite |
| External Data | yfinance, httpx |

---

## Commands

```bash
uv run dev                                    # Start uvicorn on port 9528
uv run alembic revision --autogenerate -m ""  # Generate migration
uv run alembic upgrade head                   # Apply migrations
uv run pytest                                 # Run tests
uv run export-docs                            # Regenerate api/docs/openapi.json + api-reference.md
```

---

## API documentation discipline (contract-as-spec)

The Swagger UI at `/docs` — and the committed `api/docs/openapi.json` / `api/docs/api-reference.md` — **are the API spec** consumed by the frontend refactor. This is non-negotiable discipline, enforced in BE-032 by a CI check.

### Every endpoint MUST
- Have `summary` and `description` on the route decorator (English).
- Use Pydantic models for both request and response (never raw `dict`).
- Declare `responses={...}` with error-code examples.
- Annotate query params: `Annotated[T, Query(..., description="...", examples=[...])]`.

### Every Pydantic field MUST
- Use `Field(..., description="...", examples=[...])`.
- Add `model_config = ConfigDict(json_schema_extra={"example": {...}})` to every schema class for a full-model example.

### Contract boundary
- Frontend-side AI agents consume `api/docs/api-reference.md` (primary) and `api/docs/openapi.json` (drill-down).
- Frontend agents **do not** read `api/app/routers/**` or `api/app/models/**`. If the spec is missing something they need, fix the spec — don't let the reader reach into implementation.

### Language policy
All ticket content, OpenAPI descriptions, code comments, and generated docs are written in **English**. User-facing conversation uses Traditional Chinese only.
