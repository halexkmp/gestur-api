# Phase 0 Research: HR Lateness Tolerance & Salary Deduction Configuration

No open `NEEDS CLARIFICATION` markers remained from `spec.md` — all scope-level ambiguity was resolved with the user during `/speckit-specify`. This phase resolves the remaining *technical* decisions needed to design the data model and contracts, including the defaults directive given at `/speckit-plan` time ("disabled by default, seeded via migration as a single record, numeric columns default 0, expected entrance time defaults to today").

## Decision: Singleton enforcement strategy

**Decision**: No DB-level uniqueness trick (e.g., a fixed/constant PK or a partial unique index). The repository always operates on "the first row by `created_at`" — `get` returns it (or an in-memory disabled/zero default if none exists), and `update` fetches-then-saves that same row, or creates it if none exists yet (upsert).

**Rationale**: The codebase has no existing singleton-table pattern to mirror, and introducing a DB constraint (e.g., `CHECK (id = '00000000-...')`) adds schema complexity for a problem the application layer already fully controls (only HR-facing endpoints ever write to this table, and there are only two of them). Matches Principle IV (Consistency Over Cleverness) — simplest mechanism that satisfies "unique for the entire system."

**Alternatives considered**:
- Fixed well-known UUID primary key, endpoints always `get_or_create` by that exact id. Rejected: adds a magic constant with no behavioral benefit over "first row," and would need special-casing if the seed migration ever needed re-running.
- A dedicated one-row-guarantee DB constraint (partial unique index on a constant expression). Rejected: unnecessary defensive engineering for a two-endpoint, HR-only write surface.

## Decision: Default row seeded via migration `INSERT`

**Decision**: After `aerich migrate` generates the schema-diff migration for the new `lateness_configuration` table, hand-append a single `INSERT` (with `ON CONFLICT DO NOTHING`, following existing precedent) that creates one disabled row with all numeric columns at `0` and `expected_entrance_time` set to the current time at migration-apply time (`CURRENT_TIME`, i.e. "today"/"now" — there is no meaningful zero-value default for a time-of-day column, so the current moment is used as a harmless placeholder since the row starts disabled anyway).

**Rationale**: Explicit user instruction. This repo already hand-appends seed `INSERT`s into Aerich-generated migrations twice (`migrations/models/8_20260206102320_update.py` and `12_20260617170624_update.py`, both seeding the `role` table with `ON CONFLICT (name) DO NOTHING`), so this is a repeated, established exception to "don't hand-edit migrations," not a novel one. It is flagged explicitly in `plan.md`'s Complexity Tracking.

**Alternatives considered**:
- Lazily create the row in application code on first `GET`/`PUT` (no migration `INSERT` at all). Rejected: contradicts the explicit instruction that the insert must live in the migration.
- Seed a full Aerich "data migration" via a separate custom migration-runner step outside the model migration. Rejected: over-engineered for one row; the existing role-seeding precedent already solves this inline.

**Consequence carried into data-model.md**: Because `GENERATE_SCHEMAS=True` in development (constitution: schema auto-generation, not Aerich, drives local dev schema), the seed row from the migration will **not** exist in a fresh local dev database unless `aerich upgrade` is run explicitly. The application must therefore still treat "no row exists" as "disabled, all zero" at the code level (already required by spec `FR-014`) — the migration seed is a production/staging convenience, not something the app is allowed to assume.

## Decision: `expected_entrance_time` field type

**Decision**: Tortoise `TimeField` (time-of-day only, no date component).

**Rationale**: Spec assumption states the expected entrance time applies uniformly every day (no per-weekday variation), so a bare time-of-day is sufficient and avoids modeling a spurious date. This also matches the "hour of entrance" phrasing from the original feature request.

**Alternatives considered**: `DatetimeField` — rejected, would imply a specific calendar date is meaningful, which it isn't.

## Decision: Delay/deduction computed at request time, not persisted

**Decision**: No new table for "daily delay" records. `GET /employees/salary-summary/{employee_id}` computes delay and deduction on the fly from existing `JourneyRegistry` rows for the employee's linked user, for the requested month, every time it's called.

**Rationale**: Matches how `advances_total` is already computed in `get_salary_summary` (summed live from `SalaryAdvance`, not cached), and matches the spec's explicit note that summaries always reflect current attendance/configuration data (no historical snapshotting). Keeps `JourneyRegistry` as the single source of truth for attendance.

**Alternatives considered**: A persisted `daily_delay` table populated by a background job. Rejected as unnecessary scope — no requirement calls for historical snapshotting or for delay data to be queryable outside the salary summary.

## Decision: Attendance grouping — earliest check-in per calendar day

**Decision**: For each day in the requested month, the employee's entrance time is the earliest (`MIN(timestamp)`) non-deleted `JourneyRegistry` row for that day, scoped to the employee's linked `user_id`. Employees with no linked `user_id` (nullable per existing `Employee.user` FK) produce zero delay days and zero deduction — there's no possible attendance data for them.

**Rationale**: Mirrors the existing day-boundary logic already used in `register_journey`'s `count_today_by_user` (UTC calendar-day boundaries via `datetime.combine(date, time.min/max)`), so delay calculation reuses the same notion of "day" the attendance system already uses. Consistent with spec assumption that only the earliest check-in of a day counts as the entrance.

**Alternatives considered**: Requiring a specific "check-in type" (e.g., first-of-day tagged explicitly). Rejected — `JourneyRegistry` has no type/kind field today and spec does not request adding one; earliest-timestamp-of-day is unambiguous given the existing 4-records/day cap.

## Decision: Deduction math lives in a pure `domain/rules.py`

**Decision**: Add `app/slices/employees/get_salary_summary/domain/rules.py` with pure functions `calculate_daily_delay_minutes(...)` and `calculate_lateness_deduction(...)` (no framework imports, no ORM access), invoked from the use case after the repository returns raw attendance timestamps + config values.

**Rationale**: VSA's optional `domain/` layer is exactly for this — business rules (tolerance gate, block-based deduction formula) don't belong in `infra/` (persistence only) or `ui/` (HTTP only), and keeping them in the use case directly would mix orchestration with a moderately complex formula that benefits from being independently readable.

**Alternatives considered**: Inline the math in the use case's `execute`. Rejected only because the formula (tolerance gate + floor-division blocks, applied per day, aggregated across a month) is non-trivial enough that a named pure function reads better than inline loops — this is a judgment call, not a hard requirement.

## Decision: Route placement and permission guard

**Decision**: `GET /employees/lateness-config` and `PUT /employees/lateness-config` registered in `app/slices/employees/urls.py` alongside the existing fixed-prefix routes (before the dynamic `/{employee_id}` route, same ordering rule already documented in that file). Both guarded by `ensure_hr`, matching every other endpoint in `specs/api/employees.md`.

**Rationale**: Consistency Over Cleverness — no existing "hr"-only context exists, and this feature exclusively augments `employees`' existing salary-related surface. Reusing `ensure_hr` matches spec `FR-013` ("consistent with existing access controls already protecting the existing salary summary endpoint").

**Alternatives considered**: New top-level `app/slices/hr/` context. Rejected — one settings resource plus one extended endpoint doesn't warrant a new context per CLAUDE.md's fixed context list, and would duplicate the `ensure_hr`-guarded-employees pattern for no benefit.
