# Phase 0 — Project Setup

---

## BE-001: Initialize networth-api project with FastAPI + uv

**Labels:** `backend` `setup`
**Priority:** Urgent

### Description

建立全新的 `networth-api` 後端專案，以 FastAPI + uv 取代舊有的 `account-book-API`（Flask + pip）。

### Tasks

- 在 workspace root 建立 `networth-api/` 資料夾
- 使用 `uv init` 初始化專案，建立 `pyproject.toml`
- 安裝核心依賴：
  - `fastapi`
  - `uvicorn[standard]`
  - `sqlmodel`
  - `alembic`
  - `pydantic-settings`
  - `python-dateutil`
  - `yfinance`
  - `pandas`
  - `httpx`（取代 requests）
- 建立以下目錄結構：
  ```
  networth-api/
  ├── app/
  │   ├── main.py           # FastAPI app 入口
  │   ├── database.py       # DB engine + session
  │   ├── config.py         # pydantic-settings
  │   ├── models/           # SQLModel models（按 domain 分資料夾）
  │   │   ├── settings/
  │   │   ├── monthly_report/
  │   │   ├── assets/
  │   │   └── dashboard/
  │   ├── routers/          # APIRouter（按 domain 分資料夾）
  │   │   ├── settings/
  │   │   ├── monthly_report/
  │   │   ├── assets/
  │   │   ├── reports/
  │   │   ├── dashboard/
  │   │   └── utilities/
  │   └── services/         # Business logic（按 domain）
  ├── migrations/           # Alembic migration files
  ├── data/                 # SQLite db file
  ├── tests/
  ├── .env.example
  ├── alembic.ini
  └── pyproject.toml
  ```
- 在 `app/main.py` 建立基礎 FastAPI app，掛載所有 router（空殼即可）
- 設定 uvicorn 啟動指令在 `pyproject.toml` 的 `[tool.uv.scripts]`，port 9528

### Acceptance Criteria

- `uv run dev` 可啟動 uvicorn，`http://localhost:9528/docs` 可訪問 Swagger UI
- 專案結構符合上述目錄樹

---

## BE-002: Setup SQLModel + Alembic database layer

**Labels:** `backend` `setup` `database`
**Priority:** Urgent
**Depends on:** BE-001

### Description

建立 SQLModel 的 database session 管理，以及 Alembic 的 migration 設定，讓後續的 model 定義可以自動產生 migration。

### Tasks

- 在 `app/database.py` 建立：
  - SQLite engine（`sqlite:///./data/networth.db`）
  - `get_session()` dependency（FastAPI Depends 模式）
  ```python
  from sqlmodel import SQLModel, create_engine, Session
  from typing import Generator

  engine = create_engine(DATABASE_URL, echo=settings.debug)

  def get_session() -> Generator[Session, None, None]:
      with Session(engine) as session:
          yield session
  ```
- 初始化 Alembic：`uv run alembic init migrations`
- 設定 `alembic.ini` 與 `migrations/env.py` 讀取 `DATABASE_URL` 從 settings
- `migrations/env.py` 設定 `target_metadata = SQLModel.metadata`
- 建立 `create_db_and_tables()` 函式在 `main.py` lifespan 中呼叫（開發環境用）

### Acceptance Criteria

- `uv run alembic revision --autogenerate -m "init"` 可正確產生 migration
- `uv run alembic upgrade head` 可建立資料庫

---

## BE-003: Configure environment variables with pydantic-settings

**Labels:** `backend` `setup` `config`
**Priority:** Urgent
**Depends on:** BE-001

### Description

以 pydantic-settings 取代舊的 `config.py` hardcoded 設定，敏感資訊改由 `.env` 管理。

舊 `config.py` 問題：
- Invoice API credentials 直接 hardcoded（安全風險）
- 無法區分 dev / prod 環境

### Tasks

- 在 `app/config.py` 建立 `Settings` class：
  ```python
  from pydantic_settings import BaseSettings, SettingsConfigDict

  class Settings(BaseSettings):
      model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

      app_name: str = "Networth API"
      debug: bool = True
      port: int = 9528
      database_url: str = "sqlite:///./data/networth.db"

      # Invoice import (optional)
      invoice_card_no: str = ""
      invoice_password: str = ""
      invoice_app_id: str = ""
      invoice_skip: bool = False
      import_csv: str = ""

  settings = Settings()
  ```
- 建立 `.env.example`（含所有 key，不含真實 value）
- 將 `.env` 加入 `.gitignore`
- 所有後續模組透過 `from app.config import settings` 存取設定

### Acceptance Criteria

- 啟動時若 `.env` 不存在，使用預設值正常啟動
- 不得有任何 credentials 直接寫在程式碼中

---

## BE-004: Setup CORS, unified response format, and global exception handler

**Labels:** `backend` `setup` `middleware`
**Priority:** High
**Depends on:** BE-001

### Description

建立 API 統一的 response 格式、CORS 設定，以及全域 exception handler，取代舊版分散在各 route 的 try/except。

舊版 response 格式：
```json
{ "status": 1, "data": {...}, "msg": "success" }
{ "status": 0, "error": {...}, "msg": "fail" }
```

### Tasks

- 在 `app/main.py` 加入 CORS middleware：
  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```
- 建立 `app/schemas/response.py`，定義標準 response model：
  ```python
  from typing import Generic, TypeVar
  from pydantic import BaseModel

  T = TypeVar("T")

  class ApiResponse(BaseModel, Generic[T]):
      status: int = 1
      data: T | None = None
      msg: str = "success"

  class ApiError(BaseModel):
      status: int = 0
      error: dict | str | None = None
      msg: str = "fail"
  ```
- 建立全域 exception handler，捕捉 `ValueError`、`Exception`，回傳 `ApiError` 格式
- 所有 router 使用 `response_model=ApiResponse[T]` 統一格式

### Acceptance Criteria

- 任何 endpoint 成功時回傳 `{ status: 1, data: ..., msg: "success" }`
- 任何未捕捉例外回傳 `{ status: 0, error: ..., msg: "fail" }` with HTTP 500

---

## BE-005: Migrate SQLite database from account-book-API

**Labels:** `backend` `setup` `database` `migration`
**Priority:** High
**Depends on:** BE-002

### Description

將舊 `account-book-API/data/ledger.db` 的資料遷移至新的 `networth-api/data/networth.db`，確保歷史資料不遺失。

### Tasks

- 確認舊 DB 的所有 table schema 與 SQLModel models（BE-006 ~ BE-009）完全對應
- 建立 migration script `scripts/migrate_from_legacy.py`：
  - 從 `ledger.db` 讀取所有 table 資料
  - 寫入 `networth.db`（透過 SQLModel session）
  - 處理欄位命名差異（snake_case 統一）
- 執行 migration 並驗證 row count 一致
- 舊 DB 保留為備份，不刪除

### Acceptance Criteria

- `networth.db` 中各 table 的 row count 與 `ledger.db` 完全一致
- 所有 date 欄位格式統一為 ISO 8601
