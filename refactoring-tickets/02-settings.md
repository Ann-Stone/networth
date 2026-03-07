# Phase 2 — Settings Domain

> Router prefix: `/settings`
> 對應舊版：`/account`, `/code`, `/sub-code`, `/budget`, `/credit-card`, `/alarm`, `/initial`

---

## BE-010: Account CRUD endpoints

**Labels:** `backend` `settings`
**Priority:** High
**Depends on:** BE-006

### Description

實作帳戶管理的完整 CRUD API，對應舊版 `/account` routes。

### Endpoints

| Method | Path | 說明 | 舊版對應 |
|--------|------|------|---------|
| GET | `/settings/accounts` | 查詢帳戶列表（支援 name / type / in_use filter）| `GET /account/query` |
| GET | `/settings/accounts/selection` | 取得啟用中帳戶（下拉選單用）| `GET /account/selection` |
| POST | `/settings/accounts` | 建立新帳戶 | `POST /account` |
| PUT | `/settings/accounts/{id}` | 更新帳戶 | `PUT /account/<id>` |
| DELETE | `/settings/accounts/{id}` | 刪除帳戶 | `DELETE /account/<id>` |

### Implementation Notes

- Query params 使用 FastAPI `Query()` 定義（name, account_type, in_use 均為 optional）
- 建立時自動產生 `account_id`（若舊版有特定格式需保留）
- `account_index` 依現有最大值 + 1 自動填入
- 回傳格式統一為 `ApiResponse[list[AccountRead]]` 或 `ApiResponse[AccountRead]`

### Acceptance Criteria

- 所有 5 個 endpoints 可正常呼叫
- Filter 組合查詢正確
- 刪除不存在的 ID 回傳 404

---

## BE-011: Code / Sub-Code CRUD endpoints

**Labels:** `backend` `settings`
**Priority:** High
**Depends on:** BE-006

### Description

實作交易類別（主類別 + 子類別）的完整 CRUD API，對應舊版 `/code` 和 `/sub-code` routes。

**注意：** 舊版建立主類別時若 code_type 為 Fixed/Floating，會自動建立 Budget 記錄，需保留此邏輯。

### Endpoints

| Method | Path | 說明 | 舊版對應 |
|--------|------|------|---------|
| GET | `/settings/codes` | 查詢主類別 | `GET /code/query` |
| GET | `/settings/codes/all-with-sub` | 取得含子類別的完整列表 | `GET /code/all-sub-code` |
| POST | `/settings/codes` | 建立主類別（若為 Fixed/Floating 自動建 Budget）| `POST /code` |
| PUT | `/settings/codes/{code_id}` | 更新主類別 | `PUT /code/<code_id>` |
| DELETE | `/settings/codes/{code_id}` | 刪除主類別 | `DELETE /code/<code_id>` |
| GET | `/settings/codes/{parent_id}/sub-codes` | 取得子類別 | `GET /sub-code/query/<parent_id>` |
| POST | `/settings/sub-codes` | 建立子類別 | `POST /sub-code` |
| PUT | `/settings/sub-codes/{code_id}` | 更新子類別 | `PUT /sub-code/<code_id>` |
| DELETE | `/settings/sub-codes/{code_id}` | 刪除子類別 | `DELETE /sub-code/<code_id>` |

### Implementation Notes

- 建立主類別時的 Budget 自動建立邏輯抽為 service 層
- 舊版 DELETE sub-code 有未完成的 code（line 142），需重新實作完整邏輯

### Acceptance Criteria

- POST code 若 code_type = Fixed/Floating，自動在 Budget table 新增對應記錄
- 子類別的 CRUD 正確關聯 parent code_id

---

## BE-012: Budget management endpoints

**Labels:** `backend` `settings`
**Priority:** High
**Depends on:** BE-006

### Description

實作預算管理的 API，對應舊版 `/budget` routes。

### Endpoints

| Method | Path | 說明 | 舊版對應 |
|--------|------|------|---------|
| GET | `/settings/budgets/{year}` | 取得指定年度的所有預算 | `GET /budget/<year>` |
| GET | `/settings/budgets/year-range` | 取得可用的預算年度範圍 | `GET /budget/year-range` |
| PUT | `/settings/budgets` | 批次更新預算金額 | `PUT /budget` |
| POST | `/settings/budgets/{year}/copy-from-previous` | 從前一年度 Journal 計算並建立新年預算 | `POST /budget/<next_year>` |

### Implementation Notes

- `copy-from-previous` 邏輯：
  1. 取得 `{year-1}` 全年 Journal 資料
  2. 依 action_main_type 加總各月支出
  3. 取平均值作為新年各月預算初始值
  4. Bulk insert 到 Budget table
- PUT 為批次更新，body 為 `list[BudgetUpdate]`

### Acceptance Criteria

- POST copy-from-previous 正確計算前一年平均並寫入
- GET year-range 回傳已存在的年度列表

---

## BE-013: Credit Card CRUD endpoints

**Labels:** `backend` `settings`
**Priority:** High
**Depends on:** BE-006

### Description

實作信用卡管理的完整 CRUD API，對應舊版 `/credit-card` routes。

### Endpoints

| Method | Path | 說明 | 舊版對應 |
|--------|------|------|---------|
| GET | `/settings/credit-cards` | 查詢信用卡列表（支援 filter）| `GET /credit-card/query` |
| POST | `/settings/credit-cards` | 建立信用卡 | `POST /credit-card` |
| PUT | `/settings/credit-cards/{id}` | 更新信用卡 | `PUT /credit-card/<id>` |
| DELETE | `/settings/credit-cards/{id}` | 刪除信用卡 | `DELETE /credit-card/<id>` |

### Acceptance Criteria

- 所有 4 個 endpoints 可正常呼叫

---

## BE-014: Alarm / Reminder CRUD endpoints

**Labels:** `backend` `settings`
**Priority:** Medium
**Depends on:** BE-006

### Description

實作提醒事項的完整 CRUD API，對應舊版 `/alarm` routes。

### Endpoints

| Method | Path | 說明 | 舊版對應 |
|--------|------|------|---------|
| GET | `/settings/alarms` | 取得所有提醒 | `GET /alarm` |
| GET | `/settings/alarms/by-date` | 依日期查詢提醒 | `GET /alarm/query` |
| POST | `/settings/alarms` | 建立提醒（支援多種日期格式）| `POST /alarm` |
| PUT | `/settings/alarms/{alarm_id}` | 更新提醒 | `PUT /alarm/<alarm_id>` |
| DELETE | `/settings/alarms/{alarm_id}` | 刪除提醒 | `DELETE /alarm/<alarm_id>` |

### Implementation Notes

- 舊版 POST 使用 `python-dateutil` 解析多種日期格式
- 日期欄位統一存為 `YYYYMMDD` 格式的字串

### Acceptance Criteria

- POST 支援 ISO 8601 格式輸入，存入 YYYYMMDD

---

## BE-015: Initial Settings CRUD endpoints

**Labels:** `backend` `settings`
**Priority:** Medium
**Depends on:** BE-006

### Description

實作初始設定的 CRUD API，對應舊版 `/initial` routes。

> **注意：** 需先讀取舊版 `router/setting/initialRouter.py` 與對應 model，確認完整欄位後再實作。

### Endpoints

| Method | Path | 說明 | 舊版對應 |
|--------|------|------|---------|
| GET | `/settings/initial` | 查詢初始設定 | `GET /initial/query` |
| POST | `/settings/initial` | 建立初始設定 | `POST /initial` |
| PUT | `/settings/initial` | 更新初始設定 | `PUT /initial` |
| DELETE | `/settings/initial` | 刪除初始設定 | `DELETE /initial` |

### Acceptance Criteria

- 所有 4 個 endpoints 可正常呼叫
- 欄位與舊版完全對應
