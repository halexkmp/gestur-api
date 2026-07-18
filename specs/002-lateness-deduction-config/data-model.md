# Phase 1 Data Model: HR Lateness Tolerance & Salary Deduction Configuration

## Entity: `LatenessConfiguration`

Singleton table — exactly one row is expected to exist at any time (application-enforced, see `research.md`).

| Field | Type | Constraints / Default | Notes |
|---|---|---|---|
| `id` | UUID (pk) | `default=uuid4` | Standard PK per Principle V. |
| `enabled` | bool | `default=False` | Disabled by default, per user instruction. |
| `expected_entrance_time` | Time | required, no app-level default (migration seed uses `CURRENT_TIME`) | Time-of-day only; applies uniformly every day (spec assumption). |
| `tolerance_minutes` | int | `default=0`, must be `>= 0` | Grace period in minutes before a check-in counts as late (FR-005). |
| `deduction_interval_minutes` | int | `default=0`, must be `> 0` **on write via the update endpoint** | Block size in minutes for deduction stepping (FR-008). The seeded default row may legitimately hold `0` since it starts `enabled=False` and was inserted outside the validated update path — see Validation Rules below. |
| `deduction_value` | Decimal(10,2) | `default=0`, must be `>= 0` | Monetary amount deducted per full interval reached (FR-008). |
| `created_at` | Datetime | `auto_now_add=True` | Principle V. |
| `updated_at` | Datetime | `auto_now=True` | Principle V (mutable entity). |

### Validation Rules (enforced in `UpdateLatenessConfiguration.execute`, FR-004)

- `tolerance_minutes < 0` → reject.
- `deduction_interval_minutes <= 0` → reject.
- `deduction_value < 0` → reject.
- `expected_entrance_time` is always required on update (full-replace semantics, no partial patch — see `research.md`).

### Runtime Guard (defense-in-depth, not a stored constraint)

`get_salary_summary`'s deduction calculation must treat `deduction_interval_minutes <= 0` as "zero deduction" (never divide by zero), even though the update endpoint blocks writing that value. This covers the bootstrapped seed row (`0`, `enabled=False`) and any pre-existing row from before validation existed.

### Absence Handling (FR-014)

If no `LatenessConfiguration` row exists at all (e.g., a fresh dev DB using `GENERATE_SCHEMAS` instead of Aerich — see `research.md`), the read path (`GetLatenessConfigurationRepository`) returns an in-memory equivalent of the disabled/zero defaults above rather than raising or creating a row. Only the update endpoint actually persists a row (creating it on first write if none exists).

---

## Value Object (not persisted): Daily Delay

Computed per employee, per calendar day, per salary-summary request. Lives entirely in `get_salary_summary/domain/rules.py` and the use case's in-memory aggregation — never stored.

| Field | Type | Derivation |
|---|---|---|
| `day` | date | Calendar day within the requested month that has at least one non-deleted `JourneyRegistry` row for the employee's linked user. |
| `entrance_at` | datetime | `MIN(timestamp)` of that day's `JourneyRegistry` rows. |
| `delay_minutes` | int | `max(0, minutes between entrance_at.time() and config.expected_entrance_time)`. `0` if `entrance_at` is at/before the expected time. |
| `is_late` | bool | `delay_minutes > config.tolerance_minutes`. |
| `deduction` | Decimal | `0` if not `is_late`; otherwise `floor(delay_minutes / config.deduction_interval_minutes) * config.deduction_value` (with the zero-interval guard above). |

Days with **no** `JourneyRegistry` row (absence) are simply absent from this list — not evaluated, per spec Edge Cases.

---

## Entity: `SalarySummary` (existing, extended — not a DB table, a response shape)

Produced by `GetSalarySummary.execute`, unchanged persistence source (`Employee`, `SalaryAdvance`) plus the new `LatenessConfiguration` + `JourneyRegistry` reads.

| Field | Type | Change |
|---|---|---|
| `employee_id` | UUID | unchanged |
| `month` | int | unchanged |
| `year` | int | unchanged |
| `gross_salary` | Decimal | unchanged |
| `advances_total` | Decimal | unchanged |
| `late_delay_minutes` | int | **new** — sum of `delay_minutes` across days where `is_late` is true. `0` when config disabled or absent. |
| `late_days_count` | int | **new** — count of days where `is_late` is true. `0` when config disabled or absent. |
| `late_deduction_total` | Decimal | **new** — sum of `deduction` across late days. `0` when config disabled or absent. |
| `net_salary` | Decimal | **changed formula** — `gross_salary - advances_total - late_deduction_total` (was `gross_salary - advances_total`). When the configuration is disabled or absent, `late_deduction_total` is `0`, so the formula is numerically unchanged from today's behavior. |

No floor is applied to `net_salary` (can go negative), consistent with existing behavior where `advances_total` is already uncapped.

---

## Relationships

```text
LatenessConfiguration        (no FK — standalone singleton)

Employee 1───0..1 User 1───* JourneyRegistry   (existing relationships, unchanged)
                             (used read-only to derive Daily Delay per month)
```

No schema changes to `Employee`, `User`, or `JourneyRegistry`.
