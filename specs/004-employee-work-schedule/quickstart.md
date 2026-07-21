# Quickstart: Employee Weekly Work Schedule & Attendance Verification

Manual end-to-end validation guide (no automated tests are added for this feature, per
project policy). Run these against a local dev server (`python app/main.py`) with an
HR/Admin JWT (`$HR_TOKEN`) and, for the self-service check, an EMPLOYEE JWT linked to the
same employee record (`$EMPLOYEE_TOKEN`). Replace `$EMPLOYEE_ID` with a real employee UUID
that has a linked `user_id` (required for the journey-matching steps).

## Prerequisites

1. Migration for `employee_schedule` and `justified_absence` has been generated
   (`aerich migrate`) and applied (`aerich upgrade`) — see `data-model.md`.
2. An employee exists with a linked user account (`user_id` set), so journey registers can
   be attributed to them (`POST /employees/` with `user_id`, or an existing employee from
   seed data).

## Scenario 1 — Define a weekly schedule (User Story 1)

```bash
curl -X PUT "$API/employees/schedule/$EMPLOYEE_ID" \
  -H "Authorization: Bearer $HR_TOKEN" -H "Content-Type: application/json" \
  -d '{"monday":true,"tuesday":true,"wednesday":true,"thursday":true,"friday":true,"saturday":false,"sunday":false}'

curl "$API/employees/schedule/$EMPLOYEE_ID" -H "Authorization: Bearer $HR_TOKEN"
```

**Expected**: PUT returns the same Mon–Fri-working shape; GET returns it back unchanged.
Re-running PUT with different flags (e.g. `saturday: true`) and re-fetching confirms the
replace-in-place behavior (same `employee_id`, updated flags).

## Scenario 2 — Employee self-service view (part of User Story 1)

```bash
curl "$API/employees/me/schedule" -H "Authorization: Bearer $EMPLOYEE_TOKEN"
```

**Expected**: same shape as Scenario 1's GET, scoped to the token's own linked employee, no
`employee_id` needed in the request.

## Scenario 3 — Record a justified absence (User Story 2)

Pick a date that falls on one of the working days set in Scenario 1 (e.g. a Wednesday).

```bash
curl -X POST "$API/employees/justified-absences" \
  -H "Authorization: Bearer $HR_TOKEN" -H "Content-Type: application/json" \
  -d '{"employee_id":"'"$EMPLOYEE_ID"'","absence_date":"2026-07-22","reason":"Medical leave"}'

curl "$API/employees/justified-absences?employee_id=$EMPLOYEE_ID&month=7&year=2026" \
  -H "Authorization: Bearer $HR_TOKEN"
```

**Expected**: POST returns `201`; GET list includes the new record with `reason: "Medical
leave"`. Re-running the same POST a second time → `400 Bad Request` (duplicate). Posting a
non-working day from Scenario 1 (e.g. a Sunday) → `400 Bad Request`.

## Scenario 4 — Verify attendance end-to-end (User Story 3)

Using the same employee and month as Scenario 3:

1. Register a journey for a *different* working day in the month (e.g. via
   `POST /journey/` as the employee, or pre-seeded data) so at least one working day has a
   matching check-in.
2. Leave at least one other working day in the month with neither a journey register nor a
   justified absence.

```bash
curl "$API/employees/attendance-verification/$EMPLOYEE_ID?month=7&year=2026" \
  -H "Authorization: Bearer $HR_TOKEN"
```

**Expected**: `days` contains one entry per working day in July 2026 within the employee's
employment period only:
- The day with a journey register → `status: "PRESENT"`.
- 2026-07-22 (the justified absence from Scenario 3) → `status: "JUSTIFIED_ABSENCE"`, even
  if a journey register also happens to exist that day.
- The day with neither → `status: "UNJUSTIFIED_ABSENCE"`.
- No Saturday/Sunday entries appear (non-working days per Scenario 1's schedule).
- `unjustified_absence_count` equals the number of `UNJUSTIFIED_ABSENCE` entries.

## Scenario 5 — No schedule yet (edge case, FR-012)

Using an employee with no `PUT /employees/schedule/{employee_id}` call ever made:

```bash
curl "$API/employees/attendance-verification/$EMPLOYEE_ID?month=7&year=2026" \
  -H "Authorization: Bearer $HR_TOKEN"
```

**Expected**: `days: []`, `unjustified_absence_count: 0` — not a `404` and not a crash;
`GET /employees/schedule/{employee_id}` for the same employee → `404 Not Found`.

## Scenario 6 — Delete a justified absence

```bash
curl -X DELETE "$API/employees/justified-absences/$ABSENCE_ID" -H "Authorization: Bearer $HR_TOKEN"
```

**Expected**: `204 No Content`; a subsequent attendance verification for that date now shows
`UNJUSTIFIED_ABSENCE` instead of `JUSTIFIED_ABSENCE` (assuming no journey register that
day).
