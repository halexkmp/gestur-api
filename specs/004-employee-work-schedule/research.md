# Phase 0 Research: Employee Weekly Work Schedule & Attendance Verification

No items in the Technical Context were left as `NEEDS CLARIFICATION` — this is a backend-only
feature added to an existing, single-stack repository (FastAPI + Tortoise-ORM + Aerich +
PostgreSQL), so language, dependencies, storage, testing policy, target platform, and
project type are all fixed by existing convention rather than open questions. The
decisions below resolve the feature-specific design choices the spec's Assumptions section
left to implementation.

## Decision: Weekly schedule stored as 7 explicit boolean columns

**Decision**: `EmployeeSchedule` has one `BooleanField` per weekday
(`monday` … `sunday`), not a bitmask, CSV string, or JSON array.

**Rationale**: Matches constitution Principle V (favor DB constraints and typed columns
over application-only structures) and Principle II (no `dict`/generic containers crossing
layer boundaries — a JSON blob would force callers to parse/validate weekday keys by hand
in every layer). Explicit columns are directly queryable (e.g. a future report could filter
`WHERE saturday = true` without unpacking JSON) and mirror the existing style of
`LatenessConfiguration`, which also uses one column per discrete setting rather than a
config blob.

**Alternatives considered**:
- *Bitmask integer*: more compact, but opaque in the DB and not queryable per-day without
  bit-arithmetic in SQL; rejected as inconsistent with "Consistency Over Cleverness."
- *JSON field* (Tortoise `JSONField`, already used for `JourneyRegistry.original_data` as
  an audit snapshot, not as primary structured data): rejected because it would require
  ad hoc parsing/validation of weekday keys in the domain layer, which explicit typed
  columns avoid entirely.
- *Separate `WorkDay` child table (one row per weekday)*: more "normalized," but adds a
  join and a variable-cardinality collection for a fixed 7-value set with no independent
  lifecycle — rejected as needless complexity for a fixed-size, always-fully-populated set.

## Decision: One active schedule per employee via `OneToOneField`, upsert use case

**Decision**: `EmployeeSchedule.employee` is a `OneToOneField("models.Employee",
related_name="schedule")`. `set_employee_schedule` is a single upsert use case (create if
absent, replace in place if present) rather than separate `create_employee_schedule` /
`update_employee_schedule` slices.

**Rationale**: The spec (User Story 1, FR-001/FR-002) explicitly describes this as "set the
schedule" with create-or-replace semantics and no schedule history — there is exactly one
active schedule per employee at any time, which is precisely what `LatenessConfiguration`'s
get/upsert pair already models (there, `.order_by("created_at").first()` finds the singleton
row; here, `OneToOneField` gives the same one-row-per-employee guarantee at the DB level,
which is stronger since it's scoped per employee rather than global). Splitting into
separate create/update slices (as `Employee`, `SalaryAdvance` etc. do) would misrepresent
the entity — those are independently-lifecycled records with their own identity, whereas a
schedule has no meaning without exactly one row per employee.

**Alternatives considered**:
- *Separate create/update slices mirroring `create_employee`/`update_employee`*: rejected —
  those entities have independent identity and a delete lifecycle; a schedule does not (no
  "delete schedule" requirement exists in the spec), so a single upsert slice is simpler and
  matches actual usage.

## Decision: Justified absence uniqueness enforced at the DB layer

**Decision**: `JustifiedAbsence` has `unique_together = (("employee", "absence_date"),)` in
its `Meta`. The `create_justified_absence` use case still performs an application-level
existence check first (to return a clean `ValueError` → `400`, consistent with how
`update_lateness_config` and other use cases signal validation failures), with the DB
constraint as the authoritative backstop.

**Rationale**: Constitution Principle V explicitly favors DB constraints over
application-only validation for exactly this kind of invariant (FR-006: reject duplicate
justified absence for the same employee/date). The existing codebase has no established
pattern for translating a Tortoise `IntegrityError` into an HTTP response, so the
check-then-create pattern (already used throughout, e.g. `get_employee`'s
`ValueError` → `404 Not Found`) is reused for the primary path, keeping the DB constraint as
a safety net rather than the primary signaling mechanism — no new error-handling pattern is
introduced.

**Alternatives considered**:
- *Application-only check, no DB constraint*: rejected — violates Principle V's explicit
  preference for DB constraints on this kind of invariant.
- *Catch `IntegrityError` in the route and translate to 409*: rejected for this iteration —
  no existing slice in the repo does this, and introducing an application-level check
  first makes the DB-level constraint a backstop rather than the primary code path used on
  every request, avoiding a new error-translation pattern.

## Decision: Justified absence restricted to scheduled work days (FR-005) is a use-case-level check

**Decision**: `create_justified_absence`'s use case loads the employee's current
`EmployeeSchedule` and checks the weekday of `absence_date` against the corresponding
boolean column before creating; raises `ValueError` if the day isn't a scheduled work day
(or no schedule exists at all) — the route translates this to `400 Bad Request`.

**Rationale**: This is a cross-entity business rule (justified absence validity depends on
the *schedule* entity), which per Principle I belongs in `application/` (or `domain/`), not
in the repository. It cannot be a DB constraint since it depends on another table's data.

## Decision: Attendance verification is computed on demand, not persisted

**Decision**: `get_attendance_verification` has no backing table. Its use case fetches (a)
the employee's `EmployeeSchedule`, (b) `JustifiedAbsence` rows for the employee/period, and
(c) `JourneyRegistry` presence per day for the employee's linked user — the same
`user_id` + `timestamp__gte`/`timestamp__lt` month-range filter pattern already used by
`get_salary_summary.infra.repository.get_journey_timestamps` — then classifies each
scheduled work day in `domain/rules.py` (pure function, no framework imports).

**Rationale**: The spec's Key Entities section explicitly calls the verification result
"derived (computed on demand, not separately stored)." Reusing the exact filter pattern
(`JourneyRegistry.filter(user_id=..., is_deleted=False, timestamp__gte=..., timestamp__lt=...)`)
that `get_salary_summary` and `admin_list_journeys` already use keeps the query idiomatic
and avoids inventing a new way to ask "did this user have a journey register on this day."
Only presence-per-day is needed here (unlike `get_salary_summary`, which also needs the
*earliest* timestamp per day for lateness math) — so the repository method returns a
`set[date]` of days with at least one non-deleted `JourneyRegistry` row, rather than raw
timestamps.

**Alternatives considered**:
- *Persist a materialized attendance record per day*: rejected — the spec explicitly scopes
  this as a computed report, and persisting it would require a background job or
  invalidation logic when journeys/absences change after the fact, which is unrequested
  scope.

## Decision: New shared `ensure_hr_or_admin` permission guard

**Decision**: Add `ensure_hr_or_admin(current_user)` to `app/shared/security/permissions.py`,
raising `403 Forbidden` unless the caller has the `HUMAN_RESOURCES` or `ADMIN` role. All six
HR-facing management/reporting endpoints in this feature (schedule get/set, justified
absence create/list/delete, attendance verification) use this guard instead of `ensure_hr`.
The self-service `GET /employees/me/schedule` endpoint is unaffected — it continues to use
`resolve_own_employee_id`/`ensure_employee`.

**Rationale**: Confirmed with the user that FR-013's "HR/Admin" wording is literal — both
`HUMAN_RESOURCES` and `ADMIN` roles must have access, not `HUMAN_RESOURCES` alone. No
existing guard in `permissions.py` combines two roles (`ensure_hr`, `ensure_employee`, and
`ensure_admin` each check exactly one), and every existing `employees`-context endpoint
(`create_employee`, `create_salary_advance`, `update_lateness_config`, etc.) is `ensure_hr`-
only — so this is new ground, not a case where an existing pattern was available to copy
outright. The closest-fitting existing style is `ensure_admin`/`ensure_hr` themselves (a
short function in `app/shared/security/permissions.py` that inspects
`current_user.roles` and raises `HTTPException(403, ...)`); `ensure_hr_or_admin` is written
in that exact shape, just checking membership in a two-role tuple instead of one role.
`app/shared/security/` is explicitly the stable, cross-cutting home for this kind of guard
per CLAUDE.md, so adding one more small function there (not touching the three existing
ones) stays within Principle I's boundaries for `app/shared/`.

**Alternatives considered**:
- *Call `ensure_hr(current_user)` and catch, then fall back to `ensure_admin(current_user)`
  in every route*: rejected — duplicates the same two-line try/except six times across
  routes instead of once in `permissions.py`, and is harder to read than a single guard
  call, violating Principle IV's preference for the simplest consistent shape.
- *Add an `allowed_roles: list[UserRole]` parameter to a generalized `ensure_role(...)`
  helper*: rejected — would require changing the call sites of the three existing guards
  (or leaving them as inconsistent dead code next to a new generic one) for a benefit this
  feature doesn't need; out of scope per "Don't Be Smart" (CLAUDE.md) and Principle IV.

## Decision: No new enum required

**Decision**: `app/shared/db/enums.py` is not modified. The attendance day classification
(`PRESENT` / `JUSTIFIED_ABSENCE` / `UNJUSTIFIED_ABSENCE`) is a response-shape concern
expressed as a `Literal`/string in the `ui/schemas.py` response model and mirrored as plain
string return values from the pure domain function — it is not stored on any model, so it
does not need a `CharEnumField`-backed shared enum the way `UserRole`/`SaleStatus`/etc. do
for persisted columns.

**Rationale**: Existing shared enums all back a persisted `CharEnumField` column. Since
this status is never written to a column (only ever computed and returned), adding it to
the shared enum module would be scope creep with no corresponding persistence need.
