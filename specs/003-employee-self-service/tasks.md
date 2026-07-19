---

description: "Task list for Employee Self-Service Salary Access"
---

# Tasks: Employee Self-Service Salary Access

**Input**: Design documents from `/specs/003-employee-self-service/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/employees-self-service.md, quickstart.md

**Tests**: Not included — project policy is to not write automated tests for new feature work (constitution "Development Workflow & Quality Gates"). Verification is manual, via `quickstart.md`.

**Organization**: Tasks are grouped by user story (spec.md: US1 = P1, US2 = P2) so each can be implemented and verified independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on an incomplete task)
- **[Story]**: Which user story this task belongs to (US1/US2) — omitted for Setup/Foundational/Polish

## Path Conventions

Single FastAPI project (Vertical Slice Architecture). All paths are relative to the repo root.

**Architecture note (binding on every task below)**: Per `research.md` Decision 1, `get_my_salary_summary` and `list_my_salary_advances` are fully self-contained slices — neither may import `GetSalarySummary`/`GetSalarySummaryRepository`/`ListSalaryAdvances`/`ListSalaryAdvancesRepository` from the HR-facing slices. The only permitted cross-slice imports are (a) the pure functions in `get_salary_summary/domain/rules.py`, and (b) the `ui/schemas.py` response models `SalarySummaryResponse`/`SalaryAdvanceItem`.

---

## Phase 1: Setup

**Purpose**: Confirm the prerequisites this feature depends on. No new dependencies, models, or migrations are required.

- [X] T001 Confirm prerequisite groundwork is present: `ensure_employee` guard exists in `app/shared/security/permissions.py`, and `get_current_user` in `app/shared/security/current_user.py` calls `.prefetch_related("roles","employee")` so `current_user.employee` is available without an extra query. Both were already added (uncommitted) on this branch before this spec was written — no code change expected here, just confirmation before building on top of them.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Single shared identity-resolution check that both user stories depend on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 Add `resolve_own_employee_id(current_user) -> UUID` to `app/shared/security/permissions.py`: calls `ensure_employee(current_user)` (role check), then raises `HTTPException(403)` if `current_user.employee` is `None`, otherwise returns `current_user.employee.id` — the single shared check satisfying FR-004/FR-005, called identically by both new routes instead of duplicating the role-check + link-check pair in each one.

**Checkpoint**: Both new endpoints have one identity-resolution call site to depend on. User story implementation can begin.

---

## Phase 3: User Story 1 - Employee views their own salary summary (Priority: P1) 🎯 MVP

**Goal**: `GET /employees/me/salary-summary` returns the caller's own gross salary, advances total, lateness delay/deduction, and net salary — matching what HR sees for that same employee/month via the existing endpoint.

**Independent Test**: Log in as a user with the Employee role and a linked employee record, call the endpoint with and without `month`/`year`, and confirm the figures match the equivalent `GET /employees/salary-summary/{employee_id}` call made by an HR user for the same employee/month.

### Implementation for User Story 1

- [X] T003 [P] [US1] Create `GetMySalarySummaryRepository` in `app/slices/employees/get_my_salary_summary/infra/repository.py` — own queries for employee + month's advances total, the current `LatenessConfiguration` (or none), and the employee's linked user's `JourneyRegistry` timestamps for the month (mirrors the three query methods in `get_salary_summary/infra/repository.py`; do not import that repository — see Architecture note above)
- [X] T004 [P] [US1] Create `GetMySalarySummary` use case in `app/slices/employees/get_my_salary_summary/application/use_case.py` — own class, `execute(employee_id: UUID, month: int | None, year: int | None)`, defaulting month/year to today when omitted, computing lateness the same way `GetSalarySummary.execute` does (earliest check-in per day, gated by tolerance, summed deduction) by importing `calculate_daily_delay_minutes`, `is_late`, `calculate_deduction` from `app.slices.employees.get_salary_summary.domain.rules` — depends on T003
- [X] T005 [P] [US1] Create `app/slices/employees/get_my_salary_summary/ui/schemas.py` importing and re-exporting `SalarySummaryResponse` from `app.slices.employees.get_salary_summary.ui.schemas` (no redefinition — see `research.md` Decision 4)
- [X] T006 [US1] Create `GET /me/salary-summary` route in `app/slices/employees/get_my_salary_summary/ui/route.py`: `employee_id = resolve_own_employee_id(current_user)`, then calls `GetMySalarySummary.execute(employee_id, month, year)`, wiring `use_case = GetMySalarySummary(GetMySalarySummaryRepository())` at import time (existing route-module pattern) — depends on T002, T003, T004, T005
- [X] T007 [US1] Register the new router in `app/slices/employees/urls.py`, in the fixed-prefix block, before `get_employee_router`/`update_employee_router`/`delete_employee_router` (routing-order hazard: `GET /employees/{employee_id}` would otherwise attempt — and fail — to parse `"me"` as a UUID before falling through; see `research.md` Decision 3) — depends on T006
- [X] T008 [P] [US1] Update `specs/api/employees.md` with `GET /employees/me/salary-summary` per `contracts/employees-self-service.md`

**Checkpoint**: User Story 1 is fully functional and independently testable.

---

## Phase 4: User Story 2 - Employee views their own salary advance history (Priority: P2)

**Goal**: `GET /employees/me/salary-advances` returns only the caller's own advances, optionally filtered by month/year.

**Independent Test**: Log in as an employee with known advances across multiple months, call the endpoint with no filters (all own advances returned) and with a month/year filter (only that month's advances returned); confirm no other employee's advances ever appear.

### Implementation for User Story 2

- [X] T009 [P] [US2] Create `ListMyAdvancesRepository` in `app/slices/employees/list_my_salary_advances/infra/repository.py` — own `SalaryAdvance` query, always filtered by the given `employee_id`, with optional `month`/`year` narrowing (mirrors `list_salary_advances/infra/repository.py`'s filter logic minus the cross-employee case; do not import that repository — see Architecture note above)
- [X] T010 [P] [US2] Create `ListMyAdvances` use case in `app/slices/employees/list_my_salary_advances/application/use_case.py` — own class, `execute(employee_id: UUID, month: int | None, year: int | None)` — depends on T009
- [X] T011 [P] [US2] Create `app/slices/employees/list_my_salary_advances/ui/schemas.py` importing and re-exporting `SalaryAdvanceItem` from `app.slices.employees.list_salary_advances.ui.schemas` (no redefinition)
- [X] T012 [US2] Create `GET /me/salary-advances` route in `app/slices/employees/list_my_salary_advances/ui/route.py`: `employee_id = resolve_own_employee_id(current_user)`, then calls `ListMyAdvances.execute(employee_id, month, year)`, wiring `use_case = ListMyAdvances(ListMyAdvancesRepository())` at import time — depends on T002, T009, T010, T011
- [X] T013 [US2] Register the new router in `app/slices/employees/urls.py`, in the same fixed-prefix block as T007, before the dynamic `/{employee_id}` routes — depends on T012 and T007 (same file — sequential edit, not parallel)
- [X] T014 [P] [US2] Update `specs/api/employees.md` with `GET /employees/me/salary-advances` per `contracts/employees-self-service.md`

**Checkpoint**: User Stories 1 AND 2 both work independently.

---

## Phase 5: Polish & Cross-Cutting Concerns

- [X] T015 [P] Run `python app/main.py` and execute the full `quickstart.md` flow (steps 1-8) end-to-end against a live dev server, including the two 403 rejection scenarios (no linked employee record, non-Employee role) and the `/me` vs `/{employee_id}` routing sanity check — **partially completed**: no live Postgres/dev server was available in this session (user chose "skip live run, static review only" when asked), so this was done as a static review instead: (a) `app.openapi()` was built successfully with both new paths (`/employees/me/salary-summary`, `/employees/me/salary-advances`) appearing as `GET`, registered ahead of the dynamic `/{employee_id}` route — confirms step 8 (routing sanity check) without needing a DB; (b) the route/use-case/repository code was read end-to-end and confirmed to match `contracts/employees-self-service.md` and `resolve_own_employee_id`'s 403 behavior for steps 6-7. Steps 1-5 (actual numeric cross-check against HR's view with live data) are **deferred** — run manually against a dev DB before considering this feature fully verified.
- [X] T016 Diff the implemented routes/schemas/guards against `specs/api/employees.md` to confirm the contract is exact (use the `update-api-contract` skill if available) — depends on T008, T014, T015. Confirmed by direct comparison: paths, methods, optional `month`/`year` params, reused response schemas, and the EMPLOYEE-role-plus-linked-record permission description all match the implementation exactly.
- [X] T017 Review all new files for constitution compliance: explicit typed use-case params (no `dict`/`**kwargs`), business logic kept out of `ui/`/`infra/`, **no cross-slice import of another slice's `application/use_case.py` or `infra/repository.py`** (the specific concern this spec's design was revised for for `get_my_salary_summary`/`list_my_salary_advances` — confirm only `domain/rules.py` functions and `ui/schemas.py` models are shared), `Decimal` used for all monetary fields — depends on T016. Confirmed via `grep` of all `from app.slices` imports in both new slices: only `get_salary_summary.domain.rules` and the two `ui.schemas` modules are imported cross-slice; no HR-facing use case or repository is imported anywhere.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on T001 — BLOCKS both user stories
- **User Story 1 (Phase 3)**: Depends on Phase 2 completion only
- **User Story 2 (Phase 4)**: Depends on Phase 2 completion only — independent of US1's code, but shares one file (`urls.py`) with it at T007/T013
- **Polish (Phase 5)**: Depends on both user stories being complete

### Within Each User Story

- US1: repository/use-case/schema tasks (T003, T004, T005) before the route task (T006); route before `urls.py` wiring (T007)
- US2: repository/use-case/schema tasks (T009, T010, T011) before the route task (T012); route before `urls.py` wiring (T013)

### Parallel Opportunities

- T003, T004, T005 (US1) can run in parallel — different files; T004 logically depends on T003's return shape but both can be drafted concurrently against `data-model.md`
- T009, T010, T011 (US2) can run in parallel — same reasoning
- T008 (US1 docs) and T014 (US2 docs) can each run in parallel with their sibling story's route/wiring tasks
- US1 (Phase 3) and US2 (Phase 4) can be built by different people in parallel once Phase 2 is done, except for T007/T013 which touch the same file sequentially

---

## Parallel Example: User Story 1

```bash
Task: "Create GetMySalarySummaryRepository in app/slices/employees/get_my_salary_summary/infra/repository.py"
Task: "Create GetMySalarySummary use case in app/slices/employees/get_my_salary_summary/application/use_case.py"
Task: "Create app/slices/employees/get_my_salary_summary/ui/schemas.py re-exporting SalarySummaryResponse"
```

## Parallel Example: User Story 2

```bash
Task: "Create ListMyAdvancesRepository in app/slices/employees/list_my_salary_advances/infra/repository.py"
Task: "Create ListMyAdvances use case in app/slices/employees/list_my_salary_advances/application/use_case.py"
Task: "Create app/slices/employees/list_my_salary_advances/ui/schemas.py re-exporting SalaryAdvanceItem"
```

---

## Implementation Strategy

### MVP Scope

User Story 1 alone (self-service salary summary) is the MVP — it's the higher-priority, higher-value story per spec.md and is fully independent of US2.

1. Complete Phase 1 (Setup) + Phase 2 (Foundational) — shared identity-resolution helper in place
2. Complete Phase 3 (US1) — **MVP checkpoint**: employees can view their own salary summary
3. Complete Phase 4 (US2) — employees can also view their own advance history
4. Complete Phase 5 (Polish) — full quickstart run + contract diff + constitution review

### Incremental Delivery

Each phase checkpoint (end of Phase 3, Phase 4) is independently demoable: after Phase 3, employees can self-serve their salary summary; after Phase 4, they can also self-serve their advance history.

---

## Notes

- [P] tasks touch different files with no dependency on an incomplete task
- No automated tests are generated per project policy — `quickstart.md` is the verification mechanism (T015)
- T007 and T013 both edit `app/slices/employees/urls.py` — do them sequentially, not in parallel, even though neither carries a `[P]` marker
- Commit after each task or logical group; stop at either checkpoint to validate a story independently
