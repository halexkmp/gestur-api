# Late Penalty in Hours — Design

**Date:** 2026-11-23
**Size:** small change
**Related:** `specs/002-lateness-deduction-config/` (existing lateness deduction)

## Intent

Add a second, additional penalty for late arrivals: every day an employee arrives after
the expected entrance time plus the tolerance, they lose a fixed number of **hours** of pay.
HR configures the number of hours in the lateness configuration. The penalty is discounted
from the salary on top of the existing per-interval money deduction, which stays unchanged.

## Goals

- New config parameter `late_penalty_hours` (hours per late day, decimals allowed).
- New config parameter `monthly_work_hours` (default 220, CLT standard) used to derive the
  employee's hourly rate from their monthly salary.
- Salary summaries show the penalty as its own figure and subtract it from net salary.

## Non-goals

- No change to the existing deduction (`deduction_interval_minutes` × `deduction_value`).
- No per-employee hourly rate or workload; one system-wide `monthly_work_hours`.
- No penalty scaling by how late the employee was — it is flat per late day.
- No change to `get_attendance_verification` (it computes no money).
- Frontend work lives in the separate frontend project; this repo only updates `specs/api/`.

## Rules

- A "late day" is exactly the existing definition: earliest check-in of the local day,
  delay from `expected_entrance_time` greater than `tolerance_minutes`.
- `hourly_rate = employee.salary / monthly_work_hours`
- `late_penalty_total = hourly_rate × late_penalty_hours × late_days_count`,
  rounded to 2 decimals (ROUND_HALF_UP) — *builder's call*.
- `net_salary = gross_salary - advances_total - late_deduction_total - late_penalty_total`
- When the config is disabled or missing, `late_penalty_total = 0` (same `enabled` flag).
- `late_penalty_hours = 0` effectively turns only this penalty off.
- Not capped against gross salary (same as existing deductions).

## Changes

**Model** (`app/shared/db/models.py`, `LatenessConfiguration`):
- `late_penalty_hours = DecimalField(max_digits=5, decimal_places=2, default=0)`
- `monthly_work_hours = IntField(default=220)`
- Migration generated separately via `aerich migrate` (not hand-written).

**`PUT /employees/lateness-config`** (`update_lateness_config`): both fields **required**
(full replace, consistent with the existing contract — frontend and backend deploy together).
Validation: `0 <= late_penalty_hours < 1000` (column limit), `monthly_work_hours > 0`; violations rejected like
the existing field validations.

**`GET /employees/lateness-config`** (`get_lateness_config`): returns both fields; the
bootstrapped default (no config yet) returns `0` and `220`.

**Salary summaries** (`get_salary_summary`, `get_my_salary_summary`): one pure function
in `get_salary_summary/domain/rules.py`, which `get_my_salary_summary` already imports its
lateness rules from (not `app/shared/`), and responses gain `late_penalty_total` (Decimal). `net_salary`
subtracts it.

**Contract:** update `specs/api/employees.md` (config fields, validation, summary field,
net salary formula).

## Approaches considered

1. **Slice domain rule (chosen):** pure function in `get_salary_summary/domain/rules.py`,
   reused by `get_my_salary_summary` exactly as its existing lateness rules are.
2. **Shared helper in `app/shared/`:** less duplication, but CLAUDE.md forbids
   feature logic there.

Hourly-rate options considered: fixed 220 divisor (hardcoded), **config field with default
220 (chosen)**, per-employee hours/rate (more accurate, but touches Employee CRUD).

## Left to the builder

- Exact rounding placement (per-day vs. total) — total, ROUND_HALF_UP to 0.01, unless it
  conflicts with how existing totals are rounded.
- Error message wording for the new validations.
- No tests (project policy).
