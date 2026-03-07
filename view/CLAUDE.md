# Balance Sheet View — Architecture & Conventions

---

## Architecture Principles

### 1. Composition API only
All components use `<script setup lang="ts">`. No Options API. No `defineComponent()`.

### 2. Pinia stores — flat, domain-scoped
Each business domain has exactly one store. No store imports another store.

```
src/stores/
  app.ts          ← UI state only (sidebar, locale) — no business logic
  dashboard.ts    ← Dashboard summary data
  cashFlow.ts     ← Monthly cash flow report
  yearReport.ts   ← Balance sheet, spending, asset overview
  otherAssets.ts  ← Stocks, estate, insurance, liability, other assets
  setting.ts      ← Accounts, codes, credit cards, budgets, reminders
```

**Store pattern:**
```typescript
export const useXxxStore = defineStore('xxx', () => {
  const data = ref<DataType | null>(null)
  const loading = ref(false)

  async function fetchData(params: ParamsType) {
    loading.value = true
    try {
      data.value = await apiXxx.getData(params)
    } finally {
      loading.value = false
    }
  }

  return { data, loading, fetchData }
})
```

### 3. API layer separation
All HTTP calls go through `src/api/`. Components and stores never call `axios` directly.

```
src/api/
  dashboard.ts       ← getDashboardSummary(), getAlarms()
  cashFlow.ts        ← getCashFlow(), updateStockPrice()
  yearReport.ts      ← getBalanceSheet(), getSpending(), getAssets()
  otherAssets.ts     ← CRUD for stocks, estate, insurance, liability, other
  setting.ts         ← CRUD for accounts, codes, creditCards, budgets, reminders
  mock/
    handlers.ts      ← MSW handlers (activated when VITE_USE_MOCK=true)
    data/            ← Static JSON mock data files
```

### 4. TypeScript types — single source of truth
All data models in `src/types/models.ts`. No inline interface definitions anywhere else.

### 5. Tailwind for layout, Element Plus for interaction
- **Tailwind**: page layout, spacing, grid, flex, color utilities, typography
- **Element Plus**: Table, Form, Dialog, DatePicker, Select, Tabs, Pagination, Notification
- Theme customization: CSS variables in `src/assets/main.css` `:root {}` block only
- Never fight Element Plus styles with Tailwind `!important`

### 6. Component responsibility boundaries
```
src/components/
  layout/        ← AppLayout, Sidebar, SidebarContent, Navbar
  charts/        ← Stateless chart wrappers (LineChart, BarChart, PieChart, etc.)
  ui/            ← Reusable UI primitives (MoneyDisplay, Pagination, FormDialog, etc.)

src/views/
  *View.vue      ← Page components — own their store subscription and data loading
  */             ← Sub-components scoped to that view only
```

**Charts are stateless** — they receive data via props, emit nothing.
**Views own state** — they subscribe to stores and pass data down to components.

### 7. Project-specific naming
- Vue files: `PascalCase.vue`
- TypeScript files: `camelCase.ts`
- Views: suffix `View` (e.g., `DashboardView.vue`)
- Stores: `use` + noun + `Store` (e.g., `useAppStore`)
- Composables: `use` + verb/noun (e.g., `useChart`)
- API functions: verb + noun (e.g., `getBalanceSheet`, `createAccount`)

---

## Project Overview

**Balance Sheet View** — personal financial management SPA for tracking:
- Monthly cash flow (income/expense vs budget)
- Annual balance sheet (assets vs liabilities)
- Asset management (stocks, real estate, insurance, loans)
- Budget and reminder settings

No authentication required. Full spec: `PROJECT_ANALYSIS.md`.

---

## Tech Stack

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
| Date | Day.js |
| Utils | @vueuse/core |

---

## Environment & Commands

```env
VITE_API_BASE_URL=/api          # proxied to localhost:9528 in dev
VITE_USE_MOCK=false             # true for GitHub Pages mock mode
```

```bash
npm run dev          # http://127.0.0.1:5173
npm run build        # production build
npm run build:mock   # GitHub Pages build with mock data
npm run type-check   # TypeScript check (must pass before any PR)
```

---

## GitHub Pages Mock Strategy

When `VITE_USE_MOCK=true`:
- MSW intercepts all `/api/*` requests in the browser
- Mock handlers: `src/api/mock/handlers.ts`
- Mock data: `src/api/mock/data/*.json`
