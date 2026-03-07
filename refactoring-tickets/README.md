# Networth API — Refactoring Tickets

重構目標：將 `account-book-API`（Flask + SQLAlchemy + SQLite）重構為 `networth-api`（FastAPI + SQLModel + SQLite + Alembic）

## Tech Stack

| | Old | New |
|--|-----|-----|
| Framework | Flask 2.1.2 | FastAPI |
| ORM | SQLAlchemy 2.5.1 (raw SQL heavy) | SQLModel |
| Migration | 無 | Alembic |
| Validation | 無 | Pydantic v2 (built-in SQLModel) |
| Package Manager | pip | uv |
| Config | config.py hardcoded | .env + pydantic-settings |

## Ticket Index

### Phase 0 — Project Setup
| ID | Title | File |
|----|-------|------|
| BE-001 | Initialize networth-api project with FastAPI + uv | [00-setup.md](./00-setup.md) |
| BE-002 | Setup SQLModel + Alembic database layer | [00-setup.md](./00-setup.md) |
| BE-003 | Configure environment variables with pydantic-settings | [00-setup.md](./00-setup.md) |
| BE-004 | Setup CORS, unified response format, and global exception handler | [00-setup.md](./00-setup.md) |
| BE-005 | Migrate SQLite database from account-book-API | [00-setup.md](./00-setup.md) |

### Phase 1 — Data Models
| ID | Title | File |
|----|-------|------|
| BE-006 | Define SQLModel models: Settings domain (Account, Code, Budget, CreditCard, Alarm, InitialSetting) | [01-models.md](./01-models.md) |
| BE-007 | Define SQLModel models: Monthly Report domain (Journal, AccountBalance, CreditCardBalance) | [01-models.md](./01-models.md) |
| BE-008 | Define SQLModel models: Asset domain (Stock, Insurance, Estate, Loan, OtherAsset + all journals/history) | [01-models.md](./01-models.md) |
| BE-009 | Define SQLModel models: Dashboard domain (FXRate, StockPriceHistory, TargetSetting) | [01-models.md](./01-models.md) |

### Phase 2 — Settings Domain
| ID | Title | File |
|----|-------|------|
| BE-010 | Account CRUD endpoints | [02-settings.md](./02-settings.md) |
| BE-011 | Code / Sub-Code CRUD endpoints | [02-settings.md](./02-settings.md) |
| BE-012 | Budget management endpoints | [02-settings.md](./02-settings.md) |
| BE-013 | Credit Card CRUD endpoints | [02-settings.md](./02-settings.md) |
| BE-014 | Alarm / Reminder CRUD endpoints | [02-settings.md](./02-settings.md) |
| BE-015 | Initial Settings CRUD endpoints | [02-settings.md](./02-settings.md) |

### Phase 3 — Monthly Report Domain
| ID | Title | File |
|----|-------|------|
| BE-016 | Journal (Transaction) CRUD endpoints | [03-monthly-report.md](./03-monthly-report.md) |
| BE-017 | Journal analytics endpoints (expenditure ratio, invest ratio, budget comparison, liability) | [03-monthly-report.md](./03-monthly-report.md) |
| BE-018 | Stock price management endpoints | [03-monthly-report.md](./03-monthly-report.md) |
| BE-019 | Monthly balance settlement endpoint | [03-monthly-report.md](./03-monthly-report.md) |

### Phase 4 — Asset Management Domain
| ID | Title | File |
|----|-------|------|
| BE-020 | Stock asset CRUD + transaction detail endpoints | [04-assets.md](./04-assets.md) |
| BE-021 | Insurance asset CRUD + transaction detail endpoints | [04-assets.md](./04-assets.md) |
| BE-022 | Real Estate asset CRUD + transaction detail endpoints | [04-assets.md](./04-assets.md) |
| BE-023 | Loan / Liability CRUD + transaction detail endpoints | [04-assets.md](./04-assets.md) |
| BE-024 | Other Assets CRUD endpoints | [04-assets.md](./04-assets.md) |

### Phase 5 — Reports Domain
| ID | Title | File |
|----|-------|------|
| BE-025 | Year Report endpoints (balance sheet, expenditure trend, asset breakdown) | [05-reports.md](./05-reports.md) |

### Phase 6 — Dashboard Domain
| ID | Title | File |
|----|-------|------|
| BE-026 | Dashboard summary & budget trend endpoints | [06-dashboard.md](./06-dashboard.md) |
| BE-027 | Target Settings CRUD endpoints | [06-dashboard.md](./06-dashboard.md) |
| BE-028 | Dashboard alarm & gift query endpoints | [06-dashboard.md](./06-dashboard.md) |

### Phase 7 — Utility & Global
| ID | Title | File |
|----|-------|------|
| BE-029 | Utility selection group endpoints | [07-utilities.md](./07-utilities.md) |
| BE-030 | Global health check endpoint | [07-utilities.md](./07-utilities.md) |
| BE-031 | Data import endpoints (stock price, FX rate, invoice CSV) | [07-utilities.md](./07-utilities.md) |

## Dependency Graph

```
Phase 0 (Setup)
    └── Phase 1 (Models)
            ├── Phase 2 (Settings)
            ├── Phase 3 (Monthly Report) ← depends on Settings
            ├── Phase 4 (Assets) ← depends on Settings
            ├── Phase 5 (Reports) ← depends on Phase 3 + 4
            ├── Phase 6 (Dashboard) ← depends on Phase 3 + 4
            └── Phase 7 (Utilities) ← depends on Phase 2 + 4
```

## Backlog（前端重構後再排）

| ID | Title | 說明 |
|----|-------|------|
| BE-B01 | User management CRUD endpoints | 舊版 `userRouter.py` 有 User CRUD，但未註冊在 `init_router.py`。待前端重構後確認需求再規劃。 |
| BE-B02 | Initial Settings endpoint redesign | 舊版 `InitialSetting` 使用 `code_id + initial_type` 複合查詢鍵，目前 BE-015 endpoint 設計（無參數的 DELETE/PUT）不夠精確。待前端重構後統一優化 API 設計。 |

## Old API Domain Reference

| Old Domain | New Domain | Port |
|-----------|-----------|------|
| `/account`, `/code`, `/budget`, `/credit-card`, `/alarm`, `/initial` | `settings` | - |
| `/journal`, `/stock/price`, `/balance` | `monthly-report` | - |
| `/other-asset/stock`, `/other-asset/insurance`, `/other-asset/estate`, `/liability/loan`, `/other-asset` | `assets` | - |
| `/report` | `reports` | - |
| `/dashboard`, `/target` | `dashboard` | - |
| `/util`, `/global` | `utilities` | - |
