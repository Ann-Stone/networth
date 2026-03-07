# Phase 7 — Utility & Global

> Router prefixes: `/utilities`, `/global`
> 對應舊版：`/util`, `/global`

---

## BE-029: Utility selection group endpoints

**Labels:** `backend` `utilities`
**Priority:** High
**Depends on:** BE-006, BE-008

### Description

實作前端下拉選單所需的 utility endpoints，將多個 domain 的資料聚合為選單格式，對應舊版 `/util` routes。

### Endpoints

| Method | Path | 說明 | 舊版對應 |
|--------|------|------|---------|
| GET | `/utilities/selections/accounts` | 帳戶依類型分組 | `GET /util/wallet-selection-group` |
| GET | `/utilities/selections/credit-cards` | 信用卡列表 | `GET /util/credit-card-selection-group` |
| GET | `/utilities/selections/loans` | 貸款列表（若有）| `GET /util/loan-selection-group` |
| GET | `/utilities/selections/insurances` | 保單列表 | `GET /util/insurance-selection-group` |
| GET | `/utilities/selections/codes` | 類別依類型分組 | `GET /util/code-selection-group` |
| GET | `/utilities/selections/codes/{code_group}` | 指定群組的子類別 | `GET /util/code-selection-group/<code_group>` |

### Response Format

每個 endpoint 回傳適合 Element Plus `el-select` group 的格式：
```json
{
  "status": 1,
  "data": [
    {
      "label": "group name",
      "options": [
        { "value": "id", "label": "name" }
      ]
    }
  ]
}
```

### Acceptance Criteria

- 6 個 endpoints 均可正常呼叫
- 回傳格式為 group 結構，適合前端下拉選單直接使用

---

## BE-030: Global health check endpoint

**Labels:** `backend` `utilities`
**Priority:** Low
**Depends on:** BE-001

### Description

實作簡單的伺服器健康檢查 endpoint，對應舊版 `/global/server-alive`。

### Endpoints

| Method | Path | 說明 | 舊版對應 |
|--------|------|------|---------|
| GET | `/health` | 健康檢查 | `GET /global/server-alive` |

### Response
```json
{
  "status": 1,
  "data": { "alive": true, "version": "1.0.0" },
  "msg": "success"
}
```

### Acceptance Criteria

- GET `/health` 回傳 HTTP 200 with alive status

---

## BE-031: Data import endpoints (stock price, FX rate)

**Labels:** `backend` `utilities` `import`
**Priority:** Medium
**Depends on:** BE-009

### Description

實作外部資料匯入的 endpoints，對應舊版 `/global/check/<dataType>` routes。

### Endpoints

| Method | Path | 說明 | 舊版對應 |
|--------|------|------|---------|
| POST | `/utilities/import/stock-prices` | 觸發 yfinance 抓取股價 | `POST /global/check/stock` |
| POST | `/utilities/import/fx-rates` | 觸發匯率抓取 | `POST /global/check/fx` |
| POST | `/utilities/import/invoices` | 匯入 CSV 消費紀錄至 Journal | `POST /global/check/invoice` |

### Request Body

```json
{
  "period": "202501"   // YYYYMM，指定要抓取的月份
}
```

### Implementation Notes

**Stock Price Import (`importStockPrice`)：**
- 從 `StockJournal` 取所有 `stock_code`
- 呼叫 `yfinance` 取得指定月份的日 K 資料
- 含 retry 邏輯（舊版有 retry with delay）
- 寫入 `StockPriceHistory`（避免重複 = upsert）

**FX Rate Import (`importFxRate`)：**
- 從 `Account` / `Insurance` / `Stock` 取所有使用的幣別
- 呼叫 Sinopac（永豐銀行）匯率 API 或備用來源
- 寫入 `FXRate`（upsert）

**Invoice CSV Import (`importInvoice`)：**
- 前端月報頁面點擊「匯入本月消費紀錄」按鈕觸發
- Request body：`{ "period": "YYYYMM" }`
- 讀取工作目錄下的 `invoice.csv`（pipe `|` 分隔）
- CSV 含兩種 row type：
  - `M`（Master）：載具名稱、載具號碼、發票日期、商店、發票號碼、總金額
  - `D`（Detail）：發票號碼、小計、品項名稱
- 處理流程：
  1. 依 `period` 過濾：只匯入該月份的發票
  2. 跳過 `INVOICE_SKIP` 清單中的載具號碼（設定在 `.env`）
  3. 依載具號碼比對 `CreditCard` table，自動帶入支付方式
  4. 依商店名稱比對 `merchant_mapping`（可設定的商家分類對照表），自動帶入交易類別
  5. 依發票號碼去重（`queryByVestingMonthAndInvoice`），避免重複匯入
  6. Detail row 的品項名稱串接至 note 欄位
  7. 金額轉為負數（支出）
- Bulk insert 至 `Journal` table
- 商家分類對照（舊版 hardcoded `m_list`）改為可設定，建議放 `.env` 或 config

**非同步處理：**
- 舊版使用 Python threading，FastAPI 改用 `BackgroundTasks`
- endpoint 立即回傳 `{ "msg": "import started" }`，import 在背景執行

### Acceptance Criteria

- POST 立即回傳，import 在 background task 執行
- yfinance 抓取失敗時，背景 task 記錄 error log 但不 crash
- FX rate upsert 正確（同一天同幣別不重複新增）
- Invoice CSV 匯入：同月同發票號碼不重複、金額正確轉負、品項串接至 note
- Invoice CSV 找不到檔案時記錄 error log，不 crash
