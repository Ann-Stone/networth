# Assets — Stocks

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### GET /assets/stocks

**List stock holdings**

Return stock holdings filtered by asset_id.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| asset_id | query | string | yes | Parent asset category id |

#### Response (200)

Envelope:

| name | type | required | description |
| --- | --- | --- | --- |
| status | integer | no | 1 = success, 0 = fail |
| data |  | no | Response payload. Shape depends on the endpoint. |
| msg | string | no | Human-readable status message |

data (array item):

| name | type | required | description |
| --- | --- | --- | --- |
| stock_id | string | yes | Holding business ID |
| stock_code | string | yes | Ticker symbol |
| stock_name | string | yes | Stock display name |
| asset_id | string | yes | Asset category ID |
| expected_spend | number | yes | Planned investment amount for this holding entry (one-shot purchase budget; not a recurring premium — see Insurance.expected_spend for that) |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "asset_id": "AC-STK-001",
      "expected_spend": 10000.0,
      "stock_code": "AAPL",
      "stock_id": "STK-H-001",
      "stock_name": "Apple Inc."
    }
  ],
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 400 | Invalid query | `{"status": 0, "error": "Invalid query", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

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
| expected_spend | number | yes | Planned investment amount for this holding entry (one-shot purchase budget; not a recurring premium — see Insurance.expected_spend for that) |

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
| stock_id | string | yes | Holding business ID |
| stock_code | string | yes | Ticker symbol |
| stock_name | string | yes | Stock display name |
| asset_id | string | yes | Asset category ID |
| expected_spend | number | yes | Planned investment amount for this holding entry (one-shot purchase budget; not a recurring premium — see Insurance.expected_spend for that) |

Example:

```json
{
  "status": 1,
  "data": {
    "asset_id": "AC-STK-001",
    "expected_spend": 10000.0,
    "stock_code": "AAPL",
    "stock_id": "STK-H-001",
    "stock_name": "Apple Inc."
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 409 | Duplicate stock_id | `{"status": 0, "error": "Duplicate stock_id", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### DELETE /assets/stocks/{stock_id}

**Delete stock holding**

Delete a stock holding by id.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| stock_id | path | string | yes |  |

#### Response (200)

Envelope:

| name | type | required | description |
| --- | --- | --- | --- |
| status | integer | no | 1 = success, 0 = fail |
| data |  | no | Response payload. Shape depends on the endpoint. |
| msg | string | no | Human-readable status message |

Example:

```json
{
  "status": 1,
  "data": null,
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Stock not found | `{"status": 0, "error": "Stock 42 not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

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
| expected_spend |  | no | Planned investment amount for this holding entry (one-shot purchase budget; not a recurring premium — see Insurance.expected_spend for that) |

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
| stock_id | string | yes | Holding business ID |
| stock_code | string | yes | Ticker symbol |
| stock_name | string | yes | Stock display name |
| asset_id | string | yes | Asset category ID |
| expected_spend | number | yes | Planned investment amount for this holding entry (one-shot purchase budget; not a recurring premium — see Insurance.expected_spend for that) |

Example:

```json
{
  "status": 1,
  "data": {
    "asset_id": "AC-STK-001",
    "expected_spend": 10000.0,
    "stock_code": "AAPL",
    "stock_id": "STK-H-001",
    "stock_name": "Apple Inc."
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Stock not found | `{"status": 0, "error": "Stock 42 not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |
