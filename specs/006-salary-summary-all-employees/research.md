# Phase 0 Research: Salary Summary for All Employees

No `NEEDS CLARIFICATION` markers remain in the Technical Context — the stack is fixed by the
constitution and a directly analogous bulk endpoint (`get_employees_schedule_overview`)
already exists in this codebase to model the approach on. The decisions below record the
choices made from that precedent rather than open-ended research.

## Decision 1: Response envelope shape

**Decision**: Wrap the list in `items: List[SalarySummaryItem]`, matching
`EmployeeScheduleOverviewResponse.items`.

**Rationale**: `get_employees_schedule_overview` already established this shape for a
company-wide report keyed by employee. Reusing it keeps the two "bulk employee report"
endpoints consistent for the frontend, satisfying the constitution's Consistency Over
Cleverness principle.

**Alternatives considered**: A bare JSON array as the top-level response — rejected because
it breaks from the existing bulk-endpoint convention and makes future top-level metadata
(e.g., a total count) harder to add without a breaking change.

## Decision 2: Bulk data-fetch strategy (avoid N+1)

**Decision**: Add bulk repository methods that return dict-by-id maps — all employees, one
query for lateness config, salary advances keyed by `employee_id`, and journey timestamps
keyed by `user_id` — then compute each employee's summary in Python from those maps, exactly
as `get_employees_schedule_overview/infra/repository.py` does with
`get_schedules`/`get_justified_absence_dates_bulk`/`get_present_dates_bulk`.

**Rationale**: The current single-employee repository (`GetSalarySummaryRepository`) issues
one query per employee (`get_employee_and_month_advances`, `get_journey_timestamps`). Calling
that once per employee in a loop would reintroduce the N+1 pattern the sibling bulk endpoint
was already written to avoid.

**Alternatives considered**: Keep the existing per-employee repository methods and call them
in a loop — rejected: works correctly but scales linearly in query count with employee count,
which is exactly the inefficiency the analogous `schedule-overview` endpoint was built to
avoid at the same employee scale (spec SC-002: 100 employees in one call).

## Decision 3: Replace vs. add alongside

**Decision**: Modify the existing `GET /employees/salary-summary/{employee_id}` endpoint in
place to become `GET /employees/salary-summary?month&year`; do not keep the old
employee-scoped path.

**Rationale**: The user's request is explicit — "change the salary summary endpoint ... not
the employee anymore" — describing a replacement, not an addition. This matches how the spec
frames User Story 1 (replacing the per-employee lookup) rather than introducing a second,
parallel endpoint.

**Alternatives considered**: Add a new `schedule-overview`-style endpoint at a different path
(e.g. `/salary-summary-overview`) and leave the old one intact — rejected: contradicts the
explicit instruction to *change* the endpoint, and would leave two salary-summary endpoints
with confusingly similar purposes for the frontend to choose between.

## Decision 4: Where the itemized-advances schema lives

**Decision**: Define a slice-local `SalaryAdvanceItem` Pydantic model inside
`get_salary_summary/ui/schemas.py`, structurally similar to (but not imported from)
`list_salary_advances/ui/schemas.py`'s `SalaryAdvanceItem`.

**Rationale**: `CLAUDE.md`/constitution: "Pydantic schemas ... HTTP-only, never reused
elsewhere" — each slice owns its schemas. Importing another slice's `ui/schemas.py` would
create a cross-slice UI-layer dependency, which the architecture forbids.

**Alternatives considered**: Import `SalaryAdvanceItem` from `list_salary_advances.ui.schemas`
— rejected as a direct violation of the VSA schema-ownership rule.

## Decision 5: Remove the pre-existing `get_my_salary_summary` → `get_salary_summary` schema import

**Decision**: `get_my_salary_summary/ui/schemas.py` currently does
`from app.slices.employees.get_salary_summary.ui.schemas import SalarySummaryResponse` and
re-exports it as its own response model. This feature removes that import: `get_my_salary_summary`
gets its own local `SalarySummaryResponse` class (same 9 fields, same name, so its route and
external contract are unchanged), and `get_salary_summary/ui/schemas.py` drops the now-unused
original class once nothing outside the slice references it.

**Rationale**: Identified during `/speckit-analyze` (finding C1) as a direct violation of
`CLAUDE.md`'s schema-ownership rule, and as an inconsistency within this feature's own design:
Decision 4 above rejects an equivalent cross-slice import for `SalaryAdvanceItem` on this exact
principle, while the original plan left this pre-existing one in place. User confirmed:
"cross slice import should gone. each slice should have its own schema." Fixing it is a small,
behavior-preserving, one-time cleanup, not a new feature — it does not change
`get_my_salary_summary`'s route, fields, or behavior.

**Alternatives considered**: Leave the import in place and only add new classes to
`get_salary_summary/ui/schemas.py` alongside it (the original plan) — rejected per explicit
user direction, and because it would have left `get_salary_summary/ui/schemas.py` carrying a
class it itself no longer uses, kept alive only for another slice's benefit.
