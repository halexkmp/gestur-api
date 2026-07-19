# Implementation Plan: HR Lateness Tolerance & Salary Deduction Configuration

**Branch**: `002-lateness-deduction-config` | **Date**: 2026-07-18 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-lateness-deduction-config/spec.md`

## Summary

Add a single, system-wide `LatenessConfiguration` record (expected entrance time, tolerance minutes, deduction interval minutes, deduction value, enabled flag) managed by HR via two new endpoints nested under the existing `employees` slice, and extend `GET /employees/salary-summary/{employee_id}` to report delay minutes, late-days count, and lateness deduction, folded into net salary. Delay is derived at request time from each employee's earliest daily `JourneyRegistry` check-in — no new attendance data is captured. The configuration starts disabled with all-zero numeric defaults and is seeded as a single row via a migration-time `INSERT`, per explicit user instruction.

## Technical Context

**Language/Version**: Python 3.11+ (FastAPI + Tortoise-ORM, matches existing codebase)

**Primary Dependencies**: FastAPI, Tortoise-ORM, Aerich (migrations), pydantic / pydantic-settings — all already in `requirements.txt`; no new dependencies introduced.

**Storage**: PostgreSQL via Tortoise-ORM, one new table (`lateness_configuration`), no changes to existing tables.

**Testing**: N/A — project policy is to not write automated tests for new feature work (constitution "Development Workflow & Quality Gates").

**Target Platform**: Vercel Python serverless function (`api/index.py`), same as the rest of the API.

**Project Type**: Web service (single FastAPI backend) — extends the existing `employees` vertical slice context.

**Performance Goals**: No feature-specific target; matches existing endpoints (single-row config read, bounded per-employee monthly attendance scan of at most ~4 records/day × ~31 days).

**Constraints**: Must follow Vertical Slice Architecture; use-case constructors take explicit typed params (no `dict`/`**kwargs`); repositories stay persistence-only; `specs/api/employees.md` must be updated in the same change per the standing API-contract rule.

**Scale/Scope**: One singleton configuration row system-wide; salary summary calculation scoped to one employee's one requested month at a time (existing pattern, unchanged).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Vertical Slice Architecture** — PASS. New feature folders `get_lateness_config/` and `update_lateness_config/` under `app/slices/employees/`, each with `application/`, `infra/`, `ui/`; `get_salary_summary/` gets its existing `application/`+`infra/` extended in place, no reverse dependencies introduced.
- **II. Explicit Parameters** — PASS. `UpdateLatenessConfiguration.execute(...)` takes explicit typed params (`expected_entrance_time: time, tolerance_minutes: int, deduction_interval_minutes: int, deduction_value: Decimal, enabled: bool`); no dict/kwargs crossing layers.
- **III. Documentation-First** — PASS (this plan + `specs/api/employees.md` update are part of the deliverable; tracked as explicit tasks).
- **IV. Consistency Over Cleverness** — PASS. Reuses the existing `employees` context (already home to salary-related sub-resources) instead of introducing a new top-level context for one settings resource; reuses `ensure_hr` guard already applied to every other endpoint in this context; update endpoint is a full-replace PUT, mirroring the existing `update_employee`-adjacent patterns rather than inventing partial-patch semantics for a singleton.
- **V. Data & Persistence Discipline** — PASS with one flagged exception (see Complexity Tracking): UUID pk, `created_at`/`updated_at`, `Decimal` for the monetary field are all followed; the single seed row is inserted via a **hand-appended INSERT inside an Aerich-generated migration**, which is an explicit, narrow deviation from "agents MUST NOT hand-author or hand-edit migration files" — justified below.

**Result**: PASS (one documented, user-directed exception).

## Project Structure

### Documentation (this feature)

```text
specs/002-lateness-deduction-config/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output
├── quickstart.md         # Phase 1 output
├── contracts/
│   └── employees-lateness.md
└── tasks.md              # Phase 2 output (/speckit-tasks, not this command)
```

### Source Code (repository root)

```text
app/shared/db/models.py                          # + LatenessConfiguration model
app/shared/db/enums.py                            # (no changes expected)

app/slices/employees/
├── get_lateness_config/
│   ├── application/use_case.py                   # GetLatenessConfiguration
│   ├── infra/repository.py                        # GetLatenessConfigurationRepository
│   └── ui/
│       ├── route.py                                # GET /employees/lateness-config
│       └── schemas.py                              # LatenessConfigResponse
├── update_lateness_config/
│   ├── application/use_case.py                    # UpdateLatenessConfiguration
│   ├── infra/repository.py                        # UpdateLatenessConfigurationRepository
│   └── ui/
│       ├── route.py                                # PUT /employees/lateness-config
│       └── schemas.py                              # UpdateLatenessConfigRequest / LatenessConfigResponse
├── get_salary_summary/
│   ├── application/use_case.py                     # extended: delay + deduction fields
│   ├── domain/rules.py                              # NEW: pure delay/deduction calculation
│   ├── infra/repository.py                          # extended: fetch config + journey timestamps
│   └── ui/schemas.py                                # extended response fields
└── urls.py                                          # + two new routers registered

specs/api/employees.md                              # updated to match new/changed endpoints

migrations/models/<NN>_<ts>_lateness_configuration.py   # aerich-generated schema + hand-appended seed INSERT
```

**Structure Decision**: Extend the existing `employees` context rather than create a new one — the feature is HR configuration that exclusively feeds the `employees` salary summary, and `employees` already hosts adjacent salary sub-resources (`salary-advances`, `salary-summary`) under the same `ensure_hr` guard. Delay/deduction math lives in a new `domain/rules.py` inside `get_salary_summary` (pure functions, no framework imports) so the repository stays persistence-only and the use case stays orchestration-only, per VSA.

## Complexity Tracking

> Fill ONLY if Constitution Check has violations that must be justified

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|---------------------------------------|
| Hand-appended `INSERT` inside an Aerich-generated migration file (Principle V normally forbids hand-editing migrations) | User explicitly required the default disabled row to be seeded via migration, not lazily created by application code on first read | Relying on the app to lazily create the row on first `GET`/`PUT` was rejected because the user explicitly asked for the row to exist via migration; this repo already has two precedents for the same hand-appended-`INSERT`-after-`aerich migrate` pattern (`migrations/models/8_..._update.py`, `12_..._update.py`, both seeding the `role` table), so this is a repeated, established exception rather than a novel one |
