# Quickstart: Validate Bulk Employee Schedule & Attendance Verification

## Prerequisites

- Dev server running (`python app/main.py`), local Postgres up, at least two `Employee` records
  with `EmployeeSchedule` rows set (via existing `PUT /employees/schedule/{employee_id}`), and
  an HR/Admin JWT (via existing `/auth` login).
- Optional: a `JustifiedAbsence` and some `JourneyRegistry` entries for one of the employees in
  the target month, to exercise all three attendance statuses.

## Scenario 1 — bulk fetch for all employees (User Story 1)

1. `GET /employees/schedule/{employee_id}` and
   `GET /employees/attendance-verification/{employee_id}?month=M&year=Y` for each seeded
   employee — record the responses as the expected baseline.
2. `GET /employees/schedule-overview?month=M&year=Y` (no `employee_ids`).
3. Expected: `items` contains one entry per employee that has a schedule; for each, the
   `monday..sunday` flags match step 1's schedule response, and `days` /
   `unjustified_absence_count` match step 1's attendance-verification response for that
   employee and period. Employees with no schedule are absent from `items`.

## Scenario 2 — bulk fetch scoped to specific employee IDs (User Story 2)

1. `GET /employees/schedule-overview?employee_ids={id1}&employee_ids={id2}&month=M&year=Y`.
2. Expected: `items` contains only entries for `id1`/`id2` (that have a schedule); a third
   seeded employee not in the list is absent.
3. Repeat with one ID replaced by a random/nonexistent UUID.
4. Expected: the nonexistent ID is silently skipped; the valid ID's entry is still returned; no
   error.

## Scenario 3 — defaults and permission

1. Call the endpoint with no `month`/`year` → expect the response's `month`/`year` fields equal
   today's month/year.
2. Call the endpoint with a non-HR/Admin token → expect the same rejection behavior as calling
   `GET /employees/schedule/{employee_id}` with that token.

## Regression check

- Re-run the existing per-employee `GET /employees/schedule/{employee_id}` and
  `GET /employees/attendance-verification/{employee_id}` calls used as the baseline in Scenario
  1 and confirm they are unaffected (same responses as before this feature existed).
