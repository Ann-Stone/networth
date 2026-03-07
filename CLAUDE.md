# Balance Sheet — Project Overview

> This file is for the Architect to use when executing in the project root directory.

---

## Monorepo Structure

| Label | Directory | Description | Tech Stack |
|-------|-----------|-------------|------------|
| `view` | `view/` | Frontend SPA — personal finance dashboard | Vue 3 + TS, Pinia, Element Plus 2.x, Tailwind v4, ECharts, Vite 7 |
| `api` | `api/` | Backend API — accounting data service | FastAPI, SQLModel, SQLite, Alembic, uv |

> Legacy code: `account-book-API/` (old Flask backend), `account-book-view/` (old Vue 2 frontend) — for reference only.

## Subproject Routing Guide

When analyzing an issue, determine the scope of impact and mark it in the output tag:

- **Frontend-only** (UI, components, stores, charts, views) → `[DONE:view]`
- **Backend-only** (API endpoints, models, database, data logic) → `[DONE:api]`
- **Full-stack** (Both frontend and backend need modifications) → `[DONE:view,api]` (The system will automatically split this into two sub-issues)
- **Monorepo-level** (CI/CD, shared configs, docs) → `[DONE]`

## Frontend Overview (view)

Personal finance management SPA: Monthly cash flow, annual balance sheet,
asset management (stocks, real estate, insurance, loans), budgets, and reminders.

- Composition API only (`<script setup lang="ts">`)
- Pinia stores — flat, domain-scoped (one store per domain, do not import each other)
- API layer — All HTTP requests go through `src/api/`, axios is encapsulated in `src/utils/request.ts`
- Types — Centralized in `src/types/models.ts`
- For detailed architecture, see `view/CLAUDE.md`

## Backend Overview (api)

FastAPI REST API + SQLite. Three-layer architecture: Router → Service → Model.
6 domains: settings, monthly_report, assets, reports, dashboard, utilities.

- Entry: `app/main.py`
- Routers: `app/routers/` organized by domain
- Models: `app/models/` (SQLModel, schemas co-located)
- Services: `app/services/` (flat, business logic)
- DB: `data/networth.db`
- Migration: Alembic (`migrations/`)
- For detailed architecture, see `api/CLAUDE.md`
