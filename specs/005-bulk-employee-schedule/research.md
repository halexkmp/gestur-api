# Phase 0 Research: Bulk Employee Schedule & Attendance Verification

No `NEEDS CLARIFICATION` markers remain in the Technical Context — this feature reuses the
existing stack, existing models, and existing permission/domain logic verbatim. Research below
covers the two open questions that shaped the technical approach: how to avoid the N+1 pattern,
and how to keep the new endpoint's output identical to the two endpoints it consolidates.

## Decision: Batch the four data sources instead of looping per employee server-side

**Decision**: The new use case fetches, per call, at most: one query for the employee set
(all active employees, or `Employee.filter(id__in=employee_ids)`), one query for all matching
`EmployeeSchedule` rows (`employee_id__in=...`), one query for all `JustifiedAbsence` rows in
the month/year window across those employees, and one query for all `JourneyRegistry` rows in
the month/year window across the linked user IDs — then classifies each employee's days
in-memory using the existing `classify_attendance_days` pure function.

**Rationale**: The current degradation comes from the frontend calling
`GET /employees/schedule/{id}` and `GET /employees/attendance-verification/{id}?month&year`
once per employee (2×N round trips, each doing its own DB queries). Replacing that with 4
bulk queries total (regardless of N) is the direct fix and matches FR-011 ("must not scale
with employee count"). It also mirrors the existing single-employee repository's query shape
(`get_schedule`, `get_justified_absence_dates`, `get_present_dates`) — just parameterized over
a set of IDs instead of one ID, so the SQL pattern is unchanged, only its cardinality.

**Alternatives considered**:
- *Looping the existing per-employee use cases server-side in one endpoint*: rejected — it
  would remove the 2×N network round trips but keep the 2×N (or more) database round trips,
  which is the part actually degrading the server as the employee count grows.
- *A materialized/denormalized "overview" table refreshed on a schedule*: rejected — adds a new
  persistence model and a sync mechanism for a read-shape problem that plain bulk queries solve
  without new state, and the constitution's Data & Persistence Discipline principle discourages
  new models without a clear persistence need.

## Decision: Reuse `classify_attendance_days` unchanged; no new domain logic

**Decision**: The bulk use case imports and calls the existing
`app.slices.employees.get_attendance_verification.domain.rules.classify_attendance_days`
function once per employee (in-memory, no DB access inside the loop), rather than
reimplementing or forking the classification logic.

**Rationale**: FR-003 requires byte-for-byte parity with the existing per-employee attendance
verification endpoint. Reusing the same pure function guarantees identical classification
behavior (including edge cases: justified-absence-takes-priority, non-scheduled weekdays
excluded) without duplicating or drifting from it. This also satisfies the constitution's
Consistency Over Cleverness principle.

**Alternatives considered**:
- *Duplicate a bulk-oriented version of the classification logic*: rejected — duplicating pure,
  already-correct logic risks behavioral drift and violates Consistency Over Cleverness.

## Decision: Route shape — `GET /employees/schedule-overview` with optional `employee_ids`, `month`, `year`

**Decision**: New fixed-prefix route `GET /employees/schedule-overview`, registered in
`app/slices/employees/urls.py` alongside the other fixed-prefix routes (before the dynamic
`/{employee_id}` routes, per the existing ordering comment in that file). Query params:
`employee_ids: list[UUID] | None` (repeatable, e.g. `?employee_ids=a&employee_ids=b`), `month:
int | None`, `year: int | None` — mirroring the existing attendance-verification endpoint's
optional month/year with current-month/year default.

**Rationale**: Matches this codebase's existing convention for filterable list endpoints (e.g.
`GET /employees/salary-advances?employee_id=&month=&year=`) and avoids colliding with the
existing `/schedule/{employee_id}` and `/attendance-verification/{employee_id}` path-param
routes, which remain unchanged per FR-010.

**Alternatives considered**:
- *POST with a JSON body listing employee IDs*: rejected — this is a read operation with no
  side effects; every other filterable GET endpoint in this codebase uses query params, and a
  POST would break that consistency for no benefit (an empty/omitted ID list is a normal,
  supported case — "all employees" — not an unusually large payload requirement).
