# Implementation Plan: Employee Self-Service Salary Access

**Branch**: `003-employee-self-service` | **Date**: 2026-07-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-employee-self-service/spec.md`

## Summary

Add two new read-only, employee-scoped endpoints — `GET /employees/me/salary-summary` and `GET /employees/me/salary-advances` — that let an authenticated Employee-role user view their own salary summary (including the lateness delay/deduction breakdown) and their own advance history, with the target employee always resolved from the caller's linked `Employee` record (`current_user.employee`), never from a client-supplied id. Each endpoint is its own self-contained vertical slice with its own `application/use_case.py` and `infra/repository.py` — mirroring this codebase's existing `list_my_journeys` (self-service sibling of `admin_list_journeys`) precedent, where the self-service slice never imports another slice's use case or repository class. The only cross-slice reuse is of pure `domain/rules.py` functions (already established by `update_loan` importing `create_loan.domain.rules`) and `ui/schemas.py` response models (already established by `list_my_journeys` reusing `register_journey`'s `JourneyResponse`). No new models or migrations are introduced. Both new routes are gated by the existing `ensure_employee` guard instead of `ensure_hr`.

## Technical Context

**Language/Version**: Python 3.11+ (FastAPI + Tortoise-ORM, matches existing codebase)

**Primary Dependencies**: FastAPI, Tortoise-ORM, pydantic — all already in `requirements.txt`; no new dependencies introduced.

**Storage**: PostgreSQL via Tortoise-ORM. No schema changes — reuses the existing `employee`, `salary_advance`, and `lateness_configuration` tables exactly as queried by the existing HR-facing use cases.

**Testing**: N/A — project policy is to not write automated tests for new feature work (constitution "Development Workflow & Quality Gates").

**Target Platform**: Vercel Python serverless function (`api/index.py`), same as the rest of the API.

**Project Type**: Web service (single FastAPI backend) — extends the existing `employees` vertical slice context.

**Performance Goals**: No feature-specific target; identical cost profile to the existing HR-facing endpoints since the same use cases/repositories are invoked (single-employee lookup, bounded monthly attendance/advance scan).

**Constraints**: Must follow Vertical Slice Architecture; the target employee_id MUST be derived server-side from `current_user.employee`, never accepted as a path/query parameter, to prevent IDOR; new fixed-path routers (`/me/salary-summary`, `/me/salary-advances`) MUST be registered in `app/slices/employees/urls.py` before the dynamic `/{employee_id}` routers (`get_employee`, `update_employee`, `delete_employee`), matching the existing ordering convention in that file, so `/employees/me/...` is never captured by `/employees/{employee_id}`; `specs/api/employees.md` must be updated in the same change per the standing API-contract rule.

**Scale/Scope**: Two new GET endpoints; no changes to existing HR-facing endpoints' behavior, request/response shapes, or permissions.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Vertical Slice Architecture** — PASS. Two new, fully self-contained feature folders, `get_my_salary_summary/` and `list_my_salary_advances/`, under `app/slices/employees/`, each with its own `application/use_case.py` and `infra/repository.py` — no slice imports another slice's use case or repository class, matching the existing `list_my_journeys` (vs. `admin_list_journeys`) precedent. `get_my_salary_summary`'s use case imports the pure functions in `get_salary_summary/domain/rules.py` (no framework imports, stateless), the same kind of domain-layer reuse already established by `update_loan` importing `create_loan.domain.rules`.
- **II. Explicit Parameters** — PASS. `GetMySalarySummary.execute(employee_id, month, year)` and `ListMyAdvances.execute(employee_id, month, year)` are new use cases with explicit typed parameters, no dict/kwargs. The routes compute `employee_id` from `current_user.employee.id` before calling them.
- **III. Documentation-First** — PASS (this plan + `specs/api/employees.md` update are part of the deliverable; tracked as explicit tasks).
- **IV. Consistency Over Cleverness** — PASS. Reuses the existing `employees` context and the existing `ensure_employee` guard (already added to `app/shared/security/permissions.py` on the current branch, currently unused) instead of inventing new permission logic; reuses the existing `ui/schemas.py` response models (`SalarySummaryResponse`, `SalaryAdvanceItem`) by importing them, the same cross-slice schema reuse already established by `list_my_journeys` importing `JourneyResponse` and `update_loan` importing `LoanResponse`; follows the same "new sibling feature folder per distinct action, own use case/repository" pattern already established by `list_my_journeys`/`admin_list_journeys` and `get_lateness_config`/`update_lateness_config`, rather than branching identity-resolution logic inside the existing HR routes or importing another slice's use case/repository.
- **V. Data & Persistence Discipline** — PASS. No new persistence models, no migration required — this feature only adds a new access path onto already-modeled data. The new repositories duplicate a small amount of query logic already present in `get_salary_summary/infra/repository.py` and `list_salary_advances/infra/repository.py`; this is intentional duplication over cross-slice coupling, consistent with how `list_my_journeys`/`admin_list_journeys` already duplicate their near-identical `JourneyRegistry` filter queries today.

**Result**: PASS (no violations, no Complexity Tracking entries required).

## Project Structure

### Documentation (this feature)

```text
specs/003-employee-self-service/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output
├── quickstart.md         # Phase 1 output
└── contracts/
    └── employees-self-service.md
```

### Source Code (repository root)

```text
app/shared/security/permissions.py                # ensure_employee already added (unused on branch), now consumed
app/shared/security/current_user.py               # prefetch_related("roles","employee") already added, now consumed

app/slices/employees/
├── get_salary_summary/                             # UNCHANGED
│   ├── domain/rules.py                             #   calculate_daily_delay_minutes/is_late/calculate_deduction — imported (not modified) by the new use case below
│   └── ui/schemas.py                                #   SalarySummaryResponse — imported (not modified) by the new route below
├── list_salary_advances/                           # UNCHANGED
│   └── ui/schemas.py                                #   SalaryAdvanceItem — imported (not modified) by the new route below
├── get_my_salary_summary/                          # NEW — fully self-contained slice
│   ├── application/use_case.py                     # GetMySalarySummary (own class; imports get_salary_summary.domain.rules functions)
│   ├── infra/repository.py                          # GetMySalarySummaryRepository (own class; own Employee/SalaryAdvance/LatenessConfiguration/JourneyRegistry queries)
│   └── ui/
│       ├── route.py                                # GET /employees/me/salary-summary
│       └── schemas.py                               # re-exports SalarySummaryResponse from get_salary_summary.ui.schemas (import, not a redefinition)
├── list_my_salary_advances/                        # NEW — fully self-contained slice
│   ├── application/use_case.py                     # ListMyAdvances (own class)
│   ├── infra/repository.py                          # ListMyAdvancesRepository (own class; own SalaryAdvance query)
│   └── ui/
│       ├── route.py                                # GET /employees/me/salary-advances
│       └── schemas.py                               # re-exports SalaryAdvanceItem from list_salary_advances.ui.schemas (import, not a redefinition)
└── urls.py                                          # + two new routers registered in the fixed-prefix block, before the dynamic {employee_id} routers

specs/api/employees.md                              # updated to document the two new endpoints
```

**Structure Decision**: Two new, fully self-contained sibling feature folders under the existing `employees` context — own `application/use_case.py` and own `infra/repository.py` each, per Vertical Slice Architecture — mirroring the codebase's existing `list_my_journeys` (self-service) vs. `admin_list_journeys` (admin-facing) pair, where the self-service slice never imports the admin slice's use case or repository even though the underlying query is nearly identical. The two new repositories duplicate the small amount of query logic already in `get_salary_summary`'s and `list_salary_advances`'s repositories (employee/advances lookup, lateness config + journey timestamps, advance filtering) rather than importing those repository classes — intentional duplication over cross-slice infra coupling, consistent with `list_my_journeys`/`admin_list_journeys` today. Two narrow, already-established forms of cross-slice reuse are kept: (1) `get_my_salary_summary`'s use case imports the pure, stateless functions from `get_salary_summary/domain/rules.py`, the same way `update_loan` already imports `create_loan.domain.rules` — domain-rule reuse across sibling slices is an existing pattern, unlike use-case/repository reuse; (2) both new `ui/schemas.py` import (not redefine) the existing `SalarySummaryResponse`/`SalaryAdvanceItem` response models, the same way `list_my_journeys/ui/route.py` already imports `JourneyResponse` from `register_journey` and `update_loan/ui/route.py` imports `LoanResponse` from `create_loan` — response-schema reuse across slices is likewise already established practice in this codebase, independent of the use-case/repository rule.

## Complexity Tracking

> Fill ONLY if Constitution Check has violations that must be justified

*No violations — table intentionally omitted.*
