# Phase 1 Data Model: Bulk Employee Schedule & Attendance Verification

No new persistence models are introduced by this feature. It only adds a new read/aggregation
path over existing models. This document describes the entities involved and the response
shape produced by combining them — not schema changes.

## Existing models used (unchanged)

### Employee (`app/shared/db/models.py`)
- `id: UUID` (pk)
- `active: bool`
- `start_date: date`
- `user: FK[User] | None` — presence resolves attendance; an employee with no linked user
  never has present days (existing rule, reused as-is)

### EmployeeSchedule
- `employee: OneToOne[Employee]`
- `monday` … `sunday: bool` — the weekly recurring working/non-working pattern

### JustifiedAbsence
- `employee: FK[Employee]`
- `absence_date: date`

### JourneyRegistry
- `user: FK[User]`
- `timestamp: datetime` (UTC; localized via `LatenessConfiguration.utc_offset_minutes`, same as
  the existing attendance-verification repository)
- `is_deleted: bool`

### LatenessConfiguration
- `utc_offset_minutes: int` — used to localize journey timestamps to dates, exactly as the
  existing attendance-verification use case does

## Derived response shape (not persisted)

**EmployeeScheduleOverviewItem** — one per employee that has a schedule:
- `employee_id: UUID`
- `monday` … `sunday: bool` — identical to `EmployeeScheduleResponse` (existing
  `get_employee_schedule` schema)
- `month: int`
- `year: int`
- `days: list[AttendanceDayItem]` — identical shape to the existing
  `AttendanceVerificationResponse.days` (`date` + `status` in
  `PRESENT | JUSTIFIED_ABSENCE | UNJUSTIFIED_ABSENCE`)
- `unjustified_absence_count: int` — identical semantics to the existing
  `AttendanceVerificationResponse.unjustified_absence_count`

**EmployeeScheduleOverviewResponse**:
- `items: list[EmployeeScheduleOverviewItem]`

## Inclusion/exclusion rules (carried over from existing endpoints, applied per employee)

- No `EmployeeSchedule` row for the employee → employee omitted entirely from `items` (FR-007;
  matches the existing per-employee endpoint's 404-as-absence-of-data treatment, translated to
  "not present in the bulk list" since a bulk request cannot 404 for one of many employees).
- Requested `employee_ids` includes an ID with no matching `Employee` → skipped (FR-008).
- Employee has a schedule but no linked `user` → `days: []`, `unjustified_absence_count: 0` for
  that employee's entry (existing FR-016 rule from the attendance-verification feature, reused
  unchanged).
- Employee is currently inactive (`active=False`) → `days: []`,
  `unjustified_absence_count: 0` for that employee's entry (existing FR-011 rule, reused
  unchanged).
- Requested period predates `start_date` → period is clipped to `start_date`, same as today.
- `month`/`year` omitted → both default to the current month/year (existing default, reused
  unchanged).

## Relationships relevant to the bulk query plan

```
Employee 1───1 EmployeeSchedule
Employee 1───N JustifiedAbsence
Employee 1───0..1 User 1───N JourneyRegistry
```

The bulk repository fetches each of these four sets once, scoped to the resolved employee set
and the resolved month/year window, then groups them in-memory by `employee_id` (or `user_id`
for journey registers) before calling `classify_attendance_days` per employee — see
[research.md](./research.md) for why this replaces the current per-employee query pattern.
