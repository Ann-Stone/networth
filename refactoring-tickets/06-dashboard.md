# Phase 6 — Dashboard Domain

> Router prefix: `/dashboard`
> 對應舊版：`/dashboard`, `/target`

---

## BE-026: Dashboard summary & budget trend endpoints

**Labels:** `backend` `dashboard` `analytics`
**Priority:** High
**Depends on:** BE-007, BE-008

### Description

實作儀表板的核心統計 endpoints，對應舊版 `/dashboard/summary` 和 `/dashboard/budget` routes。

### Endpoints

| Method | Path | 說明 | 舊版對應 |
|--------|------|------|---------|
| GET | `/dashboard/summary` | 財務摘要（支出、自由度、資產/負債趨勢）| `GET /dashboard/summary/<type>/<period>` |
| GET | `/dashboard/budget` | 預算使用狀況 | `GET /dashboard/budget/<type>/<period>` |

### Endpoint Details

#### `GET /dashboard/summary`
**Query params：**
- `type`：`spending` / `freedom_ratio` / `asset_debt_trend`
- `period`：月份範圍，例如 `202301-202312`

**type 說明：**

| type | 計算內容 |
|------|---------|
| `spending` | 指定期間每月支出加總 |
| `freedom_ratio` | (收入 - 必要支出) / 收入，每月趨勢 |
| `asset_debt_trend` | 每月淨資產趨勢（從 history tables 取）|

#### `GET /dashboard/budget`
**Query params：**
- `type`：`monthly` / `yearly`
- `period`：YYYYMM 或 YYYY

**回傳：** 各類別的預算 vs 實際支出對比

### Implementation Notes

- `freedom_ratio` 計算：
  - 必要支出 = code_type = 'Fixed' 的交易加總
  - 自由度 = (total_income - fixed_expense) / total_income
- `asset_debt_trend` 計算：
  - 舊版 `LoanBalance.getDebtBalanceHistory()` 聯合 `CreditCardBalance` + `LoanBalance` 產生負債趨勢
  - 新版將此 cross-table 查詢移至 `dashboard_service.py`，不放在 model 層
- 所有計算邏輯抽至 `app/services/dashboard_service.py`

### Acceptance Criteria

- 三種 summary type 均可正確計算
- period 參數格式驗證（Pydantic validator）

---

## BE-027: Target Settings CRUD endpoints

**Labels:** `backend` `dashboard`
**Priority:** Medium
**Depends on:** BE-009

### Description

實作年度目標設定的完整 CRUD API，對應舊版 `/target` routes。

### Endpoints

| Method | Path | 說明 | 舊版對應 |
|--------|------|------|---------|
| GET | `/dashboard/targets` | 取得年度目標列表 | `GET /dashboard/target` |
| POST | `/dashboard/targets` | 建立年度目標 | `POST /target` |
| PUT | `/dashboard/targets/{id}` | 更新目標（金額/完成狀態）| `PUT /target/<id>` |
| DELETE | `/dashboard/targets/{id}` | 刪除目標 | `DELETE /target/<id>` |

### Acceptance Criteria

- 4 個 endpoints 均可正常呼叫
- `is_done` 可更新（Y/N）

---

## BE-028: Dashboard alarm & gift query endpoints

**Labels:** `backend` `dashboard`
**Priority:** Medium
**Depends on:** BE-006

### Description

實作儀表板的提醒事項顯示與禮物（贈與）統計 endpoints。

### Endpoints

| Method | Path | 說明 | 舊版對應 |
|--------|------|------|---------|
| GET | `/dashboard/alarms` | 取得未來 6 個月內的提醒 | `GET /dashboard/alarm` |
| GET | `/dashboard/gifts/{year}` | 取得指定年份的贈與金額統計 | `GET /dashboard/gift/<year>` |

### Endpoint Details

#### `GET /dashboard/alarms`
- 以今天為基準，取往後 6 個月的 Alarm 記錄
- 依 `alarm_date` 排序

#### `GET /dashboard/gifts/{year}`
- 從 Journal 取 `action_main_type = 'gift'`（或對應的 code）的記錄
- 依 `action_sub`（收/送禮對象）分組加總
- 回傳格式供前端圖表使用

### Implementation Notes

- alarm 的 6 個月範圍計算需使用 `today` 動態計算，非寫死日期
- gift 的 code type 需確認舊版使用哪個 `action_main_type`

### Acceptance Criteria

- `/dashboard/alarms` 只回傳未來 6 個月的記錄（不含已過期）
- `/dashboard/gifts/{year}` 依對象分組，金額正確加總
