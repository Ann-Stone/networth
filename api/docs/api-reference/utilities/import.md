# Utilities — Import

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### POST /utilities/import/fx-rates

**Fetch FX buy rates from Sinopac**

Kicks off a background task that pulls today's (or last-day-of-period) FX rates from Sinopac and upserts into FX_Rate.

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| period | string | yes | Target period in YYYYMM. Empty string falls back to today. |

#### Response (200)

Envelope:

| name | type | required | description |
| --- | --- | --- | --- |
| status | integer | no | 1 = success, 0 = fail |
| data |  | no | Response payload. Shape depends on the endpoint. |
| msg | string | no | Human-readable status message |

data:

| name | type | required | description |
| --- | --- | --- | --- |
| message | string | yes | Human-readable confirmation that the import was scheduled |

Example:

```json
{
  "status": 1,
  "data": {
    "message": "stock import started"
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### POST /utilities/import/invoices

**Import government invoice CSV**

Kicks off a background task that parses the configured pipe-delimited invoice CSV and inserts deduplicated journal rows.

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| period | string | yes | Target period in YYYYMM. Empty string falls back to today. |

#### Response (200)

Envelope:

| name | type | required | description |
| --- | --- | --- | --- |
| status | integer | no | 1 = success, 0 = fail |
| data |  | no | Response payload. Shape depends on the endpoint. |
| msg | string | no | Human-readable status message |

data:

| name | type | required | description |
| --- | --- | --- | --- |
| message | string | yes | Human-readable confirmation that the import was scheduled |

Example:

```json
{
  "status": 1,
  "data": {
    "message": "stock import started"
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### POST /utilities/import/stock-prices

**Fetch stock prices via yfinance**

Kicks off a background task that pulls daily OHLC for every distinct ticker in StockJournal and upserts into Stock_Price_History.

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| period | string | yes | Target period in YYYYMM. Empty string falls back to today. |

#### Response (200)

Envelope:

| name | type | required | description |
| --- | --- | --- | --- |
| status | integer | no | 1 = success, 0 = fail |
| data |  | no | Response payload. Shape depends on the endpoint. |
| msg | string | no | Human-readable status message |

data:

| name | type | required | description |
| --- | --- | --- | --- |
| message | string | yes | Human-readable confirmation that the import was scheduled |

Example:

```json
{
  "status": 1,
  "data": {
    "message": "stock import started"
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |
