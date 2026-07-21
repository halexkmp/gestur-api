# Phase 1 Data Model: Employee Weekly Work Schedule & Attendance Verification

Two new Tortoise-ORM models are added to `app/shared/db/models.py`, alongside the existing
`Employee` and `JourneyRegistry` models they relate to. No existing model is modified.

## EmployeeSchedule

Represents the single active recurring weekly work pattern for one employee (spec: "Employee
Weekly Schedule").

| Field        | Type                                   | Notes                                                                 |
|--------------|-----------------------------------------|------------------------------------------------------------------------|
| `id`         | `UUIDField(pk=True)`                    | Primary key, matches repo-wide convention                              |
| `employee`   | `OneToOneField("models.Employee", related_name="schedule")` | Enforces exactly one schedule row per employee at the DB level |
| `monday`     | `BooleanField(default=False)`           | `True` = scheduled working day                                         |
| `tuesday`    | `BooleanField(default=False)`           |                                                                          |
| `wednesday`  | `BooleanField(default=False)`           |                                                                          |
| `thursday`   | `BooleanField(default=False)`           |                                                                          |
| `friday`     | `BooleanField(default=False)`           |                                                                          |
| `saturday`   | `BooleanField(default=False)`           |                                                                          |
| `sunday`     | `BooleanField(default=False)`           |                                                                          |
| `created_at` | `DatetimeField(auto_now_add=True)`      |                                                                          |
| `updated_at` | `DatetimeField(auto_now=True)`          | Bumped on every replace via `set_employee_schedule`                     |

`Meta.table = "employee_schedule"`.

**Validation rules** (enforced in `set_employee_schedule`'s application layer — all fields
are plain booleans, so there is no format validation beyond typing):
- None beyond FastAPI/Pydantic boolean typing — every combination of the 7 flags (including
  all-`False`, meaning the employee has no work days) is valid input.

**Relationships**: belongs to exactly one `Employee` (reverse accessor `employee.schedule`,
matching the existing `employee.user` OneToOne style already on `Employee`).

**Lifecycle**: created on first `PUT /employees/schedule/{employee_id}`; every subsequent
call to the same endpoint replaces the 7 flags in place (`updated_at` changes, `id` and
`created_at` do not). No delete operation is exposed (no requirement for one in the spec).

## JustifiedAbsence

Represents one excused absence on one specific scheduled work day for one employee (spec:
"Justified Absence").

| Field           | Type                                                    | Notes                                                            |
|-----------------|-----------------------------------------------------------|-------------------------------------------------------------------|
| `id`            | `UUIDField(pk=True)`                                    | Primary key                                                        |
| `employee`      | `ForeignKeyField("models.Employee", related_name="justified_absences")` | Many absences per employee, mirrors `SalaryAdvance.employee` |
| `absence_date`  | `DateField()`                                           | The scheduled work day being excused                               |
| `reason`        | `TextField(null=True)`                                  | Free-text note (e.g. "medical leave"); optional per FR-004          |
| `created_at`    | `DatetimeField(auto_now_add=True)`                      |                                                                     |

`Meta`:
```python
table = "justified_absence"
unique_together = (("employee", "absence_date"),)
```

**Validation rules**:
- `(employee, absence_date)` MUST be unique — enforced by the DB `unique_together`
  constraint (FR-006), with an application-level pre-check in
  `create_justified_absence` for a clean `400` instead of a raw DB error (see
  `research.md`, "Justified absence uniqueness enforced at the DB layer").
- `absence_date` MUST correspond to a weekday marked `True` on the employee's current
  `EmployeeSchedule` (FR-005). If the employee has no `EmployeeSchedule` row at all, every
  date is rejected (no scheduled work days exist yet).

**Relationships**: belongs to exactly one `Employee`; independent lifecycle from
`EmployeeSchedule` (an absence is not deleted when the schedule changes, though a later
schedule change could in principle make its date no longer a working day — this feature
does not retroactively invalidate existing justified absences, consistent with "schedule
changes apply prospectively" in the spec's Assumptions).

**Lifecycle**: created via `POST /employees/justified-absences`, listed via
`GET /employees/justified-absences`, removed via
`DELETE /employees/justified-absences/{absence_id}`. No update/edit operation (not
requested in the spec — deleting and re-creating covers correction).

## Attendance Verification Result (derived, not persisted)

Not a table. Computed on demand by `get_attendance_verification`, per spec's Key Entities
("computed on demand, not separately stored"). Shape returned to callers:

```text
employee_id
month
year
days: [
  {
    date
    status   # one of: PRESENT | JUSTIFIED_ABSENCE | UNJUSTIFIED_ABSENCE
  },
  ...
]
unjustified_absence_count
```

**Computation inputs** (all read-only for this feature):
- `EmployeeSchedule` for the employee (which weekdays are scheduled work days within the
  requested month/year).
- `JustifiedAbsence` rows for the employee within the requested month/year.
- Presence-per-day derived from `JourneyRegistry` rows for the employee's linked
  `user_id` within the requested month/year (`is_deleted=False`, at least one row on that
  calendar day — reusing the `get_salary_summary` day-bucketing idiom, but only needing
  presence, not earliest timestamp).
- `Employee.start_date` / `Employee.active` to exclude dates outside the employment period
  (FR-011); an inactive employee's period is treated as ending at the last known state
  change available on the model today (`Employee` has no explicit `end_date`/`deactivated_at`
  column, so — per the spec's assumption that this reuses existing data — an inactive
  employee simply excludes all dates from verification, and an active employee only
  excludes dates before `start_date`; no new column is added to `Employee` for this, since
  the spec did not request one and adding one would be unscoped model surgery).
- If the employee has no linked `user` account (`Employee.user_id IS NULL`), presence can
  never be determined. Per FR-016, this returns an empty `days` list and
  `unjustified_absence_count: 0`, mirroring the no-schedule case (FR-012) — analogous to how
  `get_salary_summary` returns zero lateness when `employee_user_id is None`.

**Classification rule** (`domain/rules.py`, pure function — see `research.md`):
for each date in `[start_of_month, end_of_month]` ∩ `[employee.start_date, today]`
(further excluded entirely if `employee.active` is `False`):
1. Skip if the weekday is not a scheduled work day per `EmployeeSchedule` (or no schedule
   exists) → excluded entirely (FR-010, FR-012).
2. Else if a `JustifiedAbsence` exists for that date → `JUSTIFIED_ABSENCE` (FR-009,
   Acceptance Scenario 3 — justified takes priority over presence).
3. Else if the employee has a journey register that date → `PRESENT`.
4. Else → `UNJUSTIFIED_ABSENCE`.
