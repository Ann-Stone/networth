# Phase 4 — Asset Management Domain

> Router prefix: `/assets`
> 對應舊版：`/other-asset/stock`, `/other-asset/insurance`, `/other-asset/estate`, `/liability/loan`, `/other-asset`

---

## BE-020: Stock asset CRUD + transaction detail endpoints

**Labels:** `backend` `assets`
**Priority:** High
**Depends on:** BE-008

### Description

實作股票資產管理的完整 CRUD API，包含持倉主檔與每筆交易明細，對應舊版 `/other-asset/stock` routes。

### Endpoints — Stock Holdings

| Method | Path | 說明 | 舊版對應 |
|--------|------|------|---------|
| GET | `/assets/stocks` | 取得指定資產下的股票持倉 | `GET /other-asset/stock/<asset_id>` |
| POST | `/assets/stocks` | 新增股票持倉 | `POST /other-asset/stock` |
| PUT | `/assets/stocks/{stock_id}` | 更新持倉資訊 | `PUT /other-asset/stock/<stock_id>` |
| DELETE | `/assets/stocks/{stock_id}` | 刪除持倉 | `DELETE /other-asset/stock/<stock_id>` |

### Endpoints — Stock Transactions

| Method | Path | 說明 | 舊版對應 |
|--------|------|------|---------|
| GET | `/assets/stocks/{stock_id}/details` | 取得持倉的所有交易明細 | `GET /other-asset/stock/detail/<stock_id>` |
| POST | `/assets/stocks/{stock_id}/details` | 記錄買入/賣出/股利 | `POST /other-asset/stock/detail` |
| PUT | `/assets/stocks/details/{distinct_number}` | 更新交易記錄 | `PUT /other-asset/stock/detail/<distinct_number>` |
| DELETE | `/assets/stocks/details/{distinct_number}` | 刪除交易記錄 | `DELETE /other-asset/stock/detail/<distinct_number>` |

### Implementation Notes

- GET stocks 支援以 `asset_id` query param 過濾
- `excute_type` 枚舉值需與舊版一致（buy / sell / dividend 等）
- 交易明細的 `distinct_number` 產生邏輯需一致

### Acceptance Criteria

- 8 個 endpoints 均可正常呼叫
- 買入/賣出/股利三種 excute_type 均支援

---

## BE-021: Insurance asset CRUD + transaction detail endpoints

**Labels:** `backend` `assets`
**Priority:** High
**Depends on:** BE-008

### Description

實作保險資產管理的完整 CRUD API，對應舊版 `/other-asset/insurance` routes。

### Endpoints — Insurance Policies

| Method | Path | 說明 | 舊版對應 |
|--------|------|------|---------|
| GET | `/assets/insurances` | 取得指定資產下的保單列表 | `GET /other-asset/insurance/<asset_id>` |
| POST | `/assets/insurances` | 新增保單（解析日期格式）| `POST /other-asset/insurance` |
| PUT | `/assets/insurances/{insurance_id}` | 更新保單 | `PUT /other-asset/insurance/<insurance_id>` |
| DELETE | `/assets/insurances/{insurance_id}` | 刪除保單 | `DELETE /other-asset/insurance/<insurance_id>` |

### Endpoints — Insurance Transactions

| Method | Path | 說明 | 舊版對應 |
|--------|------|------|---------|
| GET | `/assets/insurances/{insurance_id}/details` | 取得保費/理賠明細 | `GET /other-asset/insurance/detail/<insurance_id>` |
| POST | `/assets/insurances/{insurance_id}/details` | 記錄保費繳納/理賠 | `POST /other-asset/insurance/detail` |
| PUT | `/assets/insurances/details/{distinct_number}` | 更新交易記錄 | `PUT /other-asset/insurance/detail/<distinct_number>` |
| DELETE | `/assets/insurances/details/{distinct_number}` | 刪除交易記錄 | `DELETE /other-asset/insurance/detail/<distinct_number>` |

### Implementation Notes

- POST insurance 的 `start_date` / `expected_end_date` 支援 `python-dateutil` 解析
- `has_closed` 為 Y/N 字串欄位

### Acceptance Criteria

- 8 個 endpoints 均可正常呼叫
- 日期欄位解析正確

---

## BE-022: Real Estate asset CRUD + transaction detail endpoints

**Labels:** `backend` `assets`
**Priority:** High
**Depends on:** BE-008

### Description

實作不動產管理的完整 CRUD API，對應舊版 `/other-asset/estate` routes。

### Endpoints — Estate Properties

| Method | Path | 說明 | 舊版對應 |
|--------|------|------|---------|
| GET | `/assets/estates` | 取得指定資產下的不動產列表 | `GET /other-asset/estate/<asset_id>` |
| POST | `/assets/estates` | 新增不動產（解析日期）| `POST /other-asset/estate` |
| PUT | `/assets/estates/{estate_id}` | 更新不動產 | `PUT /other-asset/estate/<estate_id>` |
| DELETE | `/assets/estates/{estate_id}` | 刪除不動產 | `DELETE /other-asset/estate/<estate_id>` |

### Endpoints — Estate Transactions

| Method | Path | 說明 | 舊版對應 |
|--------|------|------|---------|
| GET | `/assets/estates/{estate_id}/details` | 取得不動產相關費用/稅務記錄 | `GET /other-asset/estate/detail/<estate_id>` |
| POST | `/assets/estates/{estate_id}/details` | 記錄費用/稅務 | `POST /other-asset/estate/detail` |
| PUT | `/assets/estates/details/{distinct_number}` | 更新記錄 | `PUT /other-asset/estate/detail/<distinct_number>` |
| DELETE | `/assets/estates/details/{distinct_number}` | 刪除記錄 | `DELETE /other-asset/estate/detail/<distinct_number>` |

### Implementation Notes

- `obtain_date` 使用 `python-dateutil` 解析
- `estate_status` 枚舉值（持有中 / 已出售等）需與舊版一致
- `loan_id` 為 nullable FK，關聯 Loan table

### Acceptance Criteria

- 8 個 endpoints 均可正常呼叫

---

## BE-023: Loan / Liability CRUD + transaction detail endpoints

**Labels:** `backend` `assets`
**Priority:** High
**Depends on:** BE-008

### Description

實作貸款管理的完整 CRUD API，對應舊版 `/liability/loan` routes。

### Endpoints — Loans

| Method | Path | 說明 | 舊版對應 |
|--------|------|------|---------|
| GET | `/assets/loans` | 取得所有貸款 | `GET /liability/loan` |
| GET | `/assets/loans/{loan_id}` | 取得單筆貸款 | `GET /liability/loan/<loan_id>` |
| GET | `/assets/loans/selection` | 取得貸款下拉選單 | `GET /liability/loan/selection` |
| POST | `/assets/loans` | 新增貸款（解析日期）| `POST /liability/loan` |
| PUT | `/assets/loans/{loan_id}` | 更新貸款 | `PUT /liability/loan/<loan_id>` |
| DELETE | `/assets/loans/{loan_id}` | 刪除貸款 | `DELETE /liability/loan/<loan_id>` |

### Endpoints — Loan Transactions

| Method | Path | 說明 | 舊版對應 |
|--------|------|------|---------|
| GET | `/assets/loans/{loan_id}/details` | 取得還款明細 | `GET /liability/loan/detail/<loan_id>` |
| POST | `/assets/loans/{loan_id}/details` | 記錄還款（本金/利息/手續費）| `POST /liability/loan/detail` |
| PUT | `/assets/loans/details/{distinct_number}` | 更新還款記錄 | `PUT /liability/loan/detail/<distinct_number>` |
| DELETE | `/assets/loans/details/{distinct_number}` | 刪除還款記錄 | `DELETE /liability/loan/detail/<distinct_number>` |

### Implementation Notes

- `apply_date` / `grace_expire_date` 使用 `python-dateutil` 解析
- `loan_excute_type` 枚舉：principal（本金）/ interest（利息）/ fee（手續費）
- `repayed` 欄位應在 LoanJournal 新增/更新時自動重新計算

### Acceptance Criteria

- 10 個 endpoints 均可正常呼叫
- 新增還款記錄後，Loan.repayed 自動更新

---

## BE-024: Other Assets CRUD endpoints

**Labels:** `backend` `assets`
**Priority:** High
**Depends on:** BE-008

### Description

實作「其他資產」類別管理的 CRUD API，對應舊版 `/other-asset` routes。
這是資產的頂層分類，Stock / Insurance / Estate 都屬於某個 OtherAsset。

### Endpoints

| Method | Path | 說明 | 舊版對應 |
|--------|------|------|---------|
| GET | `/assets/other-assets` | 取得所有資產類別 | `GET /other-asset/query` |
| GET | `/assets/other-assets/items` | 取得 distinct 資產類型列表 | `GET /other-asset/items` |
| POST | `/assets/other-assets` | 新增資產類別 | `POST /other-asset` |
| PUT | `/assets/other-assets/{asset_id}` | 更新資產類別 | `PUT /other-asset/<asset_id>` |
| DELETE | `/assets/other-assets/{asset_id}` | 刪除資產類別 | `DELETE /other-asset/<asset_id>` |

### Acceptance Criteria

- 5 個 endpoints 均可正常呼叫
- GET items 回傳 distinct `asset_type` 列表
