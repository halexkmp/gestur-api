# Implementation Plan: Bulk Employee Schedule & Attendance Verification

**Branch**: `005-bulk-employee-schedule` | **Date**: 2026-07-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/005-bulk-employee-schedule/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Consolidate two existing per-employee endpoints — `GET /employees/schedule/{employee_id}` and
`GET /employees/attendance-verification/{employee_id}?month&year` — into one new bulk endpoint
that accepts an optional list of employee IDs plus month/year, and returns the combined
schedule + attendance-verification data for all matching employees in a single response. This
removes the 2×N per-employee request pattern that currently degrades the server as the
employee roster grows. Technical approach: a new VSA slice (`get_employees_schedule_overview`)
that batches the existing per-employee queries (schedule, justified absences, journey
registers) into set-based bulk queries, reuses the existing `classify_attendance_days` pure
function per employee, and reuses the existing HR/Admin permission guard. No changes to
existing endpoints, models, or migrations.

## Technical Context

**Language/Version**: Python 3.11 (FastAPI)

**Primary Dependencies**: FastAPI, Tortoise-ORM (existing stack, no new dependencies)

**Storage**: PostgreSQL via Tortoise-ORM — `Employee`, `EmployeeSchedule`, `JustifiedAbsence`,
`JourneyRegistry`, `LatenessConfiguration` (all existing models; no schema changes)

**Testing**: N/A — project policy is to not write tests for new features (constitution
Development Workflow & Quality Gates)

**Target Platform**: Linux server, deployed as a Vercel Python serverless function

**Project Type**: web-service (FastAPI backend, single new slice within the existing
`employees` context)

**Performance Goals**: One request replaces the current 2×N per-employee request pattern
(N = employee count); the new endpoint's own database access must be O(1) round trips per
data source (employees, schedules, justified absences, journey registers), not O(N).

**Constraints**: Must reproduce, byte-for-byte, the same per-employee values the two existing
endpoints return (FR-002, FR-003); must not modify the two existing endpoints (FR-010); no
new third-party dependencies; no new persistence models (this is a read/aggregation feature).

**Scale/Scope**: Single new route in `app/slices/employees/`; expected to be exercised against
the full active employee roster (currently on the order of tens to low hundreds of employees)
in one call.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Vertical Slice Architecture**: PASS. New feature lives entirely in a new
  `app/slices/employees/get_employees_schedule_overview/` slice (`ui/`, `application/`,
  `domain/`, `infra/`), following the same shape as the sibling `get_attendance_verification`
  slice it consolidates. No reverse dependencies.
- **II. Explicit Parameters, No Generic Containers**: PASS. The use case's `execute` method
  takes explicit typed parameters (`employee_ids: list[UUID] | None`, `month: int | None`,
  `year: int | None`); no `dict`/`**kwargs` crossing layer boundaries.
- **III. Documentation-First Feature Development**: PASS, contingent on this plan being
  completed before implementation and `specs/api/employees.md` being updated in the same
  change that adds the route (tracked as a task in `/speckit-tasks`).
- **IV. Consistency Over Cleverness**: PASS. Reuses the existing `classify_attendance_days`
  domain function as-is, reuses `ensure_hr_or_admin`, and follows the existing repository/route
  patterns from `get_employee_schedule` and `get_attendance_verification` rather than
  introducing a new querying abstraction. Existing endpoints are left untouched.
- **V. Data & Persistence Discipline**: PASS (N/A for new models — no new persistence model is
  introduced; this feature only adds bulk-oriented read queries against existing models).

No violations to record in Complexity Tracking.

**Post-Phase 1 re-check**: `data-model.md` introduces no new persistence models, `contracts/
schedule-overview.md` defines only a new GET route reusing the existing permission guard, and
`quickstart.md`'s validation approach cross-checks the new endpoint against the two existing
ones it consolidates. All five gates above still hold unchanged after design.

## Project Structure

### Documentation (this feature)

```text
specs/005-bulk-employee-schedule/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
app/slices/employees/get_employees_schedule_overview/
├── application/
│   └── use_case.py       # GetEmployeesScheduleOverview — batches schedule + attendance
│                          # retrieval across many employees for one month/year
├── domain/
│   └── rules.py           # re-exports/reuses classify_attendance_days from
│                           # get_attendance_verification.domain.rules (no duplicated logic)
├── infra/
│   └── repository.py      # bulk queries: employees (optionally filtered by id list),
│                           # schedules, justified absences, journey registers — one query
│                           # per data source, not one per employee
└── ui/
    ├── route.py            # GET /employees/schedule-overview
    └── schemas.py          # EmployeeScheduleOverviewItem, EmployeeScheduleOverviewResponse

specs/api/employees.md      # MUST be updated in the same change (new route + schema section)
```

**Structure Decision**: Single FastAPI backend project (existing structure, Option 1-style but
using this repo's actual Vertical Slice Architecture layout, not the generic template tree).
The new capability is one additional slice under the existing `employees` context, registered
in `app/slices/employees/urls.py` alongside the sibling `get_employee_schedule`,
`get_attendance_verification`, `set_employee_schedule`, and `get_my_employee_schedule` slices.
No frontend changes are part of this feature (see spec Assumptions).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
