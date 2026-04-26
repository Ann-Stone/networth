# Networth API Reference

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

- OpenAPI version: `3.1.0`
- API version: `0.1.0`

## Table of Contents

- [Settings](#settings)
- [Monthly Report](#monthly-report)
- [Assets](#assets)
- [Reports](#reports)
- [Dashboard](#dashboard)
- [Utilities](#utilities)
- [Health](#health)

## Settings

### GET /settings/accounts

**List accounts**

List accounts with optional filters on name, account_type, in_use.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| name | query |  | no | Name substring filter |
| account_type | query |  | no | Account type filter |
| in_use | query |  | no | In-use flag filter |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### POST /settings/accounts

**Create account**

Create an account. Rejects 422 when account_id is missing; 409 when account_id duplicates existing row.

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| account_id | string | yes | User-supplied business identifier |
| name | string | yes | Account name |
| account_type | string | yes | Account type |
| fx_code | string | yes | Currency code |
| is_calculate | string | no | Include in totals (Y/N) |
| in_use | string | no | Active flag (Y/N) |
| discount | number | no | Discount multiplier |
| memo |  | no | Free-form memo |
| owner |  | no | Owner label |
| account_index |  | no | Optional sort order; auto-filled with max(account_index)+1 when omitted |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /settings/accounts/selection

**Active accounts for dropdown**

Return in-use accounts ordered by account_index ASC for use in dropdowns.

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### DELETE /settings/accounts/{id}

**Delete account**

Delete an account by autoincrement id. Returns 404 if id not found.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| id | path | integer | yes |  |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### PUT /settings/accounts/{id}

**Update account**

Update an account by autoincrement id. Returns 404 if id not found.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| id | path | integer | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| account_id |  | no | Business identifier |
| name |  | no | Account name |
| account_type |  | no | Account type |
| fx_code |  | no | Currency code |
| is_calculate |  | no | Include in totals (Y/N) |
| in_use |  | no | Active flag (Y/N) |
| discount |  | no | Discount multiplier |
| memo |  | no | Free-form memo |
| owner |  | no | Owner label |
| account_index |  | no | Dropdown order |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /settings/alarms

**List all alarms**

List every alarm ordered by alarm_id ASC.

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### POST /settings/alarms

**Create alarm**

Create an alarm. due_date accepts multiple formats (ISO 8601, YYYY-MM-DD, YYYYMMDD) and is persisted normalized as YYYYMMDD.

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| alarm_type | string | yes | Reminder category |
| alarm_date | string | yes | YYYYMMDD |
| content | string | yes | Reminder text |
| due_date |  | no | YYYYMMDD |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /settings/alarms/by-date

**List alarms matching a date**

Return alarms whose alarm_date equals the query date (e.g. 08/26) or ends with it (e.g. monthly day 26 matches).

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| date | query | string | yes | Date in MM/DD or DD form |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### DELETE /settings/alarms/{alarm_id}

**Delete alarm**

Delete an alarm by alarm_id. Returns 404 if not found.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| alarm_id | path | integer | yes |  |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### PUT /settings/alarms/{alarm_id}

**Update alarm**

Update an alarm by alarm_id. Returns 404 if not found. due_date is re-normalized when provided.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| alarm_id | path | integer | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| alarm_type |  | no | Reminder category |
| alarm_date |  | no | YYYYMMDD |
| content |  | no | Reminder text |
| due_date |  | no | YYYYMMDD |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### PUT /settings/budgets

**Bulk update budgets**

Update multiple Budget rows in one call. Each item is matched by (budget_year, category_code). Transactional — if any row is missing, all updates are rolled back.

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /settings/budgets/year-range

**Available budget years**

Return distinct budget_year values present in Budget, ascending.

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /settings/budgets/{year}

**Budgets for a year**

Return all Budget rows for the given year ordered by category_code.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| year | path | integer | yes |  |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### POST /settings/budgets/{year}/copy-from-previous

**Copy budget from previous year journal**

Compute budget for {year} by averaging the previous year's Journal amounts per action_main_type across 12 months, then upsert into Budget.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| year | path | integer | yes |  |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /settings/codes

**List main codes**

List all main (top-level) codes ordered by code_index.

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### POST /settings/codes

**Create main code**

Create a main code. If code_type is Fixed or Floating, a Budget row for the current year is auto-inserted with all monthly amounts set to 0.

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| code_id | string | yes | Business identifier |
| code_type | string | yes | Code category: Fixed / Floating / Invest / Income / Transfer / etc. |
| name | string | yes | Display name |
| parent_id |  | no | Parent code id; null for main codes |
| code_group |  | no | Group code |
| code_group_name |  | no | Group name |
| in_use | string | no | Active flag |
| code_index |  | no | Dropdown order; auto-filled with max+1 when omitted |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /settings/codes/all-with-sub

**Full code tree**

Return all main codes with their sub-codes nested under sub_codes.

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### DELETE /settings/codes/{code_id}

**Delete main code**

Delete a main code by code_id. Returns 404 if not found.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| code_id | path | string | yes |  |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### PUT /settings/codes/{code_id}

**Update main code**

Update a main code by code_id. Returns 404 if not found.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| code_id | path | string | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| code_type |  | no | code type |
| name |  | no | Display name |
| parent_id |  | no | Parent code id |
| code_group |  | no | Group code |
| code_group_name |  | no | Group name |
| in_use |  | no | Active flag |
| code_index |  | no | Dropdown order |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /settings/codes/{parent_id}/sub-codes

**List sub-codes of a parent**

List sub-codes belonging to a main code, ordered by code_index.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| parent_id | path | string | yes |  |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /settings/credit-cards

**List credit cards**

List credit cards with optional filters on card_name (substring) and in_use. Ordered by credit_card_index ASC.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| card_name | query |  | no | Card name substring filter |
| in_use | query |  | no | Active flag filter Y/N |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### POST /settings/credit-cards

**Create credit card**

Create a credit card. When credit_card_index is omitted, auto-fill with max(credit_card_index)+1.

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| credit_card_id | string | yes | Business identifier |
| card_name | string | yes | Display name |
| card_no |  | no | Card number |
| last_day |  | no | Statement cut-off day |
| charge_day |  | no | Charge day |
| limit_date |  | no | Payment due day |
| feedback_way |  | no | Rewards method |
| fx_code | string | yes | Billing currency code |
| in_use | string | no | Active flag |
| credit_card_index |  | no | Sort order; auto-filled with max+1 when omitted |
| note |  | no | Free-form note |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### DELETE /settings/credit-cards/{credit_card_id}

**Delete credit card**

Delete a credit card by credit_card_id. Returns 404 if not found.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| credit_card_id | path | string | yes |  |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### PUT /settings/credit-cards/{credit_card_id}

**Update credit card**

Update a credit card by credit_card_id. Returns 404 if not found.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| credit_card_id | path | string | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| card_name |  | no | Display name |
| card_no |  | no | Card number |
| last_day |  | no | Statement cut-off day |
| charge_day |  | no | Charge day |
| limit_date |  | no | Payment due day |
| feedback_way |  | no | Rewards method |
| fx_code |  | no | Billing currency code |
| in_use |  | no | Active flag |
| credit_card_index |  | no | Dropdown order |
| note |  | no | Free-form note |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### POST /settings/sub-codes

**Create sub-code**

Create a sub-code. parent_id must reference an existing main code (404 otherwise).

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| code_id | string | yes | Business identifier |
| code_type | string | yes | Code category: Fixed / Floating / Invest / Income / Transfer / etc. |
| name | string | yes | Display name |
| parent_id |  | no | Parent code id; null for main codes |
| code_group |  | no | Group code |
| code_group_name |  | no | Group name |
| in_use | string | no | Active flag |
| code_index |  | no | Dropdown order; auto-filled with max+1 when omitted |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### DELETE /settings/sub-codes/{code_id}

**Delete sub-code**

Delete a sub-code by code_id. Returns 404 if not found. No cascading.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| code_id | path | string | yes |  |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### PUT /settings/sub-codes/{code_id}

**Update sub-code**

Update a sub-code by code_id. Returns 404 if not found.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| code_id | path | string | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| code_type |  | no | code type |
| name |  | no | Display name |
| parent_id |  | no | Parent code id |
| code_group |  | no | Group code |
| code_group_name |  | no | Group name |
| in_use |  | no | Active flag |
| code_index |  | no | Dropdown order |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

## Monthly Report

### PUT /monthly-report/balance/{vesting_month}/settle

**Run monthly balance settlement**

Snapshot every asset/liability net value for the vesting month. Idempotent: per-asset-type tables are delete+reinsert; AccountBalance and CreditCardBalance use cascade-delete from the target month forward to invalidate later carry-forward snapshots.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| vesting_month | path | string | yes | YYYYMM |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### POST /monthly-report/journals

**Create a journal entry**

Persist a new Journal row. distinct_number is auto-assigned.

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| vesting_month | string | yes | YYYYMM |
| spend_date | string | yes | YYYYMMDD |
| spend_way | string | yes | Payment source id |
| spend_way_type | string | yes | account / credit_card |
| spend_way_table | string | yes | Source table of spend_way |
| action_main | string | yes | Main code |
| action_main_type | string | yes | Main code type |
| action_main_table | string | yes | Source table of action_main |
| action_sub |  | no | Secondary code |
| action_sub_type |  | no | Secondary code type |
| action_sub_table |  | no | Secondary code source table |
| spending | number | yes | Positive = income, negative = expense |
| invoice_number |  | no | Invoice number |
| note |  | no | Free-form note |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### DELETE /monthly-report/journals/{journal_id}

**Delete a journal entry**

Delete a Journal identified by distinct_number.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| journal_id | path | integer | yes |  |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### PUT /monthly-report/journals/{journal_id}

**Update a journal entry**

Partial update of a Journal identified by distinct_number.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| journal_id | path | integer | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| vesting_month |  | no | YYYYMM |
| spend_date |  | no | YYYYMMDD |
| spend_way |  | no | Payment source id |
| spend_way_type |  | no | account / credit_card |
| spend_way_table |  | no | Source table of spend_way |
| action_main |  | no | Main code |
| action_main_type |  | no | Main code type |
| action_main_table |  | no | Source table of action_main |
| action_sub |  | no | Secondary code |
| action_sub_type |  | no | Secondary code type |
| action_sub_table |  | no | Secondary code source table |
| spending |  | no | Signed amount |
| invoice_number |  | no | Invoice number |
| note |  | no | Free-form note |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /monthly-report/journals/{vesting_month}

**List journals for a month with gain/loss**

Return all Journal entries whose vesting_month matches the path parameter, ordered by spend_date. The response also includes the FX-converted gain/loss total for the month.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| vesting_month | path | string | yes |  |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /monthly-report/journals/{vesting_month}/expenditure-budget

**Actual vs budget per category**

Compare expected (Budget.expected<MM>) vs actual (Journal.spending sum) per category, returning diff and usage_rate.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| vesting_month | path | string | yes |  |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /monthly-report/journals/{vesting_month}/expenditure-ratio

**Monthly expenditure ratio (inner/outer pie)**

Return outer/inner aggregations of journal spending for the given month. Outer = grouped by action_main_type; inner = grouped by action_sub_type. Excludes 'invest' and 'transfer' main types.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| vesting_month | path | string | yes |  |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /monthly-report/journals/{vesting_month}/invest-ratio

**Monthly invest ratio**

Aggregate journal spending whose action_main_type == 'invest', grouped by action_sub_type.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| vesting_month | path | string | yes |  |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /monthly-report/journals/{vesting_month}/liability

**Credit-card liability breakdown**

Aggregate journal spending whose spend_way_type == 'credit_card', grouped by credit card.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| vesting_month | path | string | yes |  |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### POST /monthly-report/stock-prices

**Insert a stock price record (optionally fetch yfinance)**

Persist a new StockPriceHistory row. When trigger_yfinance is True the close price is overwritten by yfinance.

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| stock_code | string | yes | Ticker symbol |
| fetch_date | string | yes | YYYYMMDD |
| open_price | number | yes | Open price |
| highest_price | number | yes | Daily high |
| lowest_price | number | yes | Daily low |
| close_price | number | yes | Close price (overwritten when trigger_yfinance is True) |
| trigger_yfinance | boolean | no | When True, fetch close price from yfinance and overwrite close_price. |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /monthly-report/stock-prices/{vesting_month}

**Month-level closing prices for held stocks**

For every stock present in the holdings table, return the most recent StockPriceHistory close on or before month-end (falling back to the latest prior row when the month has none).

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| vesting_month | path | string | yes | YYYYMM |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

## Assets

### GET /assets/estates

**List real-estate holdings**

Return estate properties filtered by asset_id.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| asset_id | query | string | yes | Parent asset category id |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### POST /assets/estates

**Create real-estate holding**

Create a new estate property; obtain_date accepts ISO 8601 and is stored as YYYYMMDD.

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| estate_id | string | yes | Estate business ID |
| estate_name | string | yes | Estate display name |
| estate_type | string | yes | Estate type |
| estate_address | string | yes | Physical address |
| asset_id | string | yes | Asset category ID |
| obtain_date | string | yes | YYYYMMDD |
| loan_id |  | no | Associated loan ID |
| estate_status | string | yes | Status |
| memo |  | no | Free-form memo |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### DELETE /assets/estates/details/{distinct_number}

**Delete estate transaction**

Delete a single estate transaction row.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| distinct_number | path | integer | yes |  |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### PUT /assets/estates/details/{distinct_number}

**Update estate transaction**

Update a single estate transaction row.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| distinct_number | path | integer | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| estate_excute_type |  | no | Transaction type |
| excute_price |  | no | Amount |
| excute_date |  | no | YYYYMMDD |
| memo |  | no | Free-form memo |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### DELETE /assets/estates/{estate_id}

**Delete real-estate holding**

Delete an estate property by id.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| estate_id | path | string | yes |  |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### PUT /assets/estates/{estate_id}

**Update real-estate holding**

Update an estate property; any omitted field is left unchanged.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| estate_id | path | string | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| estate_name |  | no | Estate display name |
| estate_type |  | no | Estate type |
| estate_address |  | no | Physical address |
| asset_id |  | no | Asset category ID |
| obtain_date |  | no | YYYYMMDD |
| loan_id |  | no | Associated loan ID |
| estate_status |  | no | Status |
| memo |  | no | Free-form memo |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /assets/estates/{estate_id}/details

**List estate transactions**

Return all fee/tax/rent/deposit transactions for an estate property.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| estate_id | path | string | yes |  |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### POST /assets/estates/{estate_id}/details

**Record estate transaction**

Record a tax/fee/insurance/fix/rent/deposit transaction.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| estate_id | path | string | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| estate_id | string | yes | FK to Estate.estate_id |
| estate_excute_type | string | yes | tax/fee/insurance/fix/rent/deposit |
| excute_price | number | yes | Amount |
| excute_date | string | yes | YYYYMMDD |
| memo |  | no | Free-form memo |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /assets/insurances

**List insurance policies**

Return policies under a given asset_id.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| asset_id | query | string | yes | Parent asset category id |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### POST /assets/insurances

**Create insurance policy**

Create a policy; start/end dates accept ISO 8601 and are stored as YYYYMMDD.

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| insurance_id | string | yes | Policy business ID |
| insurance_name | string | yes | Policy display name |
| asset_id | string | yes | Asset category ID |
| in_account | string | yes | Paying account id |
| out_account | string | yes | Disbursing account id |
| start_date | string | yes | YYYYMMDD |
| end_date | string | yes | YYYYMMDD |
| pay_type | string | yes | Premium cadence |
| pay_day | integer | yes | Day of month |
| expected_spend | number | yes | Expected premium |
| has_closed | string | yes | Closed flag (Y/N) |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### DELETE /assets/insurances/details/{distinct_number}

**Delete insurance transaction**

Delete a single insurance transaction row.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| distinct_number | path | integer | yes |  |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### PUT /assets/insurances/details/{distinct_number}

**Update insurance transaction**

Update a single insurance transaction row.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| distinct_number | path | integer | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| insurance_excute_type |  | no | Execution type |
| excute_price |  | no | Amount |
| excute_date |  | no | YYYYMMDD |
| memo |  | no | Free-form memo |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### DELETE /assets/insurances/{insurance_id}

**Delete insurance policy**

Delete a policy by id.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| insurance_id | path | string | yes |  |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### PUT /assets/insurances/{insurance_id}

**Update insurance policy**

Update a policy by id; any omitted field is left unchanged.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| insurance_id | path | string | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| insurance_name |  | no | Policy display name |
| asset_id |  | no | Asset category ID |
| in_account |  | no | Paying account id |
| out_account |  | no | Disbursing account id |
| start_date |  | no | YYYYMMDD |
| end_date |  | no | YYYYMMDD |
| pay_type |  | no | Premium cadence |
| pay_day |  | no | Day of month |
| expected_spend |  | no | Expected premium |
| has_closed |  | no | Closed flag |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /assets/insurances/{insurance_id}/details

**List insurance transactions**

Return all premium/claim/return transactions for a policy.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| insurance_id | path | string | yes |  |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### POST /assets/insurances/{insurance_id}/details

**Record insurance premium/claim**

Record a pay/cash/return/expect transaction.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| insurance_id | path | string | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| insurance_id | string | yes | FK to Insurance.insurance_id |
| insurance_excute_type | string | yes | pay/cash/return/expect |
| excute_price | number | yes | Amount |
| excute_date | string | yes | YYYYMMDD |
| memo |  | no | Free-form memo |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /assets/loans

**List loans**

Return all loan liabilities ordered by loan_index.

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### POST /assets/loans

**Create loan**

Create a new loan liability; dates accept ISO 8601 and are stored as YYYYMMDD.

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| loan_id | string | yes | Loan business ID |
| loan_name | string | yes | Loan display name |
| loan_type | string | yes | Loan type |
| account_id | string | yes | Repayment account business ID |
| account_name | string | yes | Repayment account display name |
| interest_rate | number | yes | Annual interest rate |
| period | integer | yes | Loan period in months |
| apply_date | string | yes | YYYYMMDD |
| grace_expire_date |  | no | Grace period end |
| pay_day | integer | yes | Day of month for repayment |
| amount | number | yes | Original loan amount |
| repayed | number | yes | Cumulative principal repaid |
| loan_index | integer | yes | Dropdown order |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### DELETE /assets/loans/details/{distinct_number}

**Delete loan transaction**

Delete a single loan transaction row; Loan.repayed auto-recalculates.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| distinct_number | path | integer | yes |  |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### PUT /assets/loans/details/{distinct_number}

**Update loan transaction**

Update a single loan transaction row; Loan.repayed auto-recalculates.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| distinct_number | path | integer | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| loan_excute_type |  | no | Execution type |
| excute_price |  | no | Amount |
| excute_date |  | no | YYYYMMDD |
| memo |  | no | Free-form memo |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /assets/loans/selection

**Loan dropdown options**

Return id/name pairs for loan selection UIs.

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### DELETE /assets/loans/{loan_id}

**Delete loan**

Delete a loan by id.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| loan_id | path | string | yes |  |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /assets/loans/{loan_id}

**Get loan**

Return a single loan by id.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| loan_id | path | string | yes |  |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### PUT /assets/loans/{loan_id}

**Update loan**

Update a loan; repayed is server-computed and cannot be set via this endpoint.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| loan_id | path | string | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| loan_name |  | no | Loan display name |
| loan_type |  | no | Loan type |
| account_id |  | no | Repayment account business ID |
| account_name |  | no | Repayment account display name |
| interest_rate |  | no | Annual interest rate |
| period |  | no | Loan period in months |
| apply_date |  | no | YYYYMMDD |
| grace_expire_date |  | no | Grace period end |
| pay_day |  | no | Day of month for repayment |
| amount |  | no | Original loan amount |
| repayed |  | no | Cumulative principal repaid |
| loan_index |  | no | Dropdown order |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /assets/loans/{loan_id}/details

**List loan transactions**

Return all repayment / interest / fee / increment transactions for a loan.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| loan_id | path | string | yes |  |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### POST /assets/loans/{loan_id}/details

**Record loan transaction**

Record a principal/interest/increment/fee transaction. Server auto-recalculates Loan.repayed on principal rows.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| loan_id | path | string | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| loan_id | string | yes | FK to Loan.loan_id |
| loan_excute_type | string | yes | principal/interest/increment/fee |
| excute_price | number | yes | Amount |
| excute_date | string | yes | YYYYMMDD |
| memo |  | no | Free-form memo |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /assets/other-assets

**List asset categories**

Return all asset categories ordered by asset_index ascending (drives dropdown order).

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### POST /assets/other-assets

**Create asset category**

Create a new asset category. If asset_index is omitted, the server assigns max(asset_index)+1.

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| asset_id | string | yes | Asset category business ID |
| asset_name | string | yes | Display name |
| asset_type | string | yes | Asset category type |
| vesting_nation | string | yes | Vesting country code |
| in_use | string | yes | Active flag |
| asset_index |  | no | Display order; server assigns max+1 if omitted |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /assets/other-assets/items

**List distinct asset types**

Return the distinct asset_type values currently in use.

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### DELETE /assets/other-assets/{asset_id}

**Delete asset category**

Delete an asset category by id.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| asset_id | path | string | yes |  |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### PUT /assets/other-assets/{asset_id}

**Update asset category**

Update an asset category by id; any omitted field is left unchanged.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| asset_id | path | string | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| asset_name |  | no | Display name |
| asset_type |  | no | Asset category type |
| vesting_nation |  | no | Vesting country code |
| in_use |  | no | Active flag |
| asset_index |  | no | Dropdown order |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /assets/stocks

**List stock holdings**

Return stock holdings filtered by asset_id.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| asset_id | query | string | yes | Parent asset category id |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### POST /assets/stocks

**Create stock holding**

Create a new stock holding under an asset category.

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| stock_id | string | yes | Holding business ID |
| stock_code | string | yes | Ticker symbol |
| stock_name | string | yes | Stock display name |
| asset_id | string | yes | Asset category ID |
| expected_spend | number | yes | Planned investment amount |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### DELETE /assets/stocks/details/{distinct_number}

**Delete stock transaction**

Delete a single stock transaction row.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| distinct_number | path | integer | yes |  |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### PUT /assets/stocks/details/{distinct_number}

**Update stock transaction**

Update a single stock transaction row.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| distinct_number | path | integer | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| excute_type |  | no | Transaction type |
| excute_amount |  | no | Quantity traded |
| excute_price |  | no | Price per share |
| excute_date |  | no | YYYYMMDD |
| account_id |  | no | Settling account business ID |
| account_name |  | no | Settling account display name |
| memo |  | no | Free-form memo |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### DELETE /assets/stocks/{stock_id}

**Delete stock holding**

Delete a stock holding by id.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| stock_id | path | string | yes |  |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### PUT /assets/stocks/{stock_id}

**Update stock holding**

Update a stock holding by id; any omitted field is left unchanged.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| stock_id | path | string | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| stock_code |  | no | Ticker symbol |
| stock_name |  | no | Stock display name |
| asset_id |  | no | Asset category ID |
| expected_spend |  | no | Planned investment amount |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /assets/stocks/{stock_id}/details

**List stock transactions**

Return all buy/sell/stock-dividend/cash-dividend transactions for a holding.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| stock_id | path | string | yes |  |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### POST /assets/stocks/{stock_id}/details

**Record stock transaction**

Record a buy/sell/stock-dividend/cash-dividend transaction.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| stock_id | path | string | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| stock_id | string | yes | FK to Stock_Journal.stock_id |
| excute_type | string | yes | Transaction type: buy/sell/stock/cash |
| excute_amount | number | yes | Quantity traded |
| excute_price | number | yes | Price per share |
| excute_date | string | yes | YYYYMMDD |
| account_id | string | yes | Settling account business ID |
| account_name | string | yes | Settling account display name |
| memo |  | no | Free-form memo |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

## Reports

### GET /reports/assets

**Get asset composition**

Returns share (% + absolute) of each asset type, FX-converted to base currency.

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /reports/balance

**Get current balance sheet**

Aggregates latest snapshots per asset/liability entity, FX-converts to base currency, returns net worth.

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /reports/expenditure/{type}

**Get expenditure trend**

Returns monthly (12 points) or yearly (10 points) expenditure aggregated from Journal rows whose action_main_type is Floating or Fixed.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| type | path | string | yes |  |
| vesting_month | query | string | yes | Anchor month YYYYMM |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

## Dashboard

### GET /dashboard/alarms

**List upcoming alarms**

Returns alarms scheduled within today..today+6 months. Monthly-recurring alarms are expanded per month; expired months are excluded.

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /dashboard/budget

**Get budget vs actual**

Returns per-category budget-vs-actual for a month (YYYYMM) or year (YYYY).

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| type | query |  | yes | Aggregation granularity |
| period | query | string | yes | YYYYMM for monthly, YYYY for yearly |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /dashboard/gifts/{year}

**Gifted amounts by year**

Returns cross-owner Transfer totals grouped by sender (Account.owner). Rate is amount * 100 / 2,200,000 (legacy gift-tax threshold).

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| year | path | string | yes | YYYY |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /dashboard/summary

**Get dashboard summary**

Returns spending / freedom_ratio / asset_debt_trend time series for the requested period (YYYYMM-YYYYMM).

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| type | query |  | yes | Summary variant |
| period | query | string | yes | YYYYMM-YYYYMM |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /dashboard/targets

**List annual targets**

Returns all target settings ordered by year desc.

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### POST /dashboard/targets

**Create target**

Creates a target. target_year defaults to current year; is_done defaults to N.

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| distinct_number | string | yes | Target row business ID |
| setting_value | number | yes | Target amount |
| target_year |  | no | YYYY; defaults to the current year when omitted |
| is_done |  | no | Y/N; defaults to N when omitted |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### DELETE /dashboard/targets/{target_id}

**Delete target**

Deletes a target by id.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| target_id | path | string | yes |  |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### PUT /dashboard/targets/{target_id}

**Update target**

Partial update. is_done can be changed independently.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| target_id | path | string | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| target_year |  | no | YYYY |
| setting_value |  | no | Target amount |
| is_done |  | no | Y/N |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

## Utilities

### POST /utilities/import/fx-rates

**Fetch FX buy rates from Sinopac**

Kicks off a background task that pulls today's (or last-day-of-period) FX rates from Sinopac and upserts into FX_Rate.

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| period | string | yes | Target period in YYYYMM. Empty string falls back to today. |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### POST /utilities/import/invoices

**Import government invoice CSV**

Kicks off a background task that parses the configured pipe-delimited invoice CSV and inserts deduplicated journal rows.

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| period | string | yes | Target period in YYYYMM. Empty string falls back to today. |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### POST /utilities/import/stock-prices

**Fetch stock prices via yfinance**

Kicks off a background task that pulls daily OHLC for every distinct ticker in StockJournal and upserts into Stock_Price_History.

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| period | string | yes | Target period in YYYYMM. Empty string falls back to today. |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /utilities/selections/accounts

**List accounts grouped by type**

Return active accounts grouped by account_type, ordered by account_index ASC.

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /utilities/selections/codes

**List top-level codes grouped by code_type**

Return codes whose parent_id is NULL, grouped by code_type and ordered by code_index ASC.

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /utilities/selections/codes/{code_group}

**List sub-codes for a parent code**

Return children of the parent code identified by code_group as a single 'sub' group.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| code_group | path | string | yes | Parent code_id |

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /utilities/selections/credit-cards

**List credit cards as a single group**

Return active credit cards in one group labelled 'Credit_Card'.

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /utilities/selections/insurances

**List insurance policies as a single group**

Return open insurance policies (has_closed != 'Y') in one group labelled 'Insurance'.

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

### GET /utilities/selections/loans

**List loans as a single group**

Return loans in one group labelled 'Loan'.

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |

## Health

### GET /health

**Server health check**

Returns alive=true and the running app version. Does not depend on the database.

#### Response (200)

| name | type | description |
| --- | --- | --- |
| status | integer | 1 = success, 0 = fail |
| data |  | Response payload. Shape depends on the endpoint. |
| msg | string | Human-readable status message |
