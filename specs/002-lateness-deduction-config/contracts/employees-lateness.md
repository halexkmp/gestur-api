# Contract: Employees — Lateness Configuration & Salary Summary (delta)

Format mirrors this repo's living contract style (`specs/api/employees.md`), since that
is the format this project actually consumes (no OpenAPI/JSON-schema tooling in use).
This file documents only what's new/changed for this feature; `specs/api/employees.md`
itself gets updated with the same content during implementation (per the standing
API-contract rule in CLAUDE.md).

Requires: `HUMAN_RESOURCES` on every endpoint below (same guard as the rest of `/employees/*`).

## Endpoints

```text
GET /employees/lateness-config

PUT /employees/lateness-config
```

---

## Lateness Configuration

```text
enabled                        # bool
expected_entrance_time         # time, "HH:MM:SS"
tolerance_minutes              # int >= 0
deduction_interval_minutes     # int > 0
deduction_value                # decimal >= 0
```

### GET /employees/lateness-config

Returns the current configuration. If no configuration has ever been created (no row
exists), returns the disabled/all-zero defaults below rather than 404:

```json
{
  "enabled": false,
  "expected_entrance_time": "00:00:00",
  "tolerance_minutes": 0,
  "deduction_interval_minutes": 0,
  "deduction_value": "0.00"
}
```

### PUT /employees/lateness-config

Full replace — all fields are required on every call (no partial patch). Creates the
singleton row if none exists yet, otherwise updates the existing one in place.

Request body:

```text
enabled                         # bool, required
expected_entrance_time          # time "HH:MM:SS", required
tolerance_minutes               # int >= 0, required
deduction_interval_minutes      # int > 0, required
deduction_value                 # decimal >= 0, required
```

Response: `200`, same shape as `GET /employees/lateness-config`.

Validation errors → `400 Bad Request` with `{"detail": "<message>"}` (matches the existing
`create_employee`/`update_employee` `ValueError` → `400` convention in this codebase, not
FastAPI's automatic `422`):

- `tolerance_minutes < 0`
- `deduction_interval_minutes <= 0`
- `deduction_value < 0`

---

## Salary Summary (changed response)

`GET /employees/salary-summary/{employee_id}?month={int}&year={int}` — unchanged request
shape. Response gains three fields and changes `net_salary`'s formula:

```text
employee_id
month
year
gross_salary
advances_total
late_delay_minutes     # NEW — int, total minutes late across days beyond tolerance this month
late_days_count        # NEW — int, count of days beyond tolerance this month
late_deduction_total   # NEW — decimal, total lateness deduction this month
net_salary              # CHANGED — gross_salary - advances_total - late_deduction_total
```

When the lateness configuration is disabled or has never been created,
`late_delay_minutes`, `late_days_count`, and `late_deduction_total` are all `0`/`0.00`,
and `net_salary` is numerically identical to the current (pre-feature) behavior.

### Example (enabled, one late day)

Config: `expected_entrance_time=08:00:00, tolerance_minutes=10, deduction_interval_minutes=60, deduction_value=6.80`.
Employee's earliest check-in on 2026-07-03 was `10:05` (125 minutes late).

```json
{
  "employee_id": "b3f1...",
  "month": 7,
  "year": 2026,
  "gross_salary": "3000.00",
  "advances_total": "200.00",
  "late_delay_minutes": 125,
  "late_days_count": 1,
  "late_deduction_total": "13.60",
  "net_salary": "2786.40"
}
```

(`floor(125 / 60) = 2` intervals reached × `6.80` = `13.60`; tolerance only gated
whether the day counted as late, it was not subtracted from the 125-minute delay.)
