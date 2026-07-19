# Contract: Employees — Self-Service Salary Access (new)

Format mirrors this repo's living contract style (`specs/api/employees.md`), since that
is the format this project actually consumes (no OpenAPI/JSON-schema tooling in use).
This file documents only what's new for this feature; `specs/api/employees.md` itself
gets updated with the same content during implementation (per the standing API-contract
rule in CLAUDE.md).

Requires: `EMPLOYEE` role on every endpoint below, AND a linked `Employee` record on the
caller's `User` — this is a distinct guard from the `HUMAN_RESOURCES` guard used by every
other `/employees/*` endpoint. No `employee_id` path/query parameter exists on either
endpoint below — the target employee is always the caller.

## Endpoints

```text
GET /employees/me/salary-summary

GET /employees/me/salary-advances
```

---

## GET /employees/me/salary-summary

Self-service equivalent of `GET /employees/salary-summary/{employee_id}`, scoped to the
caller. Same response shape as the HR-facing endpoint (including the lateness fields
added in spec 002) — the caller sees their own delay/deduction breakdown.

Query parameters:

```text
month    # int, optional — defaults to current month
year     # int, optional — defaults to current year
```

Response `200`:

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

Errors:

- `403 Forbidden` — caller lacks the `EMPLOYEE` role, or has the role but no linked `Employee` record.

---

## GET /employees/me/salary-advances

Self-service equivalent of `GET /employees/salary-advances?employee_id=...`, scoped to
the caller. No `employee_id` query parameter exists on this endpoint (unlike the
HR-facing one, where it's optional/filterable across employees) — the caller can never
request another employee's advances.

Query parameters:

```text
month    # int, optional — filters to this month if provided
year     # int, optional — filters to this year if provided
```

Response `200`:

```json
[
  {
    "id": "a1c2...",
    "amount": "200.00",
    "employee_id": "b3f1...",
    "created_at": "2026-07-05T14:30:00Z",
    "note": "advance for rent",
    "advance_date": "2026-07-05"
  }
]
```

Empty list (`[]`) when the caller has no advances matching the filters — not an error.

Errors:

- `403 Forbidden` — caller lacks the `EMPLOYEE` role, or has the role but no linked `Employee` record.
