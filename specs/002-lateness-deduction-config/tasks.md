---

description: "Task list for HR Lateness Tolerance & Salary Deduction Configuration"
---

# Tasks: HR Lateness Tolerance & Salary Deduction Configuration

**Input**: Design documents from `/specs/002-lateness-deduction-config/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/employees-lateness.md, quickstart.md

**Tests**: Not included — project policy is to not write automated tests for new feature work (constitution "Development Workflow & Quality Gates"). Verification is manual, via `quickstart.md`.

**Organization**: Tasks are grouped by user story (spec.md: US1 = P1, US2 = P2, US3 = P3) so each can be implemented and verified independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on an incomplete task)
- **[Story]**: Which user story this task belongs to (US1/US2/US3) — omitted for Setup/Foundational/Polish

## Path Conventions

Single FastAPI project (Vertical Slice Architecture). All paths are relative to the repo root.

---

## Phase 1: Setup

**Purpose**: Add the new persistence entity this feature is built on. No new dependencies are required (FastAPI/Tortoise-ORM/Aerich already in `requirements.txt`).

- [X] T001 [P] Add `LatenessConfiguration` Tortoise model to `app/shared/db/models.py`: `id` (UUID pk), `enabled` (bool, default `False`), `expected_entrance_time` (Time, required, no app-level default), `tolerance_minutes` (int, default `0`), `deduction_interval_minutes` (int, default `0`), `deduction_value` (Decimal(10,2), default `0`), `created_at` (auto_now_add), `updated_at` (auto_now) — field list and rationale in `data-model.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Schema + seed row that every user story depends on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 Run `aerich migrate --name lateness_configuration` to generate the schema migration for the new table under `migrations/models/` — depends on T001 (generated `migrations/models/18_20260718183443_lateness_configuration.py`)
- [X] T003 Hand-append the seed `INSERT` to the migration file generated in T002 (single row: `enabled=false`, `tolerance_minutes=0`, `deduction_interval_minutes=0`, `deduction_value=0`, `expected_entrance_time=CURRENT_TIME`, guarded by `WHERE NOT EXISTS` since this table has no natural unique key for `ON CONFLICT`), following the precedent in `migrations/models/8_20260206102320_update.py` and `migrations/models/12_20260617170624_update.py` — depends on T002. Applied via `aerich upgrade` and verified the seed row exists. This is the one documented exception to "don't hand-edit migrations" (see `plan.md` Complexity Tracking).

**Checkpoint**: Table exists with its default row seeded in migration-driven environments; app-level "no row → disabled defaults" fallback (data-model.md) covers `GENERATE_SCHEMAS`-based dev DBs. User story implementation can begin.

---

## Phase 3: User Story 1 - HR configures lateness rules (Priority: P1) 🎯 MVP

**Goal**: HR can view and fully replace the singleton lateness configuration (entrance time, tolerance, deduction interval, deduction value, enabled flag) via two new endpoints.

**Independent Test**: `PUT /employees/lateness-config` with valid values, then `GET /employees/lateness-config` returns exactly what was submitted; a second `PUT` updates the same row rather than creating a new one; submitting a negative tolerance/value or a zero/negative interval is rejected.

### Implementation for User Story 1

- [X] T004 [P] [US1] Create `GetLatenessConfigurationRepository` in `app/slices/employees/get_lateness_config/infra/repository.py` — fetch the first `LatenessConfiguration` row (`order_by("created_at")`), or return in-memory disabled/zero defaults if none exists (data-model.md "Absence Handling")
- [X] T005 [P] [US1] Create `GetLatenessConfiguration` use case in `app/slices/employees/get_lateness_config/application/use_case.py` — no params, delegates to the repository
- [X] T006 [P] [US1] Create `LatenessConfigResponse` schema in `app/slices/employees/get_lateness_config/ui/schemas.py` per `contracts/employees-lateness.md` (`enabled: bool, expected_entrance_time: time, tolerance_minutes: int, deduction_interval_minutes: int, deduction_value: Decimal`)
- [X] T007 [US1] Create `GET /lateness-config` route in `app/slices/employees/get_lateness_config/ui/route.py`, guarded by `ensure_hr`, wiring `use_case = GetLatenessConfiguration(GetLatenessConfigurationRepository())` at import time (pattern from `app/slices/employees/get_salary_summary/ui/route.py`) — depends on T004, T005, T006
- [X] T008 [P] [US1] Create `UpdateLatenessConfigurationRepository` in `app/slices/employees/update_lateness_config/infra/repository.py` — fetch the first row and update it in place, or create it if none exists (upsert), returning the persisted row. Normalizes naive `time` input to UTC before persisting (column is `TIMETZ`).
- [X] T009 [P] [US1] Create `UpdateLatenessConfiguration` use case in `app/slices/employees/update_lateness_config/application/use_case.py` with explicit typed params (`enabled: bool, expected_entrance_time: time, tolerance_minutes: int, deduction_interval_minutes: int, deduction_value: Decimal`); raise `ValueError` when `tolerance_minutes < 0`, `deduction_interval_minutes <= 0`, or `deduction_value < 0` (FR-004)
- [X] T010 [P] [US1] Create `UpdateLatenessConfigRequest` (mirrors the five fields, all required) and reuse/duplicate `LatenessConfigResponse` in `app/slices/employees/update_lateness_config/ui/schemas.py`
- [X] T011 [US1] Create `PUT /lateness-config` route in `app/slices/employees/update_lateness_config/ui/route.py`, guarded by `ensure_hr`, mapping `ValueError` → `400` (matches existing `create_employee`/`update_employee` convention throughout this repo, not the `422` drafted in `contracts/employees-lateness.md` during planning) — depends on T008, T009, T010
- [X] T012 [US1] Register both new routers in `app/slices/employees/urls.py` as fixed-prefix routes, before the existing dynamic `/{employee_id}` routes — depends on T007, T011. Also had to move `update_employee_router`/`delete_employee_router` (which own dynamic `PUT`/`DELETE /{employee_id}`) below the new routers: `update_employee`'s dynamic `PUT /{employee_id}` was intercepting `PUT /lateness-config` since it was registered earlier in the list than the plan anticipated.
- [X] T013 [P] [US1] Update `specs/api/employees.md` with the two new `lateness-config` endpoints (status code corrected to `400` to match T011)

**Checkpoint**: User Story 1 is fully functional and independently testable (config CRUD works even though nothing consumes it yet).

---

## Phase 4: User Story 2 - HR reviews delay and deduction on salary summary (Priority: P2)

**Goal**: `GET /employees/salary-summary/{employee_id}` reports `late_delay_minutes`, `late_days_count`, `late_deduction_total`, and folds the deduction into `net_salary`.

**Independent Test**: With the configuration enabled and known `JourneyRegistry` data for an employee's linked user, the salary summary's delay/deduction figures match manual calculation from `contracts/employees-lateness.md`'s worked example; with the configuration disabled (or absent), all three new fields are `0`/`0.00` and `net_salary` matches the pre-feature formula.

### Implementation for User Story 2

- [X] T014 [P] [US2] Create `app/slices/employees/get_salary_summary/domain/rules.py` with pure functions (no framework imports): `calculate_daily_delay_minutes(entrance_at: datetime, expected_entrance_time: time) -> int` (0 if entrance at/before expected), `is_late(delay_minutes: int, tolerance_minutes: int) -> bool`, `calculate_deduction(delay_minutes: int, deduction_interval_minutes: int, deduction_value: Decimal) -> Decimal` (returns `0` when `deduction_interval_minutes <= 0`; otherwise `floor(delay_minutes / deduction_interval_minutes) * deduction_value`) — formulas per `data-model.md` "Daily Delay"
- [X] T015 [P] [US2] Extend `GetSalarySummaryRepository` in `app/slices/employees/get_salary_summary/infra/repository.py` to additionally return: the current `LatenessConfiguration` (or defaults, reusing the same "first row or defaults" approach as T004), the employee's linked `user_id`, and `JourneyRegistry` timestamps (`is_deleted=False`) for that user within the requested month's date range, grouped/orderable by calendar day
- [X] T016 [US2] Extend `GetSalarySummary.execute` in `app/slices/employees/get_salary_summary/application/use_case.py`: when `employee.user_id` is set and the config is enabled, group the fetched timestamps by calendar day, take the earliest per day as that day's entrance, run each through `domain/rules.py` to get `delay_minutes`/`is_late`/`deduction`, aggregate `late_delay_minutes` (sum of `delay_minutes` for late days), `late_days_count` (count of late days), and `late_deduction_total` (sum of `deduction`); when the config is disabled/absent or `employee.user_id` is `None`, all three are `0`; subtract `late_deduction_total` from `net_salary` in addition to `advances` — depends on T014, T015
- [X] T017 [P] [US2] Extend `SalarySummaryResponse` in `app/slices/employees/get_salary_summary/ui/schemas.py` with `late_delay_minutes: int`, `late_days_count: int`, `late_deduction_total: Decimal`
- [X] T018 [P] [US2] Update the "Salary Summary" section of `specs/api/employees.md` with the three new fields and the changed `net_salary` formula, per `contracts/employees-lateness.md`

**Checkpoint**: User Stories 1 AND 2 both work independently — configuring rules and seeing them reflected in salary summaries.

---

## Phase 5: User Story 3 - HR disables lateness deductions without losing configured rules (Priority: P3)

**Goal**: Confirm toggling `enabled` off immediately zeroes delay/deduction on salary summaries, and toggling back on restores the exact same stored values without HR having to re-enter them.

**Independent Test**: Two `PUT /employees/lateness-config` calls (disable, then re-enable with the same values) around a `GET /employees/salary-summary/{employee_id}` call in between — deduction disappears then reappears unchanged; the row count never exceeds one.

### Verification for User Story 3

This story requires no new production code — it is a direct consequence of US1's upsert-in-place update (T008/T009) and US2's enabled-flag gate (T016). It exists as its own phase because the spec calls it out as an independently valuable, independently testable scenario.

- [X] T019 [US3] Manually run `quickstart.md` steps 2, 4, 5, and 6 end-to-end: confirm disabling zeroes `late_delay_minutes`/`late_days_count`/`late_deduction_total` and restores the pre-feature `net_salary` formula, and that re-enabling with the same values restores the identical deduction from step 4. Verified live against the dev server + dev DB: enabled config + a 10:05 check-in (08:00 expected, 10min tolerance, 60min interval, 6.80 value) produced `late_delay_minutes:125, late_days_count:1, late_deduction_total:13.60, net_salary:986.40`; disabling reset all three to zero and `net_salary` to `986.40+13.60=1000.00`; re-enabling with the same values restored the exact original deduction — single-row upsert (T009) and enabled-flag gate (T016) both confirmed correct. Test journey row and config values reset afterward to avoid leaving dev-DB side effects.

**Checkpoint**: All three user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T020 [P] Run `python app/main.py` and execute the full `quickstart.md` flow (steps 1-6) end-to-end against a live dev server. Ran via `uvicorn` against the dev DB; step 3 (producing a late check-in) used a direct `JourneyRegistry.create()` instead of the multipart `/journey/` upload endpoint — equivalent effect on the table this feature reads, without needing to forge a second (non-HR) user's auth + selfie upload. All other steps ran exactly as written. Test data (the inserted journey row, the enabled config values) cleaned up / reset afterward.
- [X] T021 Diff the implemented routes/schemas/guards against `specs/api/employees.md` to confirm the contract is exact (use the `update-api-contract` skill if available) — depends on T013, T018, T020. Ran the `update-api-contract` skill: found and fixed one undocumented quirk (`expected_entrance_time` serializes with a trailing `Z` once a real config row exists, but without one in the no-row default case); everything else already matched.
- [X] T022 Review all new/changed files for constitution compliance: explicit typed use-case params (no `dict`/`**kwargs`), business logic kept out of `ui/`/`infra/`, `Decimal` used for `deduction_value`/`late_deduction_total`, UUID pk + `created_at`/`updated_at` on the new model — depends on T021. Confirmed: both use cases take explicit typed params; validation lives in `UpdateLatenessConfiguration.execute` (application layer), not in `ui/`/`infra/`; delay/deduction math lives in pure `domain/rules.py`; `LatenessConfiguration` has UUID pk + `created_at`/`updated_at`; `deduction_value`/`late_deduction_total` are `Decimal` throughout.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on T001 — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Phase 2 completion only
- **User Story 2 (Phase 4)**: Depends on Phase 2 completion only — does **not** require US1's endpoints to exist (it reads the same table directly), but is only *meaningfully* testable once US1 lets you set non-default config values
- **User Story 3 (Phase 5)**: Depends on both US1 (T008/T009) and US2 (T016) being complete — it verifies their combined behavior rather than adding code
- **Polish (Phase 6)**: Depends on all three user stories being complete

### Within Each User Story

- US1: repository/use-case/schema tasks (T004-T006, T008-T010) before their respective route tasks (T007, T011); both routes before `urls.py` wiring (T012)
- US2: `domain/rules.py` (T014) and repository extension (T015) before the use-case extension (T016); schema extension (T017) can proceed in parallel with T016 since it only needs the field list, not the finished computation

### Parallel Opportunities

- T004, T005, T006 (US1 GET-side files) can run in parallel
- T008, T009, T010 (US1 PUT-side files) can run in parallel
- T013 (docs) can run in parallel with T012 (wiring) — different files
- T014, T015 (US2) can run in parallel — different files, no code dependency between them
- T017, T018 (US2 schema + docs) can run in parallel with T016 once T014/T015 are done

---

## Parallel Example: User Story 1

```bash
# GET-side files together:
Task: "Create GetLatenessConfigurationRepository in app/slices/employees/get_lateness_config/infra/repository.py"
Task: "Create GetLatenessConfiguration use case in app/slices/employees/get_lateness_config/application/use_case.py"
Task: "Create LatenessConfigResponse schema in app/slices/employees/get_lateness_config/ui/schemas.py"

# PUT-side files together:
Task: "Create UpdateLatenessConfigurationRepository in app/slices/employees/update_lateness_config/infra/repository.py"
Task: "Create UpdateLatenessConfiguration use case in app/slices/employees/update_lateness_config/application/use_case.py"
Task: "Create UpdateLatenessConfigRequest schema in app/slices/employees/update_lateness_config/ui/schemas.py"
```

---

## Implementation Strategy

### MVP Scope

Spec priority order names User Story 1 as P1, but US1 alone (config CRUD with nothing consuming it) delivers no visible value to HR on its own — the real MVP is **US1 + US2 together**: HR can configure rules and immediately see them reflected in salary summaries. Treat Phase 3 + Phase 4 as the combined MVP; Phase 5 (US3) only verifies behavior that already exists once the MVP is done.

1. Complete Phase 1 (Setup) + Phase 2 (Foundational) — table exists, seeded
2. Complete Phase 3 (US1) — HR can configure
3. Complete Phase 4 (US2) — salary summaries reflect it → **MVP checkpoint**
4. Complete Phase 5 (US3) — verify disable/re-enable behavior, fix regressions if found
5. Complete Phase 6 (Polish) — full quickstart run + contract diff + constitution review

### Incremental Delivery

Each phase checkpoint (end of Phase 3, 4, 5) is independently demoable: after Phase 3 HR can manage settings (no visible effect yet); after Phase 4 the settings visibly affect payroll; after Phase 5 the disable/re-enable lifecycle is confirmed safe.

---

## Notes

- [P] tasks touch different files with no dependency on an incomplete task
- No automated tests are generated per project policy — `quickstart.md` is the verification mechanism (T019, T020)
- T002/T003 are the one place this feature deviates from "don't hand-edit migrations" — justified in `plan.md` Complexity Tracking and pre-approved by the user's `/speckit-plan` input
- Commit after each task or logical group; stop at any checkpoint to validate a story independently
