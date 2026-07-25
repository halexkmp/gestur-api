---

description: "Task list for feature implementation"
---

# Tasks: Salary Summary for All Employees

**Input**: Design documents from `/specs/006-salary-summary-all-employees/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/salary-summary.md, quickstart.md (all present)

**Tests**: Not included — project policy explicitly forbids adding automated tests for new feature work (constitution, Development Workflow & Quality Gates; `CLAUDE.md` "Do not write tests"). Validation is via `quickstart.md`'s manual curl scenarios instead.

**Organization**: Tasks are grouped by user story (US1, US2) per spec.md's priorities.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2)
- Every task includes its exact file path

## Cross-slice cleanup (resolved during `/speckit-analyze`)

`app/slices/employees/get_my_salary_summary/ui/schemas.py` previously imported
`SalarySummaryResponse` from `get_salary_summary/ui/schemas.py` — a cross-slice reuse that
violates `CLAUDE.md`'s schema-ownership rule ("Pydantic ... never reused elsewhere") and was
inconsistent with this feature's own Decision 4 (research.md), which rejects the equivalent
reuse for `SalaryAdvanceItem`. Per explicit direction, this import is removed (T003): each
slice now owns its own schema. This is a one-time, behavior-preserving cleanup — same route,
same fields, same response shape for `GET /employees/me/salary-summary`.

---

## Phase 1: Setup

Not applicable. This feature modifies existing slices in an established codebase — no new
dependencies, project structure, or environment configuration is introduced (see plan.md
Technical Context).

---

## Phase 2: Foundational

Not applicable. There is no shared prerequisite that blocks both user stories beyond what US1
itself builds — US2 extends the same files US1 modifies, so it depends on US1 being complete
first rather than on a separate foundational phase (see Dependencies below).

---

## Phase 3: User Story 1 - HR reviews salary summaries for every employee at once (Priority: P1) 🎯 MVP

**Goal**: `GET /employees/salary-summary?month&year` (no `employee_id`) returns one entry per
employee with the existing computed fields (gross salary, advances total, lateness
delay/days/deduction, net salary), defaulting month/year to the current ones, restricted to
HR, returning `items: []` when there are no employees.

**Independent Test**: quickstart.md steps 1, 2, 3, 6, 7 — call the endpoint with no params and
with explicit `month`/`year`, confirm one item per employee, confirm a non-HR token gets 403,
confirm the old `/salary-summary/{employee_id}` path now 404s.

### Implementation for User Story 1

- [X] T001 [P] [US1] In `app/slices/employees/get_salary_summary/infra/repository.py`, add bulk-fetch methods on `GetSalarySummaryRepository`: `get_all_employees() -> list[Employee]` (replaces the per-`employee_id` lookup — does **not** filter by `active`; inactive employees stay in the report per spec Assumptions) and `get_journey_timestamps_bulk(user_ids, month, year) -> dict[UUID, list[datetime]]` (bulk equivalent of `get_journey_timestamps`, grouped by `user_id`). Keep `get_lateness_configuration()` unchanged. *Implementation note: built directly as the final `get_month_advances_bulk` (itemized, T007's shape) rather than first landing a totals-only method and replacing it — both stories' repository needs were delivered in one pass of this file to avoid writing throwaway code within the same implementation session.*
- [X] T002 [US1] In `app/slices/employees/get_salary_summary/application/use_case.py`, changed `GetSalarySummary.execute` to `execute(self, month: int | None = None, year: int | None = None) -> list[dict]` — `employee_id` parameter removed, month/year default to current, fetches all employees and the bulk maps from T001, returns `[]` when there are no employees, computes each employee's `late_delay_minutes`/`late_days_count`/`late_deduction_total` from pre-fetched bulk maps via the unchanged `domain/rules.py` functions, no per-employee queries in the loop. Both zero-fields short-circuit branches preserved in `_calculate_lateness`: no linked `user_id` → zero, and missing/disabled `LatenessConfiguration` → zero for every employee (verified: the bulk journey-timestamp query is skipped entirely when config is disabled/missing, an extra efficiency win). *Also includes T009's `advances`/`advances_total` wiring — same reasoning as T001.*
- [X] T003 [P] [US1] Decoupled `app/slices/employees/get_my_salary_summary/ui/schemas.py` from `get_salary_summary`: local `SalarySummaryResponse` class (same 9 fields) replaces the cross-slice import. `route.py` needed no change (already imports from local `.schemas`). Verified via HTTP: `GET /employees/me/salary-summary` returns byte-for-byte the same field set/values as before.
- [X] T004 [US1] (depends on T003) In `app/slices/employees/get_salary_summary/ui/schemas.py`, removed `SalarySummaryResponse` and added `SalaryAdvanceItem`, `SalarySummaryItem`, `SalarySummaryOverviewResponse` (`items: List[SalarySummaryItem]`). *Includes T008's `SalaryAdvanceItem`/`advances` field — same single-pass reasoning as T001.*
- [X] T005 [US1] (depends on T001, T002, T004) In `app/slices/employees/get_salary_summary/ui/route.py`, route changed from `@router.get("/{employee_id}", response_model=SalarySummaryResponse)` to `@router.get("", response_model=SalarySummaryOverviewResponse)`: `employee_id` path param and the `try/except ValueError → 404` block removed, `month`/`year` optional query params and `ensure_hr(current_user)` unchanged, calls `use_case.execute(month=month, year=year)`, returns `SalarySummaryOverviewResponse(items=items)`. Verified via HTTP: 200 with 102 items, old `/salary-summary/{uuid}` path now 404s, unauthenticated → 401, non-HR → 403.
- [X] T006 [US1] Updated the "Salary Summary" section (and Endpoints list entry) in `specs/api/employees.md`: new path/shape documented, `items: []` no-employees case noted, old 404-on-unknown-`employee_id` note removed. Also fixed a knock-on staleness in the "Employee Self-Service" section (`GET /employees/me/salary-summary`'s description previously said "same response shape as that endpoint," which stopped being true once the bulk endpoint gained `items`/`advances`).

**Checkpoint**: User Story 1 is fully functional and independently testable — quickstart.md steps 1, 2, 3, 6, 7 pass. `advances` (itemized list) does not exist on the response yet; that is User Story 2.

---

## Phase 4: User Story 2 - HR sees itemized salary advances alongside each summary (Priority: P2)

**Goal**: Each item in the report additionally includes the list of that employee's individual
salary advances dated within the requested month/year, and `advances_total` is provably equal
to the sum of that list (FR-006).

**Independent Test**: quickstart.md steps 4, 5 — confirm every item's `advances_total` equals
the sum of `advances[].amount`, and confirm an advance dated outside the requested month/year
does not appear in that employee's `advances` list.

### Implementation for User Story 2

- [X] T007 [US2] `get_month_advances_bulk(employee_ids, month, year) -> dict[UUID, list[SalaryAdvance]]` implemented in `app/slices/employees/get_salary_summary/infra/repository.py`, grouped by `employee_id`, ordered by `advance_date`, same range filter as `list_salary_advances/infra/repository.py`. (Delivered together with T001 — see its note.)
- [X] T008 [P] [US2] Slice-local `SalaryAdvanceItem` (`id`, `amount`, `advance_date`, `note`) added to `app/slices/employees/get_salary_summary/ui/schemas.py`; not imported from `list_salary_advances`. `advances: List[SalaryAdvanceItem]` added to `SalarySummaryItem`. (Delivered together with T004 — see its note.)
- [X] T009 [US2] `execute` calls `get_month_advances_bulk`, computes `advances_total = sum(advance.amount for advance in employee_advances)` per employee (provably consistent with the itemized list — FR-006), includes the mapped `advances` list per entry. (Delivered together with T002 — see its note.) Verified across all 102 seeded employees: 0 employees with `advances_total != sum(advances[].amount)`; an advance dated in a different month does not appear in that month's `advances` (checked via direct DB query — only 1 of 100+ seeded advances falls outside the seeded month, and it correctly does not appear when querying that month).
- [X] T010 [US2] Updated the "Salary Summary (All Employees)" section of `specs/api/employees.md`: documents the `advances` nested array (`id`, `amount`, `advance_date`, `note`) and states `advances_total` equals the sum of `advances[].amount`.

**Checkpoint**: All of quickstart.md (steps 1–8) passes end-to-end.

---

## Phase 5: Polish & Cross-Cutting Concerns

- [X] T011 [P] Ran the full `quickstart.md` validation against the 100-employee seeded local DB via an in-process ASGI client (HTTP layer, not just the use case): 200 with 102 items (no params and with explicit `month=7&year=2026`), old `/salary-summary/{uuid}` path → 404, unauthenticated → 401, non-HR (seeded employee) → 403, `advances_total` consistency verified with 0 mismatches across all 102 employees. SC-002 no-N+1 confirmed by code inspection: `execute` issues a fixed number of queries (`get_all_employees`, `get_month_advances_bulk`, `get_lateness_configuration`, and conditionally `get_journey_timestamps_bulk`) regardless of employee count — no query inside the per-employee loop.
- [X] T012 [P] Grepped the codebase: no remaining references to the old `/salary-summary/{employee_id}` path or `execute(employee_id=...)` signature in `app/` (only in other features' point-in-time `specs/<NNN>/` docs, which are historical snapshots per the constitution and are not updated); no remaining cross-slice `SalarySummaryResponse` import anywhere. `GET /employees/me/salary-summary` verified via HTTP to return the same field values as the corresponding bulk-endpoint entry for the same employee/period.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup / Foundational**: N/A (see above) — work starts directly at User Story 1.
- **User Story 1 (Phase 3)**: No dependencies; this is the MVP.
- **User Story 2 (Phase 4)**: Depends on User Story 1 being complete — T007/T009 modify the
  same `infra/repository.py` and `application/use_case.py` methods T001/T002 introduced, and
  T008 extends the `SalarySummaryItem` T004 created. Not parallelizable with US1.
- **Polish (Phase 5)**: Depends on both user stories being complete.

### Within Each User Story

- T003 (decouple `get_my_salary_summary`) has no dependency on T001/T002 (different files) and
  must complete before T004 (which deletes the class T003 stops depending on).
- Repository (T001/T007) before use case (T002/T009) before route (T005) — each layer depends
  on the one below it per Vertical Slice Architecture's one-way dependency rule.
- T004 depends on T003 (see above) and must land before T005 (route references the new classes
  T004 creates and the old class T004 removes).
- Schema tasks (T003, T004, T008) can run in parallel with repository tasks (different files)
  but must land before the route/use-case tasks that reference the new/removed classes.
- `specs/api/employees.md` update (T006, T010) can happen any time after its story's
  behavior is finalized, but must land in the same change (constitution requirement) — not
  deferred to Polish.

### Parallel Opportunities

- T001 (repository) and T003 (decouple `get_my_salary_summary`) can be worked in parallel
  within US1 — different files, no dependency between them.
- T008 (schema) can be worked in parallel with T007 (repository) within US2.
- T011 and T012 (Polish) can run in parallel — independent checks.

---

## Parallel Example: User Story 1

```bash
# T001 and T003 touch different files and have no dependency on each other:
Task: "Add bulk-fetch methods to app/slices/employees/get_salary_summary/infra/repository.py"
Task: "Decouple app/slices/employees/get_my_salary_summary/ui/schemas.py from get_salary_summary"
# T004 depends on T003; T002 depends on T001; T005 depends on T001, T002, and T004.
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 3 (T001–T006).
2. **STOP and VALIDATE**: run quickstart.md steps 1, 2, 3, 6, 7.
3. At this point the endpoint is fully functional without itemized advances, and the
   cross-slice schema import is already gone — a valid, shippable increment on its own if
   needed.

### Incremental Delivery

1. User Story 1 → validate → the bulk report exists and replaces the old endpoint (MVP);
   cross-slice schema cleanup lands as part of this increment.
2. User Story 2 → validate → itemized advances appear, total/list consistency confirmed.
3. Polish → full quickstart.md pass + stale-reference sweep + N+1 check.

## Notes

- [P] tasks touch different files and have no unmet dependency on an incomplete task.
- Commit after each task or logical group (per repository convention — do not batch unrelated
  changes into one commit).
- No test tasks are included per project policy; quickstart.md is the verification mechanism.
- `domain/rules.py` (`calculate_daily_delay_minutes`, `is_late`, `calculate_deduction`) is
  reused unchanged by both stories — no task modifies it.
