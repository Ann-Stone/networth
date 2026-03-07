# Phase 5 — Reports Domain

> Router prefix: `/reports`
> 對應舊版：`/report`

---

## BE-025: Year Report endpoints

**Labels:** `backend` `reports` `analytics`
**Priority:** High
**Depends on:** BE-007, BE-008

### Description

實作年度報表的聚合 endpoints，對應舊版 `/report` routes。這些 endpoints 均為唯讀，整合多個 domain 的 history table 產生報表。

### Endpoints

| Method | Path | 說明 | 舊版對應 |
|--------|------|------|---------|
| GET | `/reports/balance` | 資產負債表（資產 vs 負債明細）| `GET /report/balance` |
| GET | `/reports/expenditure/{type}` | 支出趨勢報表（近12月 or 近10年）| `GET /report/expenditure/<type>/<vesting_month>` |
| GET | `/reports/assets` | 資產組成分析 | `GET /report/asset` |

### Endpoint Details

#### `GET /reports/balance`
**回傳結構：**
```json
{
  "assets": {
    "accounts": [...],        // AccountBalance 最新快照
    "stocks": [...],          // StockNetValueHistory 最新快照
    "estates": [...],         // EstateNetValueHistory 最新快照
    "insurances": [...]       // InsuranceNetValueHistory 最新快照
  },
  "liabilities": {
    "loans": [...],           // LoanBalance 最新快照
    "credit_cards": [...]     // CreditCardBalance 最新快照
  },
  "net_worth": float          // 總資產 - 總負債
}
```

#### `GET /reports/expenditure/{type}`
- Query param：`vesting_month` (YYYYMM)
- `type = monthly`：回傳指定月份往前 12 個月的支出明細（按月加總）
- `type = yearly`：回傳往前 10 年的支出加總

#### `GET /reports/assets`
**回傳結構：**
- 各資產類型的佔比（stocks / estates / insurances / accounts / other）
- 含幣別換算（統一換算為主幣別）

### Implementation Notes

- 所有計算邏輯抽至 `app/services/report_service.py`
- balance sheet 需考慮 FX rate 換算（取最近一筆 FXRate 記錄）
- expenditure trend 從 `Journal` table 聚合，不依賴 history tables

### Acceptance Criteria

- `/reports/balance` 回傳完整的資產負債分類，net_worth 計算正確
- expenditure monthly/yearly 回傳格式可直接供前端圖表使用
- 所有計算在 service 層，非 router 層
