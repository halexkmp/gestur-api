---

description: "Task list template for feature implementation"
---

# Tasks: Employee Weekly Work Schedule & Attendance Verification

**Input**: Design documents from `/specs/004-employee-work-schedule/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/employees-schedule-and-attendance.md, quickstart.md

**Tests**: Not included — project policy explicitly forbids adding automated tests for new feature work (constitution, Development Workflow & Quality Gates). Verification is manual, via `quickstart.md`.

**Organization**: Tasks are grouped by user story (from spec.md: US1 = P1, US2 = P2, US3 = P3) so each can be implemented and demoed independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Every task includes its exact file path

## Path Conventions

Single project (existing FastAPI backend). All paths are relative to the repository root,
inside the existing `app/slices/employees/` context, per `plan.md`'s Project Structure.

## Access control note

Confirmed with the user: **both HR and Admin** have management access to this feature's
HR-facing endpoints (FR-013's "HR/Admin" is literal, not shorthand for HR alone). Since no
existing guard in `app/shared/security/permissions.py` combines two roles, a new
`ensure_hr_or_admin` guard is added there (Foundational phase) and used by every HR-facing
route below. The self-service `GET /employees/me/schedule` endpoint is unaffected — it
keeps using `resolve_own_employee_id`/`ensure_employee`, per FR-014.

---

## Phase 1: Setup

No setup tasks are required. This feature adds no new dependency, tool, or project
configuration — it extends the existing `employees` context using the stack already in
`requirements.txt` (FastAPI, Tortoise-ORM, Aerich).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The two new ORM models, their migration, and the new shared permission guard.
Every user story below reads and/or writes the two tables and every HR-facing route uses
the guard, so this phase MUST complete first.

**⚠️ CRITICAL**: No user story task can begin until T001, and T004 (migration applied), are done.

- [X] T001 [P] Add `ensure_hr_or_admin(current_user)` to `app/shared/security/permissions.py` — raises `HTTPException(403, detail="Forbidden: HR or Admin role required")` unless `current_user.roles` contains `UserRole.HUMAN_RESOURCES` or `UserRole.ADMIN` (same shape as the existing `ensure_hr`/`ensure_admin` functions in that file; does not modify them)
- [X] T002 Add `EmployeeSchedule` model (`id` UUID pk, `employee` OneToOneField→`Employee` related_name `schedule`, `monday`…`sunday` BooleanField default False, `created_at`, `updated_at`, `Meta.table = "employee_schedule"`) in `app/shared/db/models.py`, per `data-model.md`
- [X] T003 Add `JustifiedAbsence` model (`id` UUID pk, `employee` ForeignKeyField→`Employee` related_name `justified_absences`, `absence_date` DateField, `reason` TextField null, `created_at`, `Meta.table = "justified_absence"`, `Meta.unique_together = (("employee", "absence_date"),)`) in `app/shared/db/models.py`, per `data-model.md` (depends on T002 — same file)
- [X] T004 Run `aerich migrate` to generate the migration for `employee_schedule` and `justified_absence`, then `aerich upgrade` to apply it — do not hand-author or hand-edit the generated migration file (constitution, Principle V) (depends on T002, T003)

**Checkpoint**: The guard exists and both tables exist in the database — user story implementation can now begin.

---

## Phase 3: User Story 1 - Define and view an employee's weekly work schedule (Priority: P1) 🎯 MVP

**Goal**: HR/Admin can set which weekdays an employee is scheduled to work, retrieve that
schedule, update it (full replace), and the employee can view their own current schedule.

**Independent Test**: `PUT /employees/schedule/{employee_id}` a Mon–Fri pattern, then
`GET /employees/schedule/{employee_id}` returns it unchanged; `PUT` again with different
flags and re-`GET` confirms replace-in-place; `GET /employees/me/schedule` as the linked
employee returns the same data (see `quickstart.md` Scenarios 1–2).

### Implementation for User Story 1

- [X] T005 [P] [US1] Create `GetEmployeeScheduleRepository` with `get_employee(employee_id) -> Employee | None` and `get_schedule(employee_id) -> EmployeeSchedule | None` in `app/slices/employees/get_employee_schedule/infra/repository.py`
- [X] T006 [US1] Create `GetEmployeeSchedule` use case — `execute(employee_id: UUID)`, raises `ValueError("Employee not found")` if no employee, `ValueError("Schedule not found")` if no schedule row — in `app/slices/employees/get_employee_schedule/application/use_case.py` (depends on T005)
- [X] T007 [P] [US1] Create `EmployeeScheduleResponse` schema (`employee_id`, `monday`…`sunday: bool`, `from_attributes = True`) in `app/slices/employees/get_employee_schedule/ui/schemas.py`
- [X] T008 [US1] Create `GET /schedule/{employee_id}` route — `ensure_hr_or_admin`, catch `ValueError as e` → `HTTPException(404, detail=str(e))` — in `app/slices/employees/get_employee_schedule/ui/route.py` (depends on T001, T006, T007)
- [X] T009 [P] [US1] Create `SetEmployeeScheduleRepository` with `get_employee(employee_id) -> Employee | None` and `upsert(employee_id, monday, ..., sunday) -> EmployeeSchedule` (create if absent via `get_or_none`, else mutate 7 fields + `.save()`) in `app/slices/employees/set_employee_schedule/infra/repository.py`
- [X] T010 [US1] Create `SetEmployeeSchedule` use case — `execute(employee_id: UUID, monday: bool, tuesday: bool, wednesday: bool, thursday: bool, friday: bool, saturday: bool, sunday: bool)`, raises `ValueError("Employee not found")` if employee missing — in `app/slices/employees/set_employee_schedule/application/use_case.py` (depends on T009)
- [X] T011 [P] [US1] Create `SetEmployeeScheduleRequest` (7 required bool fields) and reuse-shaped `EmployeeScheduleResponse` schemas in `app/slices/employees/set_employee_schedule/ui/schemas.py`
- [X] T012 [US1] Create `PUT /schedule/{employee_id}` route — `ensure_hr_or_admin`, catch `ValueError as e` → `HTTPException(404, detail=str(e))` — in `app/slices/employees/set_employee_schedule/ui/route.py` (depends on T001, T010, T011)
- [X] T013 [P] [US1] Create `GetMyEmployeeScheduleRepository` (same shape as T005, duplicated per this codebase's established self-service convention — see `get_my_salary_summary`) in `app/slices/employees/get_my_employee_schedule/infra/repository.py`
- [X] T014 [US1] Create `GetMyEmployeeSchedule` use case — same behavior as T006 — in `app/slices/employees/get_my_employee_schedule/application/use_case.py` (depends on T013)
- [X] T015 [P] [US1] Create `EmployeeScheduleResponse` schema (same shape as T007) in `app/slices/employees/get_my_employee_schedule/ui/schemas.py`
- [X] T016 [US1] Create `GET /me/schedule` route — `resolve_own_employee_id(current_user)` (unaffected by the HR/Admin guard change — self-service stays `ensure_employee`-gated), catch `ValueError as e` → `HTTPException(404, detail=str(e))` — in `app/slices/employees/get_my_employee_schedule/ui/route.py` (depends on T014, T015)
- [X] T017 [US1] Register `get_employee_schedule`, `set_employee_schedule`, and `get_my_employee_schedule` routers in `app/slices/employees/urls.py`, placed among the other fixed-prefix routes (before `update_employee_router`/`delete_employee_router`/`get_employee_router`) to avoid colliding with `/{employee_id}` (depends on T008, T012, T016)

**Checkpoint**: User Story 1 is fully functional and independently testable (`quickstart.md` Scenarios 1–2).

---

## Phase 4: User Story 2 - Record a justified absence (Priority: P2)

**Goal**: HR/Admin can record, list, and remove a justified absence tied to one of an
employee's scheduled work days.

**Independent Test**: `POST /employees/justified-absences` for a date that is a scheduled
work day succeeds and appears in `GET /employees/justified-absences?employee_id=...`;
repeating the same POST → `400`; posting a non-working-day date → `400`; `DELETE` removes
it (see `quickstart.md` Scenarios 3 and 6).

### Implementation for User Story 2

- [X] T018 [P] [US2] Create `CreateJustifiedAbsenceRepository` with `get_employee(employee_id)`, `get_schedule(employee_id) -> EmployeeSchedule | None`, `exists(employee_id, absence_date) -> bool`, and `create(employee_id, absence_date, reason) -> JustifiedAbsence` in `app/slices/employees/create_justified_absence/infra/repository.py`
- [X] T019 [US2] Create `CreateJustifiedAbsence` use case — `execute(employee_id: UUID, absence_date: date, reason: str | None)`; raises `ValueError("Employee not found")` if missing, `ValueError("Date is not a scheduled work day")` if no schedule or the weekday flag is `False`, `ValueError("Justified absence already exists for this date")` if `exists()` is `True` before creating — in `app/slices/employees/create_justified_absence/application/use_case.py` (depends on T018)
- [X] T020 [P] [US2] Create `CreateJustifiedAbsenceRequest` schema (`employee_id`, `absence_date`, `reason: str | None`) in `app/slices/employees/create_justified_absence/ui/schemas.py`
- [X] T021 [US2] Create `POST /justified-absences` route, `status_code=201`, no response body (matches `create_salary_advance`) — `ensure_hr_or_admin`, catch `ValueError as e` → branch on `"not found" in str(e)` for `404` vs `400` (same idiom as `create_employee`'s route) — in `app/slices/employees/create_justified_absence/ui/route.py` (depends on T001, T019, T020)
- [X] T022 [P] [US2] Create `ListJustifiedAbsencesRepository.list(employee_id: UUID | None, month: int | None, year: int | None) -> List[JustifiedAbsence]` (mirrors `list_salary_advances`'s optional employee/month/year filtering on `absence_date`) in `app/slices/employees/list_justified_absences/infra/repository.py`
- [X] T023 [US2] Create `ListJustifiedAbsences` use case — pure pass-through `execute(employee_id, month, year)` — in `app/slices/employees/list_justified_absences/application/use_case.py` (depends on T022)
- [X] T024 [P] [US2] Create `JustifiedAbsenceItem` schema (`id`, `employee_id`, `absence_date`, `reason`, `created_at`) in `app/slices/employees/list_justified_absences/ui/schemas.py`
- [X] T025 [US2] Create `GET /justified-absences` route with optional `employee_id`, `month`, `year` query params — `ensure_hr_or_admin` — in `app/slices/employees/list_justified_absences/ui/route.py` (depends on T001, T023, T024)
- [X] T026 [P] [US2] Create `DeleteJustifiedAbsenceRepository.delete(absence_id: UUID) -> bool` (mirrors `delete_salary_advance`) in `app/slices/employees/delete_justified_absence/infra/repository.py`
- [X] T027 [US2] Create `DeleteJustifiedAbsence` use case — `execute(absence_id: UUID) -> bool` — in `app/slices/employees/delete_justified_absence/application/use_case.py` (depends on T026)
- [X] T028 [US2] Create `DELETE /justified-absences/{absence_id}` route, `status_code=204` — `ensure_hr_or_admin`, `404` if `delete()` returns `False` (mirrors `delete_salary_advance`) — in `app/slices/employees/delete_justified_absence/ui/route.py` (depends on T001, T027)
- [X] T029 [US2] Register `create_justified_absence`, `list_justified_absences`, and `delete_justified_absence` routers in `app/slices/employees/urls.py` among the fixed-prefix routes (depends on T021, T025, T028, and on T017 since both edit `urls.py`)

**Checkpoint**: User Stories 1 AND 2 both work independently (`quickstart.md` Scenarios 1–3, 6).

---

## Phase 5: User Story 3 - Verify attendance against the schedule (Priority: P3)

**Goal**: HR/Admin can request, for an employee and a period, a per-scheduled-work-day
classification (present / justified absence / unjustified absence) computed from the
schedule, justified absences, and `JourneyRegistry` check-ins.

**Independent Test**: seed a schedule, a journey register on one working day, a justified
absence on another, and leave a third with neither; `GET
/employees/attendance-verification/{employee_id}?month=&year=` classifies each of the
three correctly and excludes non-working days and out-of-employment-period dates (see
`quickstart.md` Scenarios 4–5).

### Implementation for User Story 3

- [X] T030 [P] [US3] Create pure day-classification function(s) (e.g. `classify_attendance_days(scheduled_weekdays: set[int], justified_absence_dates: set[date], present_dates: set[date], period_start: date, period_end: date) -> list[tuple[date, str]]`, status values `PRESENT`/`JUSTIFIED_ABSENCE`/`UNJUSTIFIED_ABSENCE`, justified-absence takes priority over presence per spec Acceptance Scenario 3 of US3) — no framework imports — in `app/slices/employees/get_attendance_verification/domain/rules.py`
- [X] T031 [P] [US3] Create `GetAttendanceVerificationRepository` with `get_employee(employee_id) -> Employee | None`, `get_schedule(employee_id) -> EmployeeSchedule | None`, `get_justified_absence_dates(employee_id, month, year) -> set[date]`, and `get_present_dates(user_id, month, year) -> set[date]` (the last one filters `JourneyRegistry` by `user_id`, `is_deleted=False`, `timestamp__gte`/`timestamp__lt` on the month range, then buckets by local calendar day the way `get_salary_summary` does — see `research.md`) in `app/slices/employees/get_attendance_verification/infra/repository.py`
- [X] T032 [US3] Create `GetAttendanceVerification` use case — `execute(employee_id: UUID, month: int | None, year: int | None)`; default month/year to current (matches `get_salary_summary`); raises `ValueError("Employee not found")` if missing; returns `days: []` and `unjustified_absence_count: 0` without further computation if either (a) no schedule exists (FR-012), or (b) `employee.user_id is None` (FR-016, mirrors `get_salary_summary`'s `employee_user_id is None` short-circuit — presence can never be determined without a linked user); otherwise, if `employee.active` is `False`, also returns `days: []`/`unjustified_absence_count: 0` for the entire period (FR-011 — no deactivation timestamp exists to clip to, so an inactive employee excludes the whole requested period rather than just the days after deactivation); if `employee.active` is `True`, clips the period to `[employee.start_date, today]` before calling the domain function from T030 — in `app/slices/employees/get_attendance_verification/application/use_case.py` (depends on T030, T031)
- [X] T033 [P] [US3] Create `AttendanceVerificationResponse` schema (`employee_id`, `month`, `year`, `days: List[AttendanceDayItem]` where `AttendanceDayItem` has `date` and `status`, `unjustified_absence_count: int`) in `app/slices/employees/get_attendance_verification/ui/schemas.py`
- [X] T034 [US3] Create `GET /attendance-verification/{employee_id}` route with optional `month`/`year` query params — `ensure_hr_or_admin`, catch `ValueError as e` → `HTTPException(404, detail=str(e))` — in `app/slices/employees/get_attendance_verification/ui/route.py` (depends on T001, T032, T033)
- [X] T035 [US3] Register `get_attendance_verification` router in `app/slices/employees/urls.py` among the fixed-prefix routes (depends on T034, and on T029 since both edit `urls.py`)

**Checkpoint**: All three user stories are independently functional (`quickstart.md` Scenarios 1–6).

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T036 [P] Update `specs/api/employees.md` to add the 7 new endpoints (`## Employee Weekly Schedule`, `## Justified Absence`, `## Attendance Verification` sections), merging the draft in `contracts/employees-schedule-and-attendance.md`, and note the `ensure_hr_or_admin` access requirement (both HR and Admin) instead of HR-only — mandatory per constitution Principle III, not optional cleanup
- [X] T037 Run `quickstart.md` Scenarios 1–6 end-to-end against a running dev server (`python app/main.py`) and confirm every expected result

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: None — no tasks.
- **Foundational (Phase 2)**: T001 is independent ([P]); T002 → T003 (same file) → T004
  (migration). BLOCKS all user stories.
- **User Stories (Phase 3–5)**: All depend on Phase 2 (T001, T004) completing. They can
  proceed in priority order (US1 → US2 → US3) or in parallel by different people, **except**
  that each story's final `urls.py` registration task (T017, T029, T035) touches the same
  file and MUST be applied in that order (T017 before T029 before T035) to avoid merge
  conflicts, even if the rest of each story's tasks were done in parallel.
- **Polish (Phase 6)**: Depends on all three user stories being complete (T036 needs every
  endpoint's final shape; T037 exercises all of them).

### User Story Dependencies

- **US1 (P1)**: No dependency on US2/US3. Fully independent.
- **US2 (P2)**: Depends on the `EmployeeSchedule` model (T002, Foundational) to validate
  FR-005, but not on US1's routes/use cases — independently testable once Foundational is done.
- **US3 (P3)**: Reads data shaped by US1 (`EmployeeSchedule`) and US2 (`JustifiedAbsence`)
  but calls neither's use case or repository directly — it queries the same tables via its
  own repository (T031), consistent with `get_salary_summary`'s direct-query style. It is
  functionally most meaningful once US1 and US2 data exists, but its own code has no import
  dependency on US1/US2 code.

### Parallel Opportunities

- Within Foundational: T001 (permissions guard, different file) can run in parallel with
  T002/T003 (models, same file as each other); T004 depends on T002 and T003 only.
- Within each user story: every repository task and every schema task marked `[P]` can run
  in parallel with each other (different files); each use case task depends only on its own
  repository task; each route task depends only on its own use case + schema tasks (+ T001
  for every HR-facing route).
- Across user stories: US1, US2, and US3's repository/use-case/schema/route tasks
  (T005–T016, T018–T028, T030–T034) can all be worked on in parallel by different people once
  Foundational is done — only the three `urls.py` registration tasks (T017, T029, T035) must
  be serialized.

---

## Parallel Example: User Story 1

```bash
# Launch all three repository tasks for User Story 1 together (different files):
Task: "Create GetEmployeeScheduleRepository in app/slices/employees/get_employee_schedule/infra/repository.py"
Task: "Create SetEmployeeScheduleRepository in app/slices/employees/set_employee_schedule/infra/repository.py"
Task: "Create GetMyEmployeeScheduleRepository in app/slices/employees/get_my_employee_schedule/infra/repository.py"

# Launch all three schema tasks for User Story 1 together (different files):
Task: "Create EmployeeScheduleResponse schema in app/slices/employees/get_employee_schedule/ui/schemas.py"
Task: "Create SetEmployeeScheduleRequest schema in app/slices/employees/set_employee_schedule/ui/schemas.py"
Task: "Create EmployeeScheduleResponse schema in app/slices/employees/get_my_employee_schedule/ui/schemas.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (nothing to do) + Phase 2 (Foundational: T001–T004)
2. Complete Phase 3 (User Story 1: T005–T017)
3. **STOP and VALIDATE**: run `quickstart.md` Scenarios 1–2
4. Deploy/demo if ready — HR/Admin can already define and view schedules

### Incremental Delivery

1. Foundational (T001–T004) → foundation ready
2. + User Story 1 (T005–T017) → validate → demo (MVP)
3. + User Story 2 (T018–T029) → validate → demo (justified absences)
4. + User Story 3 (T030–T035) → validate → demo (attendance verification, the full feature)
5. + Polish (T036–T037) → update `specs/api/employees.md`, run full quickstart

### Parallel Team Strategy

With multiple developers, after Foundational (T001–T004):

- Developer A: User Story 1 (T005–T017)
- Developer B: User Story 2 (T018–T028, holding T029 until after T017 lands)
- Developer C: User Story 3 (T030–T034, holding T035 until after T029 lands)

---

## Notes

- `[P]` tasks touch different files and have no incomplete-task dependency.
- `[Story]` label maps every user-story-phase task to US1/US2/US3 for traceability.
- No test tasks are included — project policy forbids automated tests for new feature work.
- Commit after each task or logical group, per repository convention.
- Stop at any phase checkpoint to validate that story independently before continuing.
- T036 (updating `specs/api/employees.md`) is not optional polish — the constitution
  requires it in the same change that adds these routes.
- Every HR-facing route (all except `GET /employees/me/schedule`) depends on T001
  (`ensure_hr_or_admin`) in addition to its own use case/schema tasks.
