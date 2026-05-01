# Balance Sheet View — Frontend Refactoring Tickets

Refactor goal: rebuild the `view/` SPA against the new `networth-api` contract
(BE-001..BE-032). All views were stubs at the start of this refactor;
every API call, store, type, and UI component is written from scratch against
the split API spec at `api/docs/` (slim index `api-reference.md` plus per-sub-router
markdown / JSON slices). Each spec file is capped at ~500 lines; see the
"Sub-router → ticket map" in `IMPLEMENTATION_GUIDE.md` for which slice each
ticket reads.

All spec content in this directory is written in English.

> **Step 2 — granularization (this file):** tickets broken into implementation-ready
> task lists under `granular/`. See [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md)
> for execution rules.
>
> **Step 3 — implementation:** one phase per session, driven by the granular files.

---

## Current State (start of refactor)

| File / Directory | Status |
|-----------------|--------|
| `view/vite.config.ts` | ✅ Correct — Vite 7, proxy `/api` → `:9528`, base `/networth/` |
| `view/package.json` | ✅ All dependencies present (Vue 3, EP 2.x, Tailwind v4, Pinia, ECharts) |
| `view/src/main.ts` | ✅ Element Plus + Pinia + Router mounted correctly |
| `view/src/utils/request.ts` | ⚠️ Bug: uses `res.message` instead of `res.msg`; has unused auth header |
| `view/src/types/models.ts` | ❌ Stale — does not match new API shapes |
| `view/src/stores/app.ts` | ✅ UI-only store, no changes needed |
| `view/src/stores/<domain>.ts` | ❌ Missing — none of the 5 domain stores exist |
| `view/src/api/` | ❌ Missing — no API layer |
| `view/src/components/layout/` | ✅ Scaffold exists; needs style update (Phase 2) |
| `view/src/components/charts/` | ❌ Missing |
| `view/src/components/ui/` | ❌ Missing |
| `view/src/views/*View.vue` | ❌ All stubs (`el-alert` placeholder only) |
| `view/src/assets/main.css` | ⚠️ Uses indigo primary; needs warm palette from `template.html` |

---

## Tech Stack (unchanged)

| Layer | Technology |
|-------|-----------|
| Framework | Vue 3 + TypeScript (`<script setup>`) |
| UI Library | Element Plus 2.x |
| CSS | Tailwind CSS v4 (utilities only, no preflight) |
| State | Pinia |
| Router | Vue Router 4 |
| Build | Vite 7 |
| Charts | ECharts 5 via `vue-echarts` |
| HTTP | Axios wrapped in `src/utils/request.ts` |

---

## Phase Table

| Session | Phase | Tickets | Gate at end |
|---------|-------|---------|-------------|
| 1 | Phase 0 — Foundation | FE-001..FE-007 | `npm run type-check` passes (zero errors) |
| 2 | Phase 1 — Stores | FE-008..FE-012 | `npm run type-check` passes; stores importable |
| 3 | Phase 2 — Layout & UI | FE-013..FE-016 | `npm run dev` starts; sidebar renders; no console errors |
| 4 | Phase 3 — Dashboard | FE-017..FE-020 | Dashboard route renders all 4 sections |
| 5 | Phase 4 — Monthly Report | FE-021..FE-024 | Journal CRUD works; charts render |
| 6 | Phase 5 — Year Report | FE-025..FE-027 | All three year-report views render with data |
| 7 | Phase 6 — Asset Management | FE-028..FE-033 | CRUD works for all 5 asset tabs |
| 8 | Phase 7 — Settings | FE-034..FE-038 | All settings CRUD operations work |
| 9 | Phase 8 — Utilities + Mock | FE-039..FE-041 | `npm run build:mock` succeeds |

---

## Ticket Index

### Phase 0 — Foundation
| ID | Title |
|----|-------|
| FE-001 | Patch request.ts — fix envelope field name, remove unused auth interceptor |
| FE-002 | Rewrite src/types/models.ts — complete API-aligned type definitions (all domains) |
| FE-003 | Create src/api/setting.ts |
| FE-004 | Create src/api/dashboard.ts + src/api/utilities.ts |
| FE-005 | Create src/api/cashFlow.ts |
| FE-006 | Create src/api/yearReport.ts |
| FE-007 | Create src/api/otherAssets.ts |

### Phase 1 — Stores
| ID | Title |
|----|-------|
| FE-008 | Create src/stores/setting.ts |
| FE-009 | Create src/stores/dashboard.ts |
| FE-010 | Create src/stores/cashFlow.ts |
| FE-011 | Create src/stores/yearReport.ts |
| FE-012 | Create src/stores/otherAssets.ts |

### Phase 2 — Layout & Shared UI
| ID | Title |
|----|-------|
| FE-013 | Apply template.html warm palette to main.css CSS variables |
| FE-014 | Update Sidebar.vue + SidebarContent.vue for full route coverage |
| FE-015 | Create shared UI primitives — MoneyDisplay.vue, StatusBadge.vue, EmptyState.vue |
| FE-016 | Create chart wrappers — LineChart.vue, BarChart.vue, PieChart.vue, DonutChart.vue |

### Phase 3 — Dashboard
| ID | Title |
|----|-------|
| FE-017 | DashboardView — net-worth summary row (GET /dashboard/summary) |
| FE-018 | DashboardView — alarm widget (GET /dashboard/alarms) |
| FE-019 | DashboardView — targets CRUD panel (CRUD /dashboard/targets) |
| FE-020 | DashboardView — budget overview + gifts (GET /dashboard/budget + /gifts/{year}) |

### Phase 4 — Monthly Report
| ID | Title |
|----|-------|
| FE-021 | CashFlowView — month selector + journal list table |
| FE-022 | CashFlowView — journal CRUD dialogs |
| FE-023 | CashFlowView — analytics chart tabs |
| FE-024 | CashFlowView — settle month + stock price section |

### Phase 5 — Year Report
| ID | Title |
|----|-------|
| FE-025 | BalanceSheetView (GET /reports/balance) |
| FE-026 | SpendingView (GET /reports/expenditure/{type}) |
| FE-027 | AssetView (GET /reports/assets) |

### Phase 6 — Asset Management
| ID | Title |
|----|-------|
| FE-028 | OtherAssetsView — tab shell + stocks list + stock CRUD |
| FE-029 | OtherAssetsView — stock journal detail sub-tab |
| FE-030 | OtherAssetsView — estates tab (parent + details CRUD) |
| FE-031 | OtherAssetsView — insurances tab (parent + details CRUD) |
| FE-032 | OtherAssetsView — loans tab (parent + details CRUD) |
| FE-033 | OtherAssetsView — other-assets tab |

### Phase 7 — Settings
| ID | Title |
|----|-------|
| FE-034 | MenuSettingView — accounts CRUD tab |
| FE-035 | MenuSettingView — codes + sub-codes CRUD tab |
| FE-036 | MenuSettingView — credit-cards CRUD tab |
| FE-037 | BudgetSettingView — year selector + 12-month grid |
| FE-038 | RemindSettingView — alarms CRUD |

### Phase 8 — Utilities + Mock
| ID | Title |
|----|-------|
| FE-039 | Utilities import panel (stock-prices, fx-rates, invoices CSV) |
| FE-040 | MSW mock handlers + static data files |
| FE-041 | Build verification — npm run build + npm run build:mock |

---

## Dependency Graph

```
Phase 0 (Foundation: FE-001..007)
  └─ FE-001 (request.ts) ←── all phases read the response via this
  └─ FE-002 (types) ←── FE-003..FE-007 all import from types/models.ts
  └─ FE-003..007 (api layer)

Phase 1 (Stores: FE-008..012)
  └─ Depends on: Phase 0 complete (needs api files + types)

Phase 2 (Layout: FE-013..016)
  └─ Depends on: Phase 0 (for type-check); can overlap with Phase 1

Phase 3 (Dashboard: FE-017..020)
  └─ Depends on: FE-009 (dashboard store), FE-016 (chart wrappers)

Phase 4 (Monthly Report: FE-021..024)
  └─ Depends on: FE-010 (cashFlow store), FE-016 (charts)
  └─ FE-022 (journal CRUD) depends on FE-021 (journal list)

Phase 5 (Year Report: FE-025..027)
  └─ Depends on: FE-011 (yearReport store), FE-016 (charts)

Phase 6 (Assets: FE-028..033)
  └─ Depends on: FE-012 (otherAssets store)
  └─ FE-029 depends on FE-028 (stock list must exist before detail sub-tab)

Phase 7 (Settings: FE-034..038)
  └─ Depends on: FE-008 (setting store)

Phase 8 (Utilities + Mock: FE-039..041)
  └─ FE-040 depends on all views done (mock data mirrors real API shapes)
  └─ FE-041 is final gate
```

---

## Decision Log

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | Single `OtherAssetsView.vue` with tabs, not separate routes per asset class | Matches existing route `/other-assets`; avoids route proliferation for a personal-use app with 5 closely related sub-sections |
| 2 | `MenuSettingView.vue` hosts accounts + codes + credit-cards as tabs | All are "settings" in the user's mental model; matches the existing `/setting/menu` route |
| 3 | Warm dark palette from `template.html` applied to main.css CSS variables (primary: `#8fa79b` sage green; accent-rose: `#b58d8d`) | User-provided design reference; existing indigo primary is replaced |
| 4 | No authentication layer | Single-user app by design; `request.ts` auth-token interceptor removed (was dead code) |
| 5 | `src/api/utilities.ts` added beyond CLAUDE.md list | `/utilities/selections/*` endpoints are needed by multiple form dialogs (journal, journal CRUD) for account/code/credit-card dropdowns; cleaner to centralize than scatter into other api files |
| 6 | MSW (`msw` npm package) added in Phase 8 only | Only needed for `build:mock`; adds 200 kB to dev install. Phase 8 ticket (FE-040) owns adding the dep and wiring the service worker. |
| 7 | `vite.config.ts` base path `/networth/` kept as-is | Set for GitHub Pages deployment; no change needed |
| 8 | `src/api/` filenames follow CLAUDE.md exactly: `setting.ts`, `cashFlow.ts`, `yearReport.ts`, `otherAssets.ts`, `dashboard.ts` | Canonical names from view/CLAUDE.md §3; utilities.ts is an approved addition (see #5) |
