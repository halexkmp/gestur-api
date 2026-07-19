# Data Model: Employee Self-Service Salary Access

No new persistence models or migrations. This feature only adds a new access path onto data already modeled for spec 001 (`User`/`Employee` link) and spec 002 (`LatenessConfiguration`, salary/lateness calculation).

## Reused persistence entities (unchanged)

- **`User`** (`app/shared/db/models.py`) — unchanged. `current_user.employee` (reverse one-to-one, `related_name="employee"` on `Employee.user`) is the identity-resolution path this feature depends on.
- **`Employee`** (`app/shared/db/models.py`) — unchanged. Supplies `id`, `salary` for the calling user.
- **`SalaryAdvance`** (`app/shared/db/models.py`) — unchanged. Filtered by the resolved `employee_id`, queried by the new `ListMyAdvancesRepository` (its own class — see `plan.md`/`research.md` Decision 1).
- **`LatenessConfiguration`** (`app/shared/db/models.py`, added in spec 002) — unchanged. Read by the new `GetMySalarySummaryRepository` (its own class, not the HR-facing `GetSalarySummaryRepository`).

## New view models (HTTP response contracts only — `ui/schemas.py`, not persisted)

Both response models below are **imported** from the existing HR-facing slices, not redefined — see `research.md` Decision 4 (cross-slice `ui/schemas.py` reuse is an established, distinct pattern from the use-case/repository rule in Decision 1).

### `SalarySummaryResponse` (defined in `get_salary_summary/ui/schemas.py`, imported by `get_my_salary_summary/ui/schemas.py`)

Populated from the new `GetMySalarySummary.execute(...)` return value (own use case, reusing the pure functions in `get_salary_summary/domain/rules.py`):

| Field | Type | Notes |
|---|---|---|
| `employee_id` | UUID | Always equals the caller's own linked `Employee.id`, never a request input |
| `month` | int | Defaults to current month when not supplied |
| `year` | int | Defaults to current year when not supplied |
| `gross_salary` | Decimal | `Employee.salary` |
| `advances_total` | Decimal | Sum of the caller's `SalaryAdvance` rows for the month |
| `late_delay_minutes` | int | Total delay minutes across late days (0 if config disabled/absent) |
| `late_days_count` | int | Count of late days (0 if config disabled/absent) |
| `late_deduction_total` | Decimal | Total lateness deduction (0 if config disabled/absent) |
| `net_salary` | Decimal | `gross_salary - advances_total - late_deduction_total` |

### `SalaryAdvanceItem` (defined in `list_salary_advances/ui/schemas.py`, imported by `list_my_salary_advances/ui/schemas.py`)

Populated from the new `ListMyAdvances.execute(...)` return value (own use case/repository), one per advance row belonging to the caller:

| Field | Type | Notes |
|---|---|---|
| `id` | UUID | Advance record id |
| `amount` | Decimal | Advance amount |
| `employee_id` | UUID | Always equals the caller's own linked `Employee.id` |
| `created_at` | datetime | |
| `note` | Optional[str] | |
| `advance_date` | date | |

## Identity resolution (not persisted — request-time only)

For both endpoints: `employee_id := current_user.employee.id`, where `current_user.employee` comes from the already-eager-loaded relation on the JWT-resolved `User`. If `current_user.employee is None`, the request is rejected (403) before either new use case is invoked — no query is made with a null/placeholder employee id.
