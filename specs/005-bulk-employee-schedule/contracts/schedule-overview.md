# Contract: GET /employees/schedule-overview

**Requires**: HUMAN_RESOURCES or ADMIN (same as `GET /employees/schedule/{employee_id}` and
`GET /employees/attendance-verification/{employee_id}`).

## Request

```text
GET /employees/schedule-overview?employee_ids={uuid}&employee_ids={uuid}&month={int}&year={int}
```

- `employee_ids` (query, repeatable, optional): zero or more employee UUIDs. Omitted or empty
  → all employees are considered.
- `month` (query, optional): 1–12. Omitted → current month.
- `year` (query, optional): omitted → current year.

## Response — 200 OK

```text
items: [
  {
    employee_id
    monday      # bool
    tuesday     # bool
    wednesday   # bool
    thursday    # bool
    friday      # bool
    saturday    # bool
    sunday      # bool
    month       # int — echoes the resolved (possibly defaulted) month
    year        # int — echoes the resolved (possibly defaulted) year
    days: [
      { date, status }   # status: PRESENT | JUSTIFIED_ABSENCE | UNJUSTIFIED_ABSENCE
    ]
    unjustified_absence_count   # int
  },
  ...
]
```

- One entry per employee that has an `EmployeeSchedule` row, among the requested/considered
  employees. Employees without a schedule are omitted entirely — never a 404, never a
  placeholder entry, since the request spans many employees.
- `days` and `unjustified_absence_count` follow exactly the same rules as
  `GET /employees/attendance-verification/{employee_id}`:
  - No linked user account → `days: []`, `unjustified_absence_count: 0`.
  - Employee currently inactive → `days: []`, `unjustified_absence_count: 0`.
  - Period clipped to the employee's `start_date` and to today, same as today's endpoint.
  - Non-scheduled weekdays never appear in `days`.
- Requested `employee_ids` containing an ID that doesn't exist, or belongs to an employee with
  no schedule, is silently skipped — no error, no partial-failure signaling.

## Errors

- Caller lacks HUMAN_RESOURCES/ADMIN role → same rejection as the existing schedule and
  attendance-verification endpoints.
- No 404 case exists for this endpoint — an empty `items: []` is a valid, non-error response
  (e.g. no employees, no employee has a schedule, or all requested IDs are invalid).

## Non-goals (unchanged endpoints)

- `GET /employees/schedule/{employee_id}` and
  `GET /employees/attendance-verification/{employee_id}?month&year` are not modified, removed,
  or deprecated by this contract. They continue to serve single-employee lookups.
