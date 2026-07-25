# Contract: Salary Summary (All Employees)

This is the Phase 1 design contract for the endpoint. Once implemented, the authoritative,
always-current copy of this contract lives in `specs/api/employees.md` (per the constitution's
Documentation-First principle) — that file MUST be updated in the same change as the code.

## Endpoint

```
GET /employees/salary-summary?month={int}&year={int}
```

- Replaces `GET /employees/salary-summary/{employee_id}?month={int}&year={int}` — the old
  path is removed, not kept alongside this one.
- `month`, `year`: optional. Omitted → default to the current month/year (unchanged from
  today's behavior).
- Auth: requires HUMAN_RESOURCES role (`ensure_hr`), unchanged from today's endpoint.

## Success response — 200

```jsonc
{
  "items": [
    {
      "employee_id": "uuid",
      "month": 7,
      "year": 2026,
      "gross_salary": "6289.00",
      "advances_total": "1257.80",
      "advances": [
        {
          "id": "uuid",
          "amount": "1257.80",
          "advance_date": "2026-07-05",
          "note": "Adiantamento salarial"
        }
      ],
      "late_delay_minutes": 1456,
      "late_days_count": 7,
      "late_deduction_total": "210.00",
      "net_salary": "4821.20"
    }
    // ... one entry per employee
  ]
}
```

- One entry per employee in the system (spec SC-004); no filtering by `active` status (spec
  Assumptions).
- `advances_total` always equals the sum of `advances[].amount` in the same entry (spec
  FR-006).
- `advances` is `[]` and `advances_total` is `"0.00"` when the employee has no salary advance
  dated within the requested month/year (spec Edge Cases / Acceptance Scenario 2.3).
- `late_delay_minutes`/`late_days_count`/`late_deduction_total` are `0`/`0`/`"0.00"` when the
  employee has no linked user account, or when the lateness configuration is missing/disabled
  — unchanged from the current single-employee endpoint's behavior.
- No employees in the system → `{"items": []}`.

## Error responses

- `403 Forbidden` — caller lacks the HUMAN_RESOURCES role.
- No `404` case: unlike the old endpoint (which 404'd for an unknown `employee_id`), this
  endpoint no longer takes an employee identifier, so that failure mode does not apply.

## Non-goals

- No pagination (spec Assumptions).
- No sort-order guarantee beyond "stable" (spec Assumptions).
- Does not change `GET /employees/me/salary-summary` (employee self-service) — out of scope.
- Does not change `GET /employees/salary-advances` (existing standalone advances list) —
  out of scope; this contract only adds advances as a nested field of the salary summary.
