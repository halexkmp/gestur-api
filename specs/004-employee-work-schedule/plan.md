# Implementation Plan: Employee Weekly Work Schedule & Attendance Verification

**Branch**: `004-employee-work-schedule` | **Date**: 2026-07-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/004-employee-work-schedule/spec.md`

## Summary

Add a per-employee weekly work schedule (which weekdays an employee is expected to work),
a justified-absence record tied to a specific scheduled work day, and an on-demand
attendance verification report that compares the schedule and justified absences against
existing `JourneyRegistry` check-ins to classify each scheduled work day in a period as
present, justified absence, or unjustified absence. All three capabilities are added as
new feature slices under the existing `app/slices/employees/` context, following the same
patterns already used by `get_lateness_config`/`update_lateness_config` (per-entity
singleton config) and `create_salary_advance`/`list_salary_advances`/`delete_salary_advance`
(per-entity child-record CRUD) and `get_salary_summary` (period-based report comparing
`JourneyRegistry` data against a config). No new architectural style, dependency, or
context is introduced.

## Technical Context

**Language/Version**: Python 3.11 (existing repo standard, `app/main.py` / `uvicorn`)

**Primary Dependencies**: FastAPI, Tortoise-ORM, Aerich, pydantic (all already in
`requirements.txt`; no new dependency required)

**Storage**: PostgreSQL via Tortoise-ORM (`app/shared/db/models.py`); two new tables
(`employee_schedule`, `justified_absence`), added via `aerich migrate`/`aerich upgrade`
run separately from this plan/implementation, per constitution

**Testing**: N/A — project policy explicitly forbids adding automated tests for new
feature work (constitution, Development Workflow & Quality Gates); manual verification via
`quickstart.md` only

**Target Platform**: Linux server, deployed as a Vercel Python serverless function
(`api/index.py`)

**Project Type**: Web service (FastAPI backend only; no frontend in this repo) — Vertical
Slice Architecture, new slices under the existing `employees` context

**Performance Goals**: No new performance requirement beyond existing endpoints in this
context (single-employee, single-period reads/writes; no batch/bulk endpoint requested)

**Constraints**: Must follow VSA folder/file layout exactly; use-case parameters must be
explicit and typed (no `dict`/`**kwargs`); `specs/api/employees.md` must be updated to match
once implemented (tracked as a task in `tasks.md`, not part of this plan's artifacts)

**Scale/Scope**: 7 new feature slices, 2 new ORM models, 1 new migration, 1 new shared
permission guard (`ensure_hr_or_admin`, additive only); no changes to existing slices'
behavior (read-only reuse of `JourneyRegistry` and `Employee`)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Vertical Slice Architecture**: PASS. All new behavior lives in new
  `app/slices/employees/<feature>/{application,ui,infra,domain}` folders. Repositories only
  query/persist; the attendance-classification rule (schedule × justified absences ×
  journey presence → per-day status) is a pure function in a new `domain/rules.py`, never
  in `ui/` or `infra/`. No reverse dependencies.
- **II. Explicit Parameters, No Generic Containers**: PASS. Every new use case declares
  explicit typed parameters (e.g. `employee_id: UUID`, `monday: bool`, ...,
  `absence_date: date`, `reason: str | None`). No `dict`/`**kwargs` crosses a layer
  boundary. Pydantic request/response schemas stay confined to each slice's `ui/schemas.py`.
- **III. Documentation-First Feature Development**: PASS (in progress). `spec.md` exists
  and is authored first; this `plan.md` is written before implementation; `tasks.md` will
  follow via `/speckit-tasks`. `specs/api/employees.md` will be updated in the same change
  that implements the routes (tracked explicitly as a task, not deferred).
- **IV. Consistency Over Cleverness**: PASS. Slice shapes are copied from the closest
  existing analogs (`get_lateness_config`/`update_lateness_config` for the singleton-config
  shape; `create_salary_advance`/`list_salary_advances`/`delete_salary_advance` for the
  child-record CRUD shape; `get_salary_summary` for the period-report shape). The one new
  element, a shared `ensure_hr_or_admin` permission guard (both HR and Admin must have
  management access, confirmed with the user — no existing guard combines two roles), is
  written in the exact shape of the existing `ensure_hr`/`ensure_admin` functions it sits
  beside in `app/shared/security/permissions.py`, and doesn't modify them. No new
  abstraction, library, or architectural style is introduced. No unrelated file is touched.
- **V. Data & Persistence Discipline**: PASS. Both new models use a UUID primary key and
  `created_at`; `EmployeeSchedule` adds `updated_at` (mutable via replace); money fields are
  N/A (no monetary field in either new model). `JustifiedAbsence` enforces
  one-row-per-(employee, date) via a DB-level `unique_together` constraint rather than
  application-only checks alone. Migration files are generated/applied via
  `aerich migrate`/`aerich upgrade` outside of agent-authored edits.

No violations — Complexity Tracking table is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/004-employee-work-schedule/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md         # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── employees-schedule-and-attendance.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
app/slices/employees/
├── get_employee_schedule/          # GET /employees/schedule/{employee_id}      (HR/Admin)
│   ├── application/use_case.py
│   ├── infra/repository.py
│   └── ui/{route.py,schemas.py}
├── set_employee_schedule/          # PUT /employees/schedule/{employee_id}      (HR/Admin, upsert)
│   ├── application/use_case.py
│   ├── infra/repository.py
│   └── ui/{route.py,schemas.py}
├── get_my_employee_schedule/       # GET /employees/me/schedule                (EMPLOYEE, self)
│   ├── application/use_case.py
│   ├── infra/repository.py
│   └── ui/{route.py,schemas.py}
├── create_justified_absence/       # POST /employees/justified-absences        (HR/Admin)
│   ├── application/use_case.py
│   ├── infra/repository.py
│   └── ui/{route.py,schemas.py}
├── list_justified_absences/        # GET /employees/justified-absences         (HR/Admin)
│   ├── application/use_case.py
│   ├── infra/repository.py
│   └── ui/{route.py,schemas.py}
├── delete_justified_absence/       # DELETE /employees/justified-absences/{id} (HR/Admin)
│   ├── application/use_case.py
│   ├── infra/repository.py
│   └── ui/{route.py,schemas.py}
└── get_attendance_verification/    # GET /employees/attendance-verification/{employee_id} (HR/Admin)
    ├── application/use_case.py
    ├── domain/rules.py             # pure day-classification logic
    ├── infra/repository.py
    └── ui/{route.py,schemas.py}

app/shared/db/
├── models.py     # + EmployeeSchedule, + JustifiedAbsence
└── enums.py      # unchanged — no new enum required (see research.md)

app/shared/security/permissions.py   # + ensure_hr_or_admin (additive; existing guards unchanged)

app/slices/employees/urls.py   # + 7 router includes, fixed-prefix routes before /{employee_id}

specs/api/employees.md         # updated during implementation to document the 7 new endpoints
```

**Structure Decision**: All new capability lives inside the existing `employees` context,
matching where `get_salary_summary`, `get_lateness_config`, and the salary-advance slices
already live — this feature is employee-management/reporting, not a new bounded context,
and it only *reads* `JourneyRegistry` (owned by the `journey` context) the same way
`get_salary_summary` already does directly against the shared model. No new top-level
context or `urls.py` is created.

## Complexity Tracking

*No violations — table intentionally omitted.*
