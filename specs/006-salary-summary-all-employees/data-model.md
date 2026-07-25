# Phase 1 Data Model: Salary Summary for All Employees

No new persistence models, fields, or migrations. This feature is a read-only report
composed entirely from existing `app/shared/db/models.py` entities:

- `Employee` (id, name, salary, start_date, active, user_id)
- `SalaryAdvance` (id, employee_id, amount, advance_date, note, created_at)
- `LatenessConfiguration` (singleton: enabled, expected_entrance_time, tolerance_minutes,
  deduction_interval_minutes, deduction_value, utc_offset_minutes)
- `JourneyRegistry` (id, user_id, timestamp, is_deleted)

## Response view: Salary Summary Item

Not a persisted entity — the per-employee shape returned in the report's `items` list.

| Field | Type | Source |
|---|---|---|
| `employee_id` | UUID | `Employee.id` |
| `month` | int | resolved request param (defaults to current month) |
| `year` | int | resolved request param (defaults to current year) |
| `gross_salary` | Decimal | `Employee.salary` |
| `advances_total` | Decimal | sum of `advances` (below); MUST equal that sum (spec FR-006) |
| `advances` | list of Salary Advance Item | `SalaryAdvance` rows for this employee where `advance_date` falls in `[month/year start, next month start)` |
| `late_delay_minutes` | int | sum of per-day delay minutes beyond tolerance, from `JourneyRegistry` timestamps vs. `LatenessConfiguration` (unchanged calculation, existing `domain/rules.py`) |
| `late_days_count` | int | count of days where delay exceeds `tolerance_minutes` |
| `late_deduction_total` | Decimal | sum of per-day deductions (existing `calculate_deduction`) |
| `net_salary` | Decimal | `gross_salary - advances_total - late_deduction_total` |

Lateness fields are `0`/`0.00` when: the employee has no linked user, or the
`LatenessConfiguration` singleton is missing/disabled — same rule as the current
single-employee endpoint, unchanged.

## Response view: Salary Advance Item (nested)

| Field | Type | Source |
|---|---|---|
| `id` | UUID | `SalaryAdvance.id` |
| `amount` | Decimal | `SalaryAdvance.amount` |
| `advance_date` | date | `SalaryAdvance.advance_date` |
| `note` | string, nullable | `SalaryAdvance.note` |

`employee_id`/`created_at` are not needed on the nested item — the item already lives inside
its employee's entry, and `advance_date` (not `created_at`) is the field the month/year filter
is applied against.

## Relationships

```
Employee (1) ──── (0..n) SalaryAdvance      [existing FK: SalaryAdvance.employee]
Employee (0..1) ── (1) User ── (0..n) JourneyRegistry   [existing FKs, unchanged]
LatenessConfiguration (singleton, unscoped — applies to every employee)
```

No state transitions — this is a read-only report; nothing here is created, updated, or
deleted.
