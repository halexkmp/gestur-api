---

description: "Task list template for feature implementation"
---

# Tasks: Bulk Employee Schedule & Attendance Verification

**Input**: Design documents from `/specs/005-bulk-employee-schedule/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/schedule-overview.md, quickstart.md

**Tests**: Not included — project policy (constitution: Development Workflow & Quality Gates)
is to not write automated tests for new feature work.

**Organization**: Tasks are grouped by user story to enable independent implementation and
testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2)
- Include exact file paths in descriptions

## Path Conventions

Single FastAPI backend project, existing Vertical Slice Architecture layout. All new files
live under `app/slices/employees/get_employees_schedule_overview/`; the only touched existing
files are `app/slices/employees/urls.py` (route registration) and `specs/api/employees.md`
(mandatory contract sync per the constitution).

---

## Phase 1: Setup

**Purpose**: Create the new slice's folder structure

- [X] T001 Create the `app/slices/employees/get_employees_schedule_overview/` slice with
      `application/`, `domain/`, `infra/`, and `ui/` subfolders, mirroring the layout of the
      sibling `app/slices/employees/get_attendance_verification/` slice

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shape shared by both user stories — response contract and route/permission
wiring — must exist before either story's behavior can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 [P] Define `AttendanceDayItem` (or import the existing one),
      `EmployeeScheduleOverviewItem` (employee_id, monday..sunday, month, year, days,
      unjustified_absence_count), and `EmployeeScheduleOverviewResponse` (items: list) in
      `app/slices/employees/get_employees_schedule_overview/ui/schemas.py`, matching the
      shapes in `specs/005-bulk-employee-schedule/contracts/schedule-overview.md`
- [X] T003 Create `app/slices/employees/get_employees_schedule_overview/ui/route.py` with
      `router = APIRouter()`, a `GET /schedule-overview` handler that depends on
      `get_current_user`, calls `ensure_hr_or_admin`, and accepts `month: int | None = None`,
      `year: int | None = None` query params (employee_ids added in Phase 4); wire a
      placeholder `use_case.execute(...)` call to be completed in Phase 3
- [X] T004 Register the new router in `app/slices/employees/urls.py` alongside the other
      fixed-prefix routers (before the dynamic `/{employee_id}` routes, per the existing
      ordering comment in that file)

**Checkpoint**: Route exists, is permission-guarded, and returns once wired to a use case —
ready for User Story 1

---

## Phase 3: User Story 1 - HR loads schedule + attendance for all employees for a period in one call (Priority: P1) 🎯 MVP

**Goal**: `GET /employees/schedule-overview?month=&year=` (no employee filter) returns, in one
response, the same weekly-schedule and attendance-verification data that calling the two
existing per-employee endpoints once per employee would return, for every employee that has a
schedule.

**Independent Test**: Seed several employees with schedules (and journey/absence data for the
target month), call the new endpoint with no `employee_ids`, and confirm each returned item
matches the existing `GET /employees/schedule/{employee_id}` and
`GET /employees/attendance-verification/{employee_id}?month&year` responses for that employee;
confirm an employee with no schedule is absent from the list (see quickstart.md Scenario 1).

### Implementation for User Story 1

- [X] T005 [US1] In `app/slices/employees/get_employees_schedule_overview/infra/repository.py`,
      implement `GetEmployeesScheduleOverviewRepository` with bulk methods: `get_employees()`
      (all employees), `get_schedules(employee_ids: list[UUID])` (all `EmployeeSchedule` rows
      for those IDs in one query), `get_justified_absence_dates_bulk(employee_ids, month,
      year)` (all `JustifiedAbsence` rows in the period for those employees, grouped by
      `employee_id`), and `get_present_dates_bulk(user_ids, month, year)` (all `JourneyRegistry`
      rows in the period for those users, localized via `LatenessConfiguration` exactly as
      `get_attendance_verification/infra/repository.py` does, grouped by `user_id`) — one query
      per data source, not one per employee
- [X] T006 [US1] In
      `app/slices/employees/get_employees_schedule_overview/application/use_case.py`,
      implement `GetEmployeesScheduleOverview.execute(employee_ids: list[UUID] | None, month:
      int | None, year: int | None)`: default month/year to today's, fetch employees (all, for
      now — US2 adds ID scoping), fetch their schedules and drop employees with none, then for
      each remaining employee reproduce the existing per-employee attendance rules (empty
      days/zero count when `employee.user_id` is `None` or `employee.active` is `False`;
      period clipped to `employee.start_date` and to today) and call the existing
      `classify_attendance_days` from
      `app.slices.employees.get_attendance_verification.domain.rules` to build each item's
      `days` and `unjustified_absence_count`
- [X] T007 [US1] Complete `app/slices/employees/get_employees_schedule_overview/ui/route.py`:
      instantiate `use_case = GetEmployeesScheduleOverview(GetEmployeesScheduleOverviewRepository())`
      at module level and have the route call `use_case.execute(employee_ids=None, month=month,
      year=year)`, returning `EmployeeScheduleOverviewResponse(items=...)`
- [X] T008 [US1] Update `specs/api/employees.md` to document
      `GET /employees/schedule-overview` (request params, response shape, permission
      requirement, omission rules) per the constitution's mandatory API-contract-sync rule,
      using `specs/005-bulk-employee-schedule/contracts/schedule-overview.md` as source

**Checkpoint**: User Story 1 is fully functional — bulk fetch for the entire roster works and
matches the two existing per-employee endpoints

---

## Phase 4: User Story 2 - HR loads schedule + attendance for a specific set of employees (Priority: P2)

**Goal**: `GET /employees/schedule-overview?employee_ids=&employee_ids=&month=&year=` scopes
the same combined result to only the requested employees, silently skipping any ID that
doesn't exist or has no schedule.

**Independent Test**: Call the endpoint with an explicit subset of seeded employee IDs (plus
one nonexistent UUID) and confirm only the valid, schedule-having employees among the
requested set appear in `items`, with values matching Scenario 1's baseline (see
quickstart.md Scenario 2).

### Implementation for User Story 2

- [X] T009 [US2] In
      `app/slices/employees/get_employees_schedule_overview/infra/repository.py`, extend
      `get_employees()` to `get_employees(employee_ids: list[UUID] | None)`, filtering by
      `Employee.filter(id__in=employee_ids)` when a non-empty list is given and returning all
      employees otherwise
- [X] T010 [US2] In
      `app/slices/employees/get_employees_schedule_overview/application/use_case.py`, pass the
      `employee_ids` parameter through to `repository.get_employees(employee_ids)` (already
      accepted by `execute`'s signature from T006); nonexistent IDs naturally produce no
      matching employee and are skipped, same as employees with no schedule
- [X] T011 [US2] In
      `app/slices/employees/get_employees_schedule_overview/ui/route.py`, add
      `employee_ids: list[UUID] | None = Query(None)` to the route signature and pass it to
      `use_case.execute(employee_ids=employee_ids, month=month, year=year)`
- [X] T012 [US2] Update `specs/api/employees.md`'s new section (from T008) to include the
      `employee_ids` query parameter and its skip-invalid-IDs behavior

**Checkpoint**: Both the "all employees" and "specific employees" calling patterns work
end-to-end

---

## Phase 5: Polish & Cross-Cutting Concerns

- [X] T013 Run through `specs/005-bulk-employee-schedule/quickstart.md` end-to-end against the
      local dev server (all three scenarios plus the regression check) and confirm the two
      existing per-employee endpoints are unaffected

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS both user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion; no dependency on US2
- **User Story 2 (Phase 4)**: Depends on Foundational completion; builds on the repository/use
  case/route files US1 creates (T005–T007), so in practice follows US1 in this single-endpoint
  feature — implement sequentially, not in parallel, even though both are nominally
  independent stories
- **Polish (Phase 5)**: Depends on both user stories being complete

### Within Each User Story

- Repository before use case (US1: T005 → T006)
- Use case before route wiring (US1: T006 → T007)
- Implementation before contract doc update (US1: T007 → T008; US2: T011 → T012)

### Parallel Opportunities

- T002 (schemas) has no dependency on T003/T004 and can run in parallel with them in Phase 2
- Because US1 and US2 touch the same three files (`repository.py`, `use_case.py`,
  `route.py`), they are **not** parallelizable with each other — implement US1 fully, then
  extend it for US2

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 — bulk "all employees" fetch, matching the two existing
   endpoints
4. **STOP and VALIDATE**: run quickstart.md Scenario 1 and the regression check
5. This alone already fixes the reported server degradation for the primary "load everyone"
   case

### Incremental Delivery

1. Setup + Foundational → route skeleton ready
2. User Story 1 → validate independently → this is the MVP fix for the degradation
3. User Story 2 → validate independently → adds ID-scoped filtering for filtered/paginated
   frontend views
4. Polish → full quickstart pass, confirm existing endpoints unaffected

---

## Notes

- No test tasks are included per project policy; validate manually via `quickstart.md`
  instead.
- `specs/api/employees.md` updates are split across T008 (initial doc) and T012
  (`employee_ids` addition) so the contract file is updated in the same change as each piece
  of behavior it documents, per the constitution's mandatory sync rule.
- Avoid introducing a new querying abstraction — reuse the existing repository/route/schema
  patterns from `get_employee_schedule` and `get_attendance_verification` throughout.
