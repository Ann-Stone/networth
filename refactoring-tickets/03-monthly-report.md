# Phase 3 — Monthly Report Domain

> Router prefix: `/monthly-report`
> 對應舊版：`/journal`, `/stock/price`, `/balance`

---

## BE-016: Journal (Transaction) CRUD endpoints

**Labels:** `backend` `monthly-report`
**Priority:** High
**Depends on:** BE-007

### Description

實作交易記錄（Journal）的完整 CRUD API，對應舊版 `/journal` 的 CRUD routes。

### Endpoints

| Method | Path | 說明 | 舊版對應 |
|--------|------|------|---------|
| GET | `/monthly-report/journals/{vesting_month}` | 取得指定月份所有交易 + gainLoss 計算 | `GET /journal/<vesting_month>` |
| POST | `/monthly-report/journals` | 建立交易記錄 | `POST /journal` |
| PUT | `/monthly-report/journals/{journal_id}` | 更新交易記錄 | `PUT /journal/<journal_id>` |
| DELETE | `/monthly-report/journals/{journal_id}` | 刪除交易記錄 | `DELETE /journal/<journal_id>` |

### Implementation Notes

- `GET /{vesting_month}` 需同時計算 gainLoss：
  - 收入加總 - 支出加總（可能涉及 FX rate 換算）
  - 舊版此邏輯在 route 中，需移至 service 層
- POST 的 `spend_date` 支援 ISO 8601 格式（`%Y-%m-%dT%H:%M:%S.%fZ`），存入時轉為 `YYYYMMDD`
- `distinct_number` 的產生邏輯需與舊版一致（若舊版有特定格式）

### Acceptance Criteria

- GET 回傳資料含 `gainLoss` 計算結果
- 日期格式轉換正確
- 刪除不存在的 journal_id 回傳 404

---

## BE-017: Journal analytics endpoints

**Labels:** `backend` `monthly-report` `analytics`
**Priority:** High
**Depends on:** BE-016

### Description

實作月度分析的聚合 endpoints，對應舊版的各類統計 routes。這些 endpoints 為唯讀，不涉及寫入。

### Endpoints

| Method | Path | 說明 | 舊版對應 |
|--------|------|------|---------|
| GET | `/monthly-report/journals/{vesting_month}/expenditure-ratio` | 支出佔比（內層/外層圓餅圖資料）| `GET /journal/expenditure-ratio/<vesting_month>` |
| GET | `/monthly-report/journals/{vesting_month}/invest-ratio` | 投資佔比 | `GET /journal/invest-ratio/<vesting_month>` |
| GET | `/monthly-report/journals/{vesting_month}/expenditure-budget` | 實際支出 vs 預算對比 | `GET /journal/expenditure-budget/<vesting_month>` |
| GET | `/monthly-report/journals/{vesting_month}/liability` | 信用卡負債明細 | `GET /journal/liability/<vesting_month>` |

### Implementation Notes

**expenditure-ratio 邏輯：**
- 外層：依 action_main_type 加總支出
- 內層：依 action_sub_type 加總（更細的分類）
- 需排除 invest / transfer 類型

**expenditure-budget 邏輯：**
- 從 Budget table 取該月預算
- 從 Journal 取實際支出
- 計算差額與使用率

**liability 邏輯：**
- 從 Journal 取 spend_way_type = credit_card 的交易
- 依 credit_card 分組加總

所有計算邏輯抽至 `app/services/monthly_report_service.py`。

### Acceptance Criteria

- expenditure-ratio 回傳兩層資料（可供前端圓餅圖使用）
- expenditure-budget 回傳每個類別的 expected vs actual
- 計算邏輯在 service 層，非 router 層

---

## BE-018: Stock price management endpoints

**Labels:** `backend` `monthly-report`
**Priority:** Medium
**Depends on:** BE-007

### Description

實作股票價格的查詢與匯入 endpoints，對應舊版 `/stock/price` routes。

### Endpoints

| Method | Path | 說明 | 舊版對應 |
|--------|------|------|---------|
| GET | `/monthly-report/stock-prices/{vesting_month}` | 取得指定月份的股票報價 | `GET /stock/price/<vesting_month>` |
| POST | `/monthly-report/stock-prices` | 手動新增股票報價記錄 | `POST /stock/price` |

### Implementation Notes

- GET 從 `StockPriceHistory` 取得該月所有持倉股票的收盤價
- POST 觸發 yfinance 抓取（或手動輸入），寫入 `StockPriceHistory`
- yfinance 相關邏輯抽至 `app/services/stock_service.py`，包含 retry 邏輯

### Acceptance Criteria

- GET 回傳格式含 stock_code, stock_name, close_price
- POST 成功後回傳新建的記錄

---

## BE-019: Monthly balance settlement endpoint

**Labels:** `backend` `monthly-report` `settlement`
**Priority:** High
**Depends on:** BE-007, BE-008

### Description

實作月結（settlement）endpoint，對應舊版 `PUT /balance/<vesting_month>`。
這是最複雜的 endpoint，負責計算並快照當月所有資產/負債的淨值。

### Endpoint

| Method | Path | 說明 | 舊版對應 |
|--------|------|------|---------|
| PUT | `/monthly-report/balance/{vesting_month}/settle` | 執行月結計算 | `PUT /balance/<vesting_month>` |

### Settlement Logic（必須完整保留）

月結依序執行以下計算（每步驟先清除該月舊快照，再重新計算）：

1. **EstateNetValueHistory**
   - 從 `Estate` 取所有房產
   - 計算 market_value（需參考 EstateJournal 或估價邏輯）
   - 計算 cost（acquisition cost）
   - 寫入 `EstateNetValueHistory`

2. **InsuranceNetValueHistory**
   - 從 `Insurance` 取所有保單
   - surrender_value = 累計繳費 - 費用
   - 考慮 fx_code 換算
   - 寫入 `InsuranceNetValueHistory`

3. **LoanBalance**
   - 從 `Loan` 取所有貸款
   - balance = 原始金額 - 已還本金
   - 寫入 `LoanBalance`

4. **StockNetValueHistory**
   - 從 `StockJournal` + `StockPriceHistory` 計算當月市值
   - cost = 買入成本加總
   - 考慮 fx_code 換算
   - 寫入 `StockNetValueHistory`

5. **AccountBalance**
   - 從 `Journal` 計算當月各帳戶餘額變動
   - 寫入 `AccountBalance`

6. **CreditCardBalance**
   - 從 `Journal` 計算當月信用卡應付金額
   - 寫入 `CreditCardBalance`

### Implementation Notes

- 整個月結流程包在一個 DB transaction 中，任一步驟失敗則全部 rollback
- 所有計算邏輯抽至 `app/services/settlement_service.py`
- 每個步驟的計算邏輯對應舊版 route function 中的邏輯

### Acceptance Criteria

- 月結後各 history table 有對應月份的快照資料
- 任一計算失敗時，整個月結 rollback，回傳錯誤訊息
- 可重複執行（冪等性：先清除再重算）
