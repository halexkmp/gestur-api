# Late Penalty in Hours Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a flat per-late-day penalty of `late_penalty_hours` hours of pay (hourly rate = `salary / monthly_work_hours`) to the lateness configuration and subtract it from net salary in both salary summaries, on top of the existing deduction.

**Architecture:** Two new columns on the singleton `LatenessConfiguration`, exposed through the existing get/update lateness-config slices. One new pure function in `get_salary_summary/domain/rules.py` (which `get_my_salary_summary` already imports its lateness rules from) computes the penalty; both salary-summary use cases call it and return `late_penalty_total`.

**Tech Stack:** FastAPI, Pydantic v2, Tortoise-ORM, Aerich, Python `decimal`.

**Spec:** `docs/superpowers/specs/2026-11-23-late-penalty-hours-design.md`

## Global Constraints

- **No test files.** Project policy (CLAUDE.md / constitution): do not create tests. Verification steps below use one-off `python -c` checks run in the shell, not committed tests.
- **No hand-written migrations.** Change the model only; the user runs `aerich migrate` / `aerich upgrade` separately.
- Use-case parameters are explicit and typed — no `dict` / `**kwargs` parameters.
- Existing deduction (`deduction_interval_minutes` × `deduction_value`) is unchanged.
- `late_penalty_hours`: Decimal, default `0`, valid range `0 <= x < 1000` (column is `max_digits=5, decimal_places=2`).
- `monthly_work_hours`: int, default `220`, must be `> 0`.
- Both new fields are **required** in `PUT /employees/lateness-config` (full replace).
- Same `enabled` flag gates the penalty; disabled / missing config / no linked user → `late_penalty_total = 0`.
- `late_penalty_total = round_half_up(salary / monthly_work_hours × late_penalty_hours × late_days_count, 0.01)`, rounded once on the total.
- `net_salary = gross_salary - advances_total - late_deduction_total - late_penalty_total`.
- `specs/api/employees.md` must be updated in the same change as the code.

## Review Focus

1. **Config disabled or never created** → `late_penalty_total` is `0`, `net_salary` unchanged vs. today. (Task 2 Step 2 check.)
2. **Bootstrapped/legacy row** (migration-seeded row, `monthly_work_hours` filled by column default 220, `late_penalty_hours` 0) → penalty `0`, no division error. (Task 2 Step 2 check with `monthly_work_hours=0` guard.)
3. **Non-round hourly rate** (e.g. salary 1000 / 220 h) → total rounded half-up to cents, not a long-tail decimal in JSON. (Task 2 Step 2.)
4. **Out-of-range PUT values** (`late_penalty_hours = -1` or `1000`, `monthly_work_hours = 0`) → `400`, not a DB error `500`. (Task 1 Step 3.)
5. **Employee with no linked user** → penalty `0` (no journeys to evaluate). Covered by the existing early return; implementer must return a 4-tuple there too.

---

### Task 1: Config fields (model + get/update lateness-config + contract)

**Files:**
- Modify: `app/shared/db/models.py` (`LatenessConfiguration`, ~line 216)
- Modify: `app/slices/employees/update_lateness_config/application/use_case.py`
- Modify: `app/slices/employees/update_lateness_config/infra/repository.py`
- Modify: `app/slices/employees/update_lateness_config/ui/schemas.py`
- Modify: `app/slices/employees/update_lateness_config/ui/route.py`
- Modify: `app/slices/employees/get_lateness_config/application/use_case.py`
- Modify: `app/slices/employees/get_lateness_config/ui/schemas.py`
- Modify: `specs/api/employees.md` ("Lateness Configuration" section)

**Interfaces:**
- Produces: `LatenessConfiguration.late_penalty_hours: Decimal`, `LatenessConfiguration.monthly_work_hours: int` (used by Task 2).
- Produces: `UpdateLatenessConfiguration.execute(enabled, expected_entrance_time, tolerance_minutes, deduction_interval_minutes, deduction_value, late_penalty_hours: Decimal, monthly_work_hours: int)`; repository `upsert(...)` gains the same two keyword params.

- [ ] **Step 1: Add model fields**

In `LatenessConfiguration`, after `deduction_value`:
`late_penalty_hours = fields.DecimalField(max_digits=5, decimal_places=2, default=0)` and
`monthly_work_hours = fields.IntField(default=220)`.

- [ ] **Step 2: Thread the fields through the update slice and the get slice**

- `UpdateLatenessConfigRequest` and both `LatenessConfigResponse` schemas: add `late_penalty_hours: Decimal` and `monthly_work_hours: int` (required, no defaults on the request).
- Update use case: add the two params; validate
  - `late_penalty_hours < 0 or late_penalty_hours >= 1000` → `ValueError("late_penalty_hours must be >= 0 and < 1000")`
  - `monthly_work_hours <= 0` → `ValueError("monthly_work_hours must be > 0")`
  then pass them to `upsert`.
- Repository `upsert`: accept both, set them on create and on update.
- Route: pass `data.late_penalty_hours`, `data.monthly_work_hours`.
- Get use case: `DEFAULT_CONFIG` gains `"late_penalty_hours": Decimal("0")`, `"monthly_work_hours": 220`; the populated branch returns `Decimal(config.late_penalty_hours)` and `config.monthly_work_hours`.

- [ ] **Step 3: Verify validation and imports**

Run:
```bash
python -c "
import asyncio
from datetime import time
from decimal import Decimal
from app.slices.employees.update_lateness_config.application.use_case import UpdateLatenessConfiguration
uc = UpdateLatenessConfiguration(None)
base = dict(enabled=True, expected_entrance_time=time(8), tolerance_minutes=5, deduction_interval_minutes=60, deduction_value=Decimal('1'))
for hours, mwh in [(Decimal('-1'), 220), (Decimal('1000'), 220), (Decimal('1'), 0)]:
    try:
        asyncio.run(uc.execute(**base, late_penalty_hours=hours, monthly_work_hours=mwh)); print('NO ERROR', hours, mwh)
    except ValueError as e:
        print('ok:', e)
import app.main
"
```
Expected: three `ok:` lines (two for `late_penalty_hours`, one for `monthly_work_hours`), no `NO ERROR`, and `import app.main` succeeds.

- [ ] **Step 4: Update contract**

In `specs/api/employees.md` "Lateness Configuration": add both fields to the field list with their constraints, change "all five fields are required" → "all seven fields", add the two new `400` conditions, note the no-row defaults (`late_penalty_hours: "0"`, `monthly_work_hours: 220`), and add a short "Late penalty" formula paragraph (flat per late day, `salary / monthly_work_hours × late_penalty_hours`, in addition to the deduction, same `enabled` flag).

- [ ] **Step 5: Commit**

```bash
git add app/shared/db/models.py app/slices/employees/update_lateness_config app/slices/employees/get_lateness_config specs/api/employees.md
git commit -m "add late penalty hours and monthly work hours to lateness config"
```

---

### Task 2: Penalty rule + salary summaries + contract

**Files:**
- Modify: `app/slices/employees/get_salary_summary/domain/rules.py`
- Modify: `app/slices/employees/get_salary_summary/application/use_case.py`
- Modify: `app/slices/employees/get_salary_summary/ui/schemas.py` (`SalarySummaryItem`)
- Modify: `app/slices/employees/get_my_salary_summary/application/use_case.py`
- Modify: `app/slices/employees/get_my_salary_summary/ui/schemas.py` (`SalarySummaryResponse`)
- Modify: `specs/api/employees.md` ("Salary Summary (All Employees)" and "GET /employees/me/salary-summary")

**Interfaces:**
- Consumes: `LatenessConfiguration.late_penalty_hours`, `.monthly_work_hours` (Task 1).
- Produces: `calculate_late_penalty(salary: Decimal, monthly_work_hours: int, late_penalty_hours: Decimal, late_days_count: int) -> Decimal` in `get_salary_summary/domain/rules.py`.

- [ ] **Step 1: Implement `calculate_late_penalty` in `get_salary_summary/domain/rules.py`**

Returns `Decimal("0")` when `monthly_work_hours <= 0` or `late_days_count <= 0`; otherwise `(salary / monthly_work_hours * late_penalty_hours * late_days_count).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.
Note: this deviates slightly from the design doc's "per-slice rules.py" — `get_my_salary_summary` already imports its lateness rules from `get_salary_summary/domain/rules.py`, so follow that existing pattern.

- [ ] **Step 2: Verify the rule**

Run:
```bash
python -c "
from decimal import Decimal as D
from app.slices.employees.get_salary_summary.domain.rules import calculate_late_penalty as f
print(f(D('2200'), 220, D('2'), 3))    # 60.00
print(f(D('1518'), 220, D('1.5'), 2))  # 20.70
print(f(D('1000'), 220, D('1'), 1))    # 4.55
print(f(D('1000'), 0, D('1'), 1))      # 0
print(f(D('1000'), 220, D('0'), 5))    # 0.00
print(f(D('1000'), 220, D('2'), 0))    # 0
"
```
Expected: `60.00`, `20.70`, `4.55`, `0`, `0.00`, `0`.

- [ ] **Step 3: Wire into both use cases and schemas**

- Both `_calculate_lateness` methods gain a `salary: Decimal` param and return a 4-tuple `(delay_minutes, late_days_count, deduction_total, penalty_total)`; every early return becomes `0, 0, Decimal("0"), Decimal("0")`. The penalty is computed once after the day loop with `calculate_late_penalty(salary, config.monthly_work_hours, Decimal(config.late_penalty_hours), late_days_count)`.
- Each result dict gains `"late_penalty_total"`; `net_salary` subtracts it as well.
- Add `late_penalty_total: Decimal` to `SalarySummaryItem` and `SalarySummaryResponse`, right after `late_deduction_total`.

- [ ] **Step 4: Verify the app imports and the routes expose the field**

Run:
```bash
python -c "
import app.main
from app.slices.employees.get_salary_summary.ui.schemas import SalarySummaryItem
from app.slices.employees.get_my_salary_summary.ui.schemas import SalarySummaryResponse
assert 'late_penalty_total' in SalarySummaryItem.model_fields
assert 'late_penalty_total' in SalarySummaryResponse.model_fields
print('ok')
"
```
Expected: `ok`.

- [ ] **Step 5: Update contract**

In `specs/api/employees.md`: add `late_penalty_total   # total late penalty (hours × hourly rate × late days) this month` to the bulk item shape; change the `net_salary` comment to `gross_salary - advances_total - late_deduction_total - late_penalty_total`; add `late_penalty_total` to the "`0`/`0.00` when disabled / never created / no linked user" bullet; add it to the field list of `GET /employees/me/salary-summary`.

- [ ] **Step 6: Commit**

```bash
git add app/slices/employees/get_salary_summary app/slices/employees/get_my_salary_summary specs/api/employees.md
git commit -m "subtract late penalty hours from salary summaries"
```

---

### Task 3: Contract audit

- [ ] **Step 1:** Invoke the `update-api-contract` skill for the `employees` context and fix any drift it reports between `app/slices/employees/` and `specs/api/employees.md`.
- [ ] **Step 2:** Commit any fixes (`git commit -m "sync employees api contract"`), or note that none were needed.
- [ ] **Step 3:** Remind the user to run `aerich migrate` (e.g. `--name add_late_penalty_hours`) and `aerich upgrade` — not done by the implementer.
