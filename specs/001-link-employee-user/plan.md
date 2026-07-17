# Implementation Plan: Link Employee to User Account

**Branch**: `001-link-employee-user` | **Date**: 2026-07-17 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-link-employee-user/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Allow HR to optionally associate an existing `User` account with an `Employee` record at
creation and at edit time, with the association enforced as one-to-one (a user account can
be linked to at most one employee) and fully optional in both directions. Technical
approach: add a nullable, unique `ForeignKeyField` from `Employee` to `User`; extend the
existing `create_employee` and `update_employee` slices' schemas/use cases/repositories
with an explicit `user_id` parameter (plus a derived `clear_user` flag on update to
disambiguate "omitted" from "explicitly cleared"); surface `user_id` in the shared
`EmployeeResponse` used by `create_employee`, `update_employee`, `get_employee`, and
`list_employees`; reuse the existing `partner_loan/create_loan` pattern for
not-found/conflict validation and HTTP status mapping. No new slice, no new dependency, no
hand-authored migration (see research.md).

## Technical Context

**Language/Version**: Python 3.11+ (existing project runtime)

**Primary Dependencies**: FastAPI, Tortoise-ORM, Aerich, Pydantic v2 — all already present in `requirements.txt`; no new dependency introduced

**Storage**: PostgreSQL via Tortoise-ORM; schema change via `aerich migrate`/`aerich upgrade` (not hand-authored)

**Testing**: N/A — project policy explicitly forbids adding tests for new feature work (see Constitution, Development Workflow & Quality Gates)

**Target Platform**: Linux server / Vercel Python serverless function (`api/index.py`)

**Project Type**: web-service (single FastAPI backend, Vertical Slice Architecture)

**Performance Goals**: None beyond existing endpoint responsiveness; the spec implies no new performance target

**Constraints**: One-to-one, optional Employee↔User invariant must be enforced at the DB level (`unique=True`); no new third-party dependencies; schema changes only via Aerich, never hand-edited

**Scale/Scope**: One new nullable+unique FK column on `Employee`; touches 4 existing slices (`create_employee`, `update_employee`, `get_employee`, `list_employees`) plus `specs/api/employees.md`; no new slice folder required

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Result |
|---|---|---|
| I. Vertical Slice Architecture | Change stays inside the 4 existing employee slices' existing `ui/`, `application/`, `infra/` files; no reverse dependencies introduced | PASS |
| II. Explicit Parameters, No Generic Containers | `user_id: Optional[UUID]` and `clear_user: bool` are explicit, typed use-case params; no dict/`**kwargs` crosses layers | PASS |
| III. Documentation-First Feature Development | This plan follows `/speckit-specify` → `/speckit-plan`; `specs/api/employees.md` update is tracked as a required implementation task (contracts/employees.md documents the delta now) | PASS |
| IV. Consistency Over Cleverness | Reuses `Sale.partner` nullable-FK shape, `partner_loan/create_loan`'s not-found/conflict `ValueError` → 404/400 pattern, and existing `ensure_hr` permission check; no new abstraction introduced; clear-user handling scoped only to the new field (see research.md Decision 2) | PASS |
| V. Data & Persistence Discipline | `Employee` keeps its UUID PK and `created_at`; new FK is nullable+unique; migration generated via `aerich migrate`, not hand-authored | PASS |

No violations. Complexity Tracking table is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/001-link-employee-user/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── employees.md
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

This feature extends existing slices in place — no new slice folder is created.

```text
app/shared/db/
└── models.py                                   # Employee gains `user` FK field

app/slices/employees/
├── create_employee/
│   ├── application/use_case.py                 # + user_id param, existence/uniqueness check
│   ├── infra/repository.py                     # + user_id passthrough to Employee.create
│   └── ui/
│       ├── route.py                            # + 404/400 ValueError mapping
│       └── schemas.py                          # CreateEmployeeRequest + user_id; EmployeeResponse + user_id
├── update_employee/
│   ├── application/use_case.py                 # + user_id, clear_user params
│   ├── infra/repository.py                     # + conditional set/clear of employee.user_id
│   └── ui/
│       ├── route.py                            # + derive clear_user from model_fields_set; 404/400 mapping
│       └── schemas.py                          # EmployeeUpdate + user_id; EmployeeResponse + user_id
├── get_employee/ui/schemas.py                   # EmployeeResponse + user_id
└── list_employees/ui/schemas.py                 # EmployeeResponse + user_id

specs/api/employees.md                           # updated to match (mandatory, same change)
```

**Structure Decision**: Single-project web service (existing FastAPI backend). This is an
extension of four already-existing employee slices plus the shared ORM model — not a new
`<context>/<feature_name>` slice — so it follows Constitution IV by touching only the
files each slice already owns, in their existing fixed layout
(`application/use_case.py`, `infra/repository.py`, `ui/route.py`, `ui/schemas.py`).

## Complexity Tracking

No Constitution Check violations — this section is intentionally empty.
