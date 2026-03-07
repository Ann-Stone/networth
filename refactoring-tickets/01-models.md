# Phase 1 — Data Models

> 所有 model 使用 SQLModel，同時作為 ORM table 與 Pydantic schema。
> 命名規則：table class 用 `TableName`，request/response 專用 schema 用 `TableNameCreate`、`TableNameUpdate`、`TableNameRead`。

---

## BE-006: Define SQLModel models — Settings domain

**Labels:** `backend` `models`
**Priority:** High
**Depends on:** BE-002

### Description

定義 Settings domain 的所有 SQLModel models，對應舊版 SQLAlchemy models。

### Models to Define

#### `Account` (`app/models/settings/account.py`)
| 欄位 | 型別 | 說明 |
|------|------|------|
| id | int (PK, autoincrement) | |
| account_id | str | 帳戶識別碼 |
| name | str | 帳戶名稱 |
| account_type | str | 類型（bank / cash / invest 等）|
| fx_code | str | 幣別代碼 |
| is_calculate | str | 是否納入計算（Y/N）|
| in_use | str | 是否使用中（Y/N）|
| discount | float | 折扣率 |
| memo | str \| None | 備註 |
| owner | str \| None | 持有人 |
| carrier_no | str \| None | 載具號碼 |
| account_index | int | 排序 |

需額外定義：`AccountCreate`, `AccountUpdate`, `AccountRead`

#### `CodeData` (`app/models/settings/code_data.py`)
| 欄位 | 型別 | 說明 |
|------|------|------|
| code_id | str (PK) | |
| code_type | str | 類型（income / expense / invest 等）|
| name | str | 類別名稱 |
| code_group | str \| None | 所屬群組 code |
| code_group_name | str \| None | 群組名稱 |
| in_use | str | Y/N |
| code_index | int | 排序 |

#### `Budget` (`app/models/settings/budget.py`)
| 欄位 | 型別 | 說明 |
|------|------|------|
| budget_year | str (PK) | 年份 YYYY |
| category_code | str (PK) | 對應 CodeData.code_id |
| category_name | str | |
| code_type | str | |
| expected01 ~ expected12 | float | 各月預算金額 |

#### `CreditCard` (`app/models/settings/credit_card.py`)
| 欄位 | 型別 | 說明 |
|------|------|------|
| credit_card_id | str (PK) | |
| card_name | str | |
| card_no | str \| None | |
| last_day | int \| None | 帳單截止日 |
| charge_day | int \| None | 繳款日 |
| limit_date | int \| None | |
| feedback_way | str \| None | 回饋方式 |
| fx_code | str | 幣別 |
| in_use | str | Y/N |
| credit_card_index | int | |
| carrier_no | str \| None | 載具號碼 |
| note | str \| None | |

#### `Alarm` (`app/models/settings/alarm.py`)
| 欄位 | 型別 | 說明 |
|------|------|------|
| alarm_id | int (PK, autoincrement) | |
| alarm_type | str | 類型 |
| alarm_date | str | 提醒日期 YYYYMMDD |
| content | str | 內容 |
| due_date | str \| None | 到期日 YYYYMMDD |

#### `InitialSetting` (`app/models/settings/initial_setting.py`)
| 欄位 | 型別 | 說明 |
|------|------|------|
| code_id | int (PK) | 關聯 Code_Data.code_id |
| code_name | str | 類別名稱 |
| initial_type | str | 類型（indexed）|
| setting_value | float | 初始金額 |
| setting_date | datetime | 設定日期 |

> 注意：舊版 `create_db.sql` 中此 table 被註解掉，但 model 與 router 均存在且有使用。
> 複合查詢鍵：`code_id` + `initial_type`。

### Acceptance Criteria

- 所有 model class 可正確透過 Alembic autogenerate 產生 migration
- 每個 model 有對應的 `Create` / `Update` / `Read` schema
- 無 raw SQL，全部使用 SQLModel 欄位定義

---

## BE-007: Define SQLModel models — Monthly Report domain

**Labels:** `backend` `models`
**Priority:** High
**Depends on:** BE-002

### Description

定義月度報表 domain 的所有 SQLModel models。

### Models to Define

#### `Journal` (`app/models/monthly_report/journal.py`)
| 欄位 | 型別 | 說明 |
|------|------|------|
| distinct_number | str (PK) | 唯一交易編號 |
| vesting_month | str | 所屬月份 YYYYMM |
| spend_date | str | 交易日期 YYYYMMDD |
| spend_way | str | 支付方式名稱 |
| spend_way_type | str | 支付方式類型（account / credit_card）|
| spend_way_table | str | 對應 table 名稱 |
| action_main | str | 主類別名稱 |
| action_main_type | str | 主類別代碼 |
| action_main_table | str | |
| action_sub | str \| None | 子類別 |
| action_sub_type | str \| None | |
| action_sub_table | str \| None | |
| spending | float | 金額（正 = 收入，負 = 支出）|
| invoice_number | str \| None | 發票號碼 |
| note | str \| None | 備註 |

#### `AccountBalance` (`app/models/monthly_report/account_balance.py`)
複合 PK：`vesting_month` + `id`
| 欄位 | 型別 |
|------|------|
| vesting_month | str |
| id | str |
| name | str |
| balance | float |
| fx_code | str |
| fx_rate | float |
| is_calculate | str |

#### `CreditCardBalance` (`app/models/monthly_report/credit_card_balance.py`)
複合 PK：`vesting_month` + `id`
| 欄位 | 型別 |
|------|------|
| vesting_month | str |
| id | str |
| name | str |
| balance | float |
| fx_rate | float |

#### History / Balance Snapshot Tables

以下 table 為月結時清除重算的快照，定義於 `app/models/monthly_report/` 下。

##### `EstateNetValueHistory` (`estate_net_value_history.py`)
複合 PK：`vesting_month` + `id` + `asset_id`
| 欄位 | 型別 | 說明 |
|------|------|------|
| vesting_month | str | 月份 YYYYMM |
| id | str | 不動產 ID |
| asset_id | str | 資產分類 ID |
| name | str | 不動產名稱 |
| market_value | float | 市值 |
| cost | float | 成本 |
| estate_status | str | 狀態 |

##### `InsuranceNetValueHistory` (`insurance_net_value_history.py`)
複合 PK：`vesting_month` + `id` + `asset_id`
| 欄位 | 型別 | 說明 |
|------|------|------|
| vesting_month | str | 月份 YYYYMM |
| id | str | 保單 ID |
| asset_id | str | 資產分類 ID |
| name | str | 保單名稱 |
| surrender_value | float | 解約金 |
| cost | float | 成本 |
| fx_code | str | 幣別 |
| fx_rate | float | 匯率 |

##### `LoanBalance` (`loan_balance.py`)
複合 PK：`vesting_month` + `id`
| 欄位 | 型別 | 說明 |
|------|------|------|
| vesting_month | str | 月份 YYYYMM |
| id | str | 貸款 ID |
| name | str | 貸款名稱 |
| balance | float | 餘額 |
| cost | float | 成本 |

> 舊版含 `getDebtBalanceHistory()` 方法，聯合 CreditCardBalance 產生負債趨勢資料，供 Dashboard `asset_debt_trend` 使用。此邏輯在新版移至 `app/services/dashboard_service.py`。

##### `StockNetValueHistory` (`stock_net_value_history.py`)
複合 PK：`vesting_month` + `id` + `asset_id`
| 欄位 | 型別 | 說明 |
|------|------|------|
| vesting_month | str | 月份 YYYYMM |
| id | str | 持倉 ID |
| asset_id | str | 資產分類 ID |
| stock_code | str | 股票代碼 |
| stock_name | str | 股票名稱 |
| amount | float | 持有數量 |
| price | float | 收盤價 |
| cost | float | 成本 |
| fx_code | str | 幣別 |
| fx_rate | float | 匯率 |

> ⚠️ 舊版 model 有 typo：`__tablestock_name__` 應為 `__tablename__`，新版需修正。遷移資料時注意此 table 在舊 DB 中仍正常存在（SQLAlchemy 實際使用 `__tablename__` 屬性）。

### Acceptance Criteria

- 同 BE-006

---

## BE-008: Define SQLModel models — Asset domain

**Labels:** `backend` `models`
**Priority:** High
**Depends on:** BE-002

### Description

定義資產管理 domain 的所有 SQLModel models，包含 Stock、Insurance、Estate、Loan 及各自的 Journal / Detail table。

### Models to Define

#### Stock 群組 (`app/models/assets/stock.py`)
- `StockJournal`：持倉記錄（stock_id PK, stock_code, stock_name, asset_id, expected_spend）
- `StockDetail`：交易明細（distinct_number PK, stock_id, excute_type, excute_amount, excute_price, excute_date, account_id, account_name, memo）

#### Insurance 群組 (`app/models/assets/insurance.py`)
- `Insurance`：保單基本資料（insurance_id PK, insurance_name, asset_id, in/out account, start/end dates, pay_type, pay_day, expected_spend, has_closed）
- `InsuranceJournal`：保費/理賠明細（distinct_number PK, insurance_id, insurance_excute_type, excute_price, excute_date, memo）

#### Estate 群組 (`app/models/assets/estate.py`)
- `Estate`：不動產基本資料（estate_id PK, estate_name, estate_type, estate_address, asset_id, obtain_date, loan_id, estate_status, memo）
- `EstateJournal`：交易明細（distinct_number PK, estate_id, estate_excute_type, excute_price, excute_date, memo）

#### Loan 群組 (`app/models/assets/loan.py`)
- `Loan`：貸款基本資料（loan_id PK, loan_name, loan_type, account_id, account_name, interest_rate, period, apply_date, grace_expire_date, pay_day, amount, repayed, loan_index）
- `LoanJournal`：還款明細（distinct_number PK, loan_id, loan_excute_type, excute_price, excute_date, memo）

#### OtherAsset (`app/models/assets/other_asset.py`)
- `OtherAsset`：資產分類（asset_id PK, asset_name, asset_type, vesting_nation, in_use, asset_index）

### Acceptance Criteria

- 同 BE-006

---

## BE-009: Define SQLModel models — Dashboard domain

**Labels:** `backend` `models`
**Priority:** High
**Depends on:** BE-002

### Description

定義 Dashboard domain 的 SQLModel models。

### Models to Define

#### `FXRate` (`app/models/dashboard/fx_rate.py`)
複合 PK：`import_date` + `code`
| 欄位 | 型別 |
|------|------|
| import_date | str | YYYYMMDD |
| code | str | 幣別代碼（USD, JPY 等）|
| buy_rate | float | 買入匯率 |

#### `StockPriceHistory` (`app/models/dashboard/stock_price_history.py`)
複合 PK：`stock_code` + `fetch_date`
| 欄位 | 型別 |
|------|------|
| stock_code | str | |
| fetch_date | str | YYYYMMDD |
| open_price | float | |
| highest_price | float | |
| lowest_price | float | |
| close_price | float | |

#### `TargetSetting` (`app/models/dashboard/target_setting.py`)
| 欄位 | 型別 |
|------|------|
| distinct_number | str (PK) | |
| target_year | str | YYYY |
| setting_value | float | 目標金額 |
| is_done | str | Y/N |

### Acceptance Criteria

- 同 BE-006
