# Frontend Refactor — Implementation Guide

> **Audience:** the AI session running **Step 3 — implementation** of the
> frontend refactor (`view/` SPA).
> **Goal:** rebuild the personal-finance SPA against the new
> `networth-api` contract, executing one phase per session driven by the
> granular tickets under `frontend-refactoring-tickets/granular/`.

This document mirrors the backend
[`refactoring-tickets/IMPLEMENTATION_GUIDE.md`](../refactoring-tickets/IMPLEMENTATION_GUIDE.md);
read both before starting. The differences below are deliberate, not
oversights.

---

## Before you start

Read these first — they are your full context. Backend implementation
files in `api/app/**` are NOT part of this list and must not be opened.

1. `frontend-refactoring-tickets/README.md` — phase order, dependency
   graph, decision log.
2. `view/CLAUDE.md` — frontend architecture, naming, store/API/component
   boundaries (non-negotiable).
3. **`api/docs/api-reference.md`** — slim **index** of the API spec. It
   lists every sub-router along with the path of its detailed markdown
   and JSON slice. Always read this first to find the right slice; do
   not infer endpoints from anywhere else.
4. **`api/docs/api-reference/<domain>/<sub-router>.md`** — the primary
   per-sub-router contract you actually consume. Each file is
   self-contained (request, response, errors, examples) and capped at
   ~500 lines. Read **only** the sub-routers your ticket touches;
   reading every file is wasteful.
5. **`api/docs/openapi/<domain>/<sub-router>.json`** — paths-only JSON
   slice for the same sub-router; use it as drill-down when the
   markdown is ambiguous.
6. **`api/docs/openapi/schemas/<SchemaName>.json`** — one OpenAPI doc
   per Pydantic model. The matching sub-router JSON lists which schema
   files it depends on under the `x-schema-files` key. Load only the
   schemas you need.
7. **`api/docs/openapi/_shared.json`** — `ApiError` + framework
   validation schemas, shared by every sub-router (referenced from
   each slice's `x-shared-file`).
8. `frontend-refactoring-tickets/granular/FE-NNN.md` — for every ticket
   in this session's phase scope.
9. **`POST_FRONTEND_TODO.md` §3** — the deferred-fields checklist. Each
   row tells you whether the field is used by some legacy view; you are
   responsible for confirming `keep` vs `drop` as you implement.

Do **not** read:
- `api/app/**`, `api/tests/**` — frontend treats the backend as a black
  box. If `api-reference.md` is missing something you need, fix the
  spec via a backend follow-up ticket — do not reach into the
  implementation.
- `account-book-API/` — legacy backend, irrelevant.
- `account-book-view/` — legacy frontend, **read only** when a granular
  file's Notes explicitly cite a legacy view for confirmation.

---

## Session scoping

Execute **one phase per session**. The phase table is owned by
`frontend-refactoring-tickets/README.md`; it should look something like:

| Session | Phase | Tickets | Gate at end |
|---------|-------|---------|-------------|
| 1 | Phase 0 | FE-001..00X | `npm run dev` starts; `/api` proxy reachable |
| 2 | Phase 1 | FE-0XX..0YY | type-check passes; `src/types/models.ts` matches `api-reference.md` |
| ... | ... | ... | ... |

(The README owns the canonical numbers; this guide just states the
session-per-phase rule.)

---

## Execution rules

1. **Process granular sub-tasks top-to-bottom.** Within a ticket, complete
   each row of the sub-task table before moving on.
2. **Run the Acceptance command after every sub-task.** If it fails, fix
   the root cause before proceeding — do not skip, do not defer.
3. **Respect dependencies.** Tickets within a phase are listed in the
   README in dependency order; do not reorder.
4. **Commit per ticket, not per sub-task.** One commit per FE-NNN with
   message `FE-NNN: <title>`.
5. **English** for code, comments, OpenAPI / type-doc text, commit
   messages. Traditional Chinese only in user-facing conversation.
6. **Do not invent scope.** If a granular file doesn't spell it out, it's
   not in scope. Flag the gap in the session summary instead of
   improvising.
7. **API contract is fixed.** Treat `api/docs/api-reference.md` and
   every file under `api/docs/api-reference/` and `api/docs/openapi/`
   as read-only spec. If something is missing, stop and flag it for
   a backend follow-up; do not work around it client-side.

---

## Sub-router → ticket map

Use this when picking which API spec slice(s) to read for a given ticket.
Entries that span a whole domain (e.g. `FE-003`) read every sub-router
under that domain; per-feature tickets read only the row(s) listed.

| Sub-router (read `api-reference/<path>.md` + matching `openapi/<path>.json`) | Primary tickets |
|------------------------------------------------------------------------------|-----------------|
| `settings/accounts` | FE-002, FE-003, FE-008, FE-034 |
| `settings/alarms` | FE-002, FE-003, FE-008, FE-038 |
| `settings/budgets` | FE-002, FE-003, FE-008, FE-037 |
| `settings/codes`, `settings/codes-tree`, `settings/sub-codes` | FE-002, FE-003, FE-008, FE-035 |
| `settings/credit-cards` | FE-002, FE-003, FE-008, FE-036 |
| `monthly-report/journals` | FE-002, FE-005, FE-010, FE-021, FE-022 |
| `monthly-report/journals-analytics` | FE-005, FE-023 |
| `monthly-report/balance` | FE-005, FE-024 |
| `monthly-report/stock-prices` | FE-005, FE-024 |
| `assets/stocks`, `assets/stocks-details` | FE-002, FE-007, FE-012, FE-028, FE-029 |
| `assets/estates`, `assets/estates-details` | FE-002, FE-007, FE-012, FE-030 |
| `assets/insurances`, `assets/insurances-details` | FE-002, FE-007, FE-012, FE-031 |
| `assets/loans`, `assets/loans-details`, `assets/loans-selection` | FE-002, FE-007, FE-012, FE-032 |
| `assets/other-assets` | FE-002, FE-007, FE-012, FE-033 |
| `reports/balance` | FE-006, FE-011, FE-025 |
| `reports/expenditure` | FE-006, FE-011, FE-026 |
| `reports/assets` | FE-006, FE-011, FE-027 |
| `dashboard/summary` | FE-004, FE-009, FE-017 |
| `dashboard/alarms` | FE-004, FE-009, FE-018 |
| `dashboard/targets` | FE-004, FE-009, FE-019 |
| `dashboard/budget`, `dashboard/gifts` | FE-004, FE-009, FE-020 |
| `utilities/selections` | FE-004 (utilities), FE-022 (journal form dropdowns) |
| `utilities/import` | FE-004 (utilities), FE-039 |
| `health` | — (smoke test only) |

---

## Cross-cutting requirements (re-stated from `view/CLAUDE.md`)

Every Vue component:
- Uses `<script setup lang="ts">`. No Options API. No
  `defineComponent()`.

Every store:
- Lives in `src/stores/<domain>.ts`, one per domain, never imports another
  store.
- Exposes `data` + `loading` + async `fetchX()` per the documented pattern.

Every HTTP call:
- Goes through `src/api/<domain>.ts`. Components and stores never call
  `axios` directly.

Every data type:
- Lives in `src/types/models.ts`. No inline `interface` declarations
  outside this file.

Every layout / interaction split:
- Tailwind for layout, Element Plus for interaction. Never `!important`
  Element Plus styles.

Every page:
- Lives in `src/views/*View.vue` and owns its store subscription;
  `src/components/charts/**` are stateless prop-driven wrappers.

---

## POST_FRONTEND_TODO.md §3 — hard gate

This is the part **unique to the frontend refactor**.

`POST_FRONTEND_TODO.md` §3 is a checklist of backend fields whose fate
(`keep` vs `drop`) was deliberately deferred until the frontend declared
its needs. As you implement views, you will be the first agent to know
which fields a UI actually consumes.

### What each granular ticket must declare

When the granularization step (Step 2) writes a ticket that touches any
field in §3, the granular file's **Notes** section must list those rows
explicitly, e.g.:

> **POST_FRONTEND_TODO.md §3 rows touched:**
> `Account.discount`, `Account.account_index`.

If a granular ticket has no such note, assume it touches no §3 row.

### What the implementing AI must do per touched row

For every §3 row listed in the ticket Notes:

1. After implementing the relevant view / store, decide whether the field
   is actually rendered or used in business logic. "Loaded but unused" =
   `drop`.
2. Edit `POST_FRONTEND_TODO.md` §3 in the same commit as the ticket:
   - Set `Verified at` to the view path or component (e.g.
     `view/src/views/AccountSettingsView.vue`).
   - Set `Decision` to `keep` or `drop`.
   - Set `Frontend commit` to the short hash of the ticket commit
     (you can use a placeholder and amend after `git commit`).
3. Do not edit other rows.

### Phase-exit gate

Before declaring a phase done, in addition to the standard gate (see
below), verify:

- Every §3 row that any granular ticket in this phase listed under
  "rows touched" has a non-`_pending_` value in **all three** mutable
  columns.
- The session summary includes a section
  `## §3 updates this phase` listing the rows changed and the
  `keep` / `drop` decision per row.

If any §3 row was touched de-facto but not listed in a ticket's Notes,
fix the ticket's Notes (and its commit message) to match reality before
the phase closes.

---

## Phase-exit checklist

Before declaring the session done:

1. All Acceptance commands in scope pass.
2. `cd view && npm run type-check` passes (zero errors). If a phase has
   an additional gate (e.g. golden-file UI snapshot), the README states
   it.
3. `cd view && npm run dev` still starts without console errors against
   the live API at `localhost:9528` (or against
   `VITE_USE_MOCK=true` if that's the phase scope).
4. `cd view && npm run build` succeeds.
5. No file written in `api/`, `account-book-API/`, or
   `account-book-view/`.
6. **`POST_FRONTEND_TODO.md` §3 updated** for every row that any ticket
   in this phase declared as "touched". If any row remains `_pending_`,
   the phase is **not** done.
7. Commit(s) pushed, one per ticket.
8. Session summary lists: tickets completed, type-check status,
   §3 rows updated this phase, any flagged gaps.

---

## When things go wrong

- **Granular file is ambiguous or contradicts source ticket**: trust the
  granular file's Notes if it explicitly cites legacy / API-spec
  confirmation; otherwise read the parent ticket and record the
  resolution in the session summary.
- **Acceptance command fails and you can't figure out why**: stop, report
  in the session summary. Do not disable the test or weaken the command.
- **API contract is missing or wrong**: do not work around it in the
  frontend. Stop, write a one-line "needs backend follow-up" entry in
  the session summary, and continue with whatever doesn't depend on it.
- **§3 row decision is unclear** (e.g. "field is shown only as a tooltip,
  is that 'used'?"): default to `keep` and explain in the row's
  `Verified at` cell. The cleanup ticket BE-B03 (per
  `POST_FRONTEND_TODO.md` §3 closing note) is where ambiguous-keep rows
  get a second look.
- **Scope creep urge** (spotting something worth fixing outside the
  ticket): do not fix it in this session — note it at the end so the
  user can decide whether to open a follow-up ticket.

---

## Prompt template for each Step 3 session

Paste this when starting a session (replace `<N>` and `<FE-XXX..FE-YYY>`):

```
讀取以下檔案作為完整 context：
- frontend-refactoring-tickets/IMPLEMENTATION_GUIDE.md
- frontend-refactoring-tickets/README.md
- view/CLAUDE.md
- api/docs/api-reference.md  ← 讀 index 找到該 ticket 對應的 sub-router 檔案
- POST_FRONTEND_TODO.md
- frontend-refactoring-tickets/granular/FE-XXX.md 到 FE-YYY.md

本 session 執行 Phase <N>（FE-XXX..FE-YYY）。依 IMPLEMENTATION_GUIDE 規則
逐題實作；每張 ticket 透過 IMPLEMENTATION_GUIDE 的「Sub-router → ticket map」
找到該題對應的 api-reference/<domain>/<sub>.md 與 openapi/<domain>/<sub>.json
切片再讀（不要讀整個 spec）。
每張 ticket 若 Notes 列出 POST_FRONTEND_TODO.md §3 的 rows，
實作完成需在同一個 commit 內把該 rows 更新為 keep/drop 並填上
Verified at + Frontend commit。結束時回報 phase-exit checklist 結果，
含「§3 updates this phase」一節。
```
