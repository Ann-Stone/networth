# Dashboard — Targets

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### GET /dashboard/targets

**List annual targets**

Returns all target settings ordered by year desc.

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
| distinct_number | string | yes | Target row business ID |
| target_year | string | yes | YYYY |
| setting_value | number | yes | Target amount |
| is_done | string | yes | Y/N |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "distinct_number": "T-2026-01",
      "is_done": "N",
      "setting_value": 1000000.0,
      "target_year": "2026"
    }
  ],
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

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

Envelope:

| name | type | required | description |
| --- | --- | --- | --- |
| status | integer | no | 1 = success, 0 = fail |
| data |  | no | Response payload. Shape depends on the endpoint. |
| msg | string | no | Human-readable status message |

data:

| name | type | required | description |
| --- | --- | --- | --- |
| distinct_number | string | yes | Target row business ID |
| target_year | string | yes | YYYY |
| setting_value | number | yes | Target amount |
| is_done | string | yes | Y/N |

Example:

```json
{
  "status": 1,
  "data": {
    "distinct_number": "T-2026-01",
    "is_done": "N",
    "setting_value": 1000000.0,
    "target_year": "2026"
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 409 | Duplicate distinct_number | `{"status": 0, "error": "Duplicate distinct_number", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### DELETE /dashboard/targets/{target_id}

**Delete target**

Deletes a target by id.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| target_id | path | string | yes |  |

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
| 404 | Target not found | `{"status": 0, "error": "Target 42 not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

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

Envelope:

| name | type | required | description |
| --- | --- | --- | --- |
| status | integer | no | 1 = success, 0 = fail |
| data |  | no | Response payload. Shape depends on the endpoint. |
| msg | string | no | Human-readable status message |

data:

| name | type | required | description |
| --- | --- | --- | --- |
| distinct_number | string | yes | Target row business ID |
| target_year | string | yes | YYYY |
| setting_value | number | yes | Target amount |
| is_done | string | yes | Y/N |

Example:

```json
{
  "status": 1,
  "data": {
    "distinct_number": "T-2026-01",
    "is_done": "N",
    "setting_value": 1000000.0,
    "target_year": "2026"
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Target not found | `{"status": 0, "error": "Target 42 not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |
