# Implementation Plan: Salary Summary for All Employees

**Branch**: `006-salary-summary-all-employees` | **Date**: 2026-07-25 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/006-salary-summary-all-employees/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Replace the single-employee `GET /employees/salary-summary/{employee_id}` endpoint with a
company-wide report: it drops the `employee_id` path parameter, keeps `month`/`year` as
optional query parameters (defaulting to the current month/year, unchanged), and returns one
summary entry per employee in the system. Each entry keeps the existing computed fields
(gross salary, advances total, lateness delay/days/deduction, net salary) and gains the
itemized list of that employee's salary advances dated within the requested month/year. The
technical approach mirrors the existing `GET /employees/schedule-overview` bulk endpoint:
bulk-fetch repository methods keyed by employee/user id to avoid N+1 queries, wrapped in an
`items: [...]` response.

## Technical Context

**Language/Version**: Python 3.13 (existing `.venv`, no `requires-python` pin in `pyproject.toml`)

**Primary Dependencies**: FastAPI, Tortoise-ORM, Pydantic (all existing; no new dependency introduced)

**Storage**: PostgreSQL via Tortoise-ORM — reads only, existing models (`Employee`, `SalaryAdvance`,
`LatenessConfiguration`, `JourneyRegistry`); no new models, fields, or migrations

**Testing**: N/A — project policy explicitly forbids adding automated tests for new feature work
(constitution, Development Workflow & Quality Gates)

**Target Platform**: Linux server (Vercel Python serverless function, existing deployment)

**Project Type**: web-service (single FastAPI backend, existing Vertical Slice Architecture)

**Performance Goals**: One request returns the full company's salary summary; no N+1 queries
across employees (bulk-fetch pattern, same as `get_employees_schedule_overview`)

**Constraints**: Must stay inside the existing `get_salary_summary` vertical slice (no new
slice); `specs/api/employees.md` MUST be updated in the same change per the constitution's
Documentation-First principle; stack is fixed, no new third-party dependencies

**Scale/Scope**: Company size consistent with existing bulk endpoints (`list_employees`,
`schedule-overview`) — tens to a few hundred employees, no pagination (matches spec Assumptions)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Vertical Slice Architecture**: PASS. Change stays entirely within the existing
  `app/slices/employees/get_salary_summary/` slice (`ui/`, `application/`, `infra/`); no
  reverse dependencies introduced.
- **II. Explicit Parameters, No Generic Containers**: PASS. `GetSalarySummary.execute` keeps
  explicit typed parameters (`month: int | None`, `year: int | None`); `employee_id` is
  simply removed, not replaced by a dict/kwargs.
- **III. Documentation-First Feature Development**: PASS, contingent on `tasks.md` including
  an explicit task to update `specs/api/employees.md`'s "Salary Summary" section (path,
  response shape, and the new itemized advances field) in the same change — tracked as a
  required task, not optional cleanup.
- **IV. Consistency Over Cleverness**: PASS. Reuses the bulk-fetch/`items`-wrapper pattern
  already established by `get_employees_schedule_overview` rather than inventing a new
  aggregation style. One touch outside `get_salary_summary` is in scope: `get_my_salary_summary`
  currently imports `SalarySummaryResponse` cross-slice, which contradicts `CLAUDE.md`'s
  schema-ownership rule ("Pydantic ... never reused elsewhere") — this plan removes that
  import by giving `get_my_salary_summary` its own local copy of the schema, fixing a
  pre-existing inconsistency rather than introducing a new one. No other unrelated files
  touched.
- **V. Data & Persistence Discipline**: N/A (no new persistence models; feature is read-only
  over existing tables).

No violations — Complexity Tracking is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/006-salary-summary-all-employees/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
app/slices/employees/get_salary_summary/
├── ui/
│   ├── route.py          # MODIFY: drop {employee_id} path param; GET /salary-summary?month&year → items[]
│   └── schemas.py         # MODIFY: response becomes items: List[SalarySummaryItem]; add nested
│                           #   SalaryAdvanceItem (slice-local, per VSA schema-ownership rule)
├── application/
│   └── use_case.py        # MODIFY: execute(month, year) — loops all employees, no employee_id param
├── infra/
│   └── repository.py      # MODIFY: bulk-fetch methods (all employees, advances-by-employee,
│                           #   lateness config, journey timestamps-by-user), mirroring the
│                           #   bulk pattern already used by get_employees_schedule_overview/infra/repository.py
└── domain/
    └── rules.py            # UNCHANGED: calculate_daily_delay_minutes/is_late/calculate_deduction reused as-is

app/slices/employees/get_my_salary_summary/
└── ui/
    ├── schemas.py          # MODIFY: define a local SalarySummaryResponse (same 9 fields)
    │                        #   instead of importing it from get_salary_summary/ui/schemas.py
    └── route.py             # MODIFY: import updated to the local schema (no behavior change)

specs/api/employees.md       # MODIFY: "Salary Summary" section — new path/shape, remove old
                              #   {employee_id} path, document itemized advances field
```

**Structure Decision**: Single existing FastAPI backend (Vertical Slice Architecture, per
`CLAUDE.md`/constitution). No new slice: this feature modifies the existing
`get_salary_summary` slice in place, following the bulk-endpoint precedent set by the
sibling `get_employees_schedule_overview` slice. The employee self-service
`get_my_salary_summary` slice receives one minimal, behavior-preserving touch — its own
local response schema, replacing a pre-existing cross-slice import — per spec Assumptions;
its route, behavior, and response shape are otherwise unaffected.

## Complexity Tracking

> Not applicable — Constitution Check reported no violations.
