# Contract: Employee Weekly Work Schedule & Attendance Verification

Draft API contract for this feature's 7 new endpoints, all under the existing
`/employees` router (`app/slices/employees/urls.py`). Written in the same format as
`specs/api/employees.md`, which this content is merged into
(`## Employee Weekly Schedule`, `## Justified Absence`, `## Attendance Verification`
sections) during implementation — this file is the planning-time draft, not the
authoritative contract itself.

Requires: HUMAN_RESOURCES **or** ADMIN on every endpoint below, **except**
`GET /employees/me/schedule`, which requires the EMPLOYEE role plus a linked employee
record on the caller's own account (same self-service pattern as
`GET /employees/me/salary-summary`). This is the first `employees`-context surface where
ADMIN is also granted access alongside HR — every other endpoint in `specs/api/employees.md`
remains HUMAN_RESOURCES-only; see `research.md`'s `ensure_hr_or_admin` decision.

## Endpoints

GET /employees/schedule/{employee_id}

PUT /employees/schedule/{employee_id}

GET /employees/me/schedule

POST /employees/justified-absences → 201

GET /employees/justified-absences?employee_id={uuid}&month={int}&year={int}

DELETE /employees/justified-absences/{absence_id} → 204

GET /employees/attendance-verification/{employee_id}?month={int}&year={int}

All query params above are optional filters; `month`/`year` default to the current month
when omitted (same convention as `GET /employees/salary-summary/{employee_id}`).

---

## Employee Weekly Schedule

```text
employee_id
monday      # bool
tuesday     # bool
wednesday   # bool
thursday    # bool
friday      # bool
saturday    # bool
sunday      # bool
```

GET /employees/schedule/{employee_id}: returns the shape above.
- No schedule exists yet for that employee → `404 Not Found` (unlike lateness config,
  there is no sensible "all working days" or "no working days" default to fall back to —
  absence of a schedule is a distinct, meaningful state per FR-012).
- `employee_id` doesn't reference an existing employee → `404 Not Found`.

PUT /employees/schedule/{employee_id}: full replace — all 7 day flags are required on every
call (no partial patch, consistent with `PUT /employees/lateness-config`). Creates the row
if none exists yet, otherwise replaces the 7 flags on the existing row (`updated_at`
changes). Response: same shape as GET.
- `employee_id` doesn't reference an existing employee → `404 Not Found`.

GET /employees/me/schedule: self-service equivalent of
`GET /employees/schedule/{employee_id}`, scoped to the caller (no `employee_id` param
accepted — resolved server-side from the token, same as
`GET /employees/me/salary-summary`). Same 404-if-no-schedule behavior.

---

## Justified Absence

Create request (POST /employees/justified-absences):

```text
employee_id
absence_date
reason         # nullable
```

- `absence_date` must be one of the employee's scheduled work days per their current
  Employee Weekly Schedule → otherwise `400 Bad Request`.
- Employee has no Employee Weekly Schedule at all → `400 Bad Request` (no scheduled work
  days exist to justify an absence against).
- A justified absence already exists for this `employee_id` + `absence_date` →
  `400 Bad Request`.
- `employee_id` doesn't reference an existing employee → `404 Not Found`.
- Returns `201` (body TBD at implementation time — likely no body, consistent with
  `POST /employees/salary-advances`, retrievable via the list endpoint below).

List item (GET /employees/justified-absences response):

```text
id
employee_id
absence_date
reason        # nullable
created_at
```

DELETE /employees/justified-absences/{absence_id} → `204 No Content`.
- `absence_id` doesn't reference an existing justified absence → `404 Not Found`.

---

## Attendance Verification

GET /employees/attendance-verification/{employee_id} response:

```text
employee_id
month
year
days: [
  {
    date
    status                    # PRESENT | JUSTIFIED_ABSENCE | UNJUSTIFIED_ABSENCE
  },
  ...
]
unjustified_absence_count      # convenience count, equal to len(days where status == UNJUSTIFIED_ABSENCE)
```

- `days` only includes dates that are scheduled work days per the employee's Employee
  Weekly Schedule, within the requested month/year, and within the employee's active
  employment period (before `start_date`, or on/after any date the employee is inactive,
  are excluded — FR-011). Non-working days per the schedule never appear in `days`
  (FR-010).
- Employee has no Employee Weekly Schedule at all → `days: []`,
  `unjustified_absence_count: 0` (FR-012) — not a `404`, since "no schedule" is a valid,
  reportable state (nothing was expected, so nothing is missing).
- `employee_id` doesn't reference an existing employee → `404 Not Found`.
- This endpoint performs no write and triggers no salary/payroll recalculation (FR-015) —
  it is read-only.
