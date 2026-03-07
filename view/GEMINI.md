# Balance Sheet View — Developer Conventions

---

## Tech Stack Quick Reference

| What | Where |
|------|-------|
| Framework | Vue 3, `<script setup lang="ts">` |
| UI Components | Element Plus 2.x |
| CSS | Tailwind v4 (utilities only) + Element Plus CSS vars in `src/assets/main.css` |
| State | Pinia stores in `src/stores/` |
| Router | Vue Router 4, config in `src/router/index.ts` |
| HTTP | Axios via `src/utils/request.ts` — never call axios directly |
| Types | `src/types/models.ts` — all data models |
| Charts | ECharts 5 via `vue-echarts` |
| Mock | MSW in `src/api/mock/` (active when `VITE_USE_MOCK=true`) |

---

## Key File Locations

```
src/
  assets/main.css         ← Global CSS, Tailwind imports, Element Plus CSS vars
  utils/request.ts        ← Axios instance, interceptors, error handling
  utils/currency.ts       ← formatCurrency(), moneyClass()
  utils/date.ts           ← date helpers using Day.js
  types/models.ts         ← ALL TypeScript interfaces
  stores/                 ← Pinia stores (one per domain)
  components/layout/      ← AppLayout, Sidebar, SidebarContent, Navbar
  components/charts/      ← chart components
  components/ui/          ← shared UI: MoneyDisplay, Pagination, SearchFilter, FormDialog
```

---

## Project-Specific Implementation Rules

### DO:
- Use `formatCurrency()` from `src/utils/currency.ts` for all money values
- Use `<el-message>` / `<el-notification>` for user feedback, never `alert()`
- Apply Tailwind for layout/spacing, Element Plus CSS vars for theming
- Run `npm run type-check` before submitting a PR

### DO NOT:
- Inline TypeScript interfaces — always reference `src/types/models.ts`
- Call `axios` directly — always use `src/utils/request.ts`
- Create new files in `src/stores/`, `src/router/`, or `src/api/` without Claude's approval
- Change mock data unless the task explicitly requires it

---

## Common Pitfalls in This Project

| Problem | Fix |
|---------|-----|
| Reactive data not updating | Check Pinia state — mutate via actions, not directly |
| `ref` vs `reactive` confusion | Use `ref()` for primitives, `reactive()` for objects |
| Element Plus table blank | `el-table-column` `prop` must match data key; `:data` must be array |
| ECharts blank on first render | Container needs explicit width/height; use `autoresize` prop |
| Tailwind class ignored | No preflight in v4 — don't expect CSS resets |
| Element Plus style override | Use CSS variables in `:root {}`, not Tailwind on `<el-*>` |
| TypeScript error after data change | Update `src/types/models.ts` first, then mock data |
