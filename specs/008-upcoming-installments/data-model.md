# Data Model: Upcoming Loan Installments List

**No schema change.** No new table, no new column, no Aerich migration. This feature is a read-only projection over existing rows. See [research.md](./research.md) §9.

---

## Source entities (existing, unchanged)

### `LoanInstallment` — `app/shared/db/models.py`

The unit the list is built from. One row in, one row out.

| Field | Type | Used for |
|-------|------|----------|
| `id` | UUID (pk) | → `installment_id` |
| `loan` | FK → `Loan` (`related_name="installments"`) | → `loan_id`, and the hop to the partner |
| `installment_number` | int | → `installment_number`, secondary sort key |
| `amount` | Decimal(10,2) | → `amount`; base for `remaining_amount` |
| `due_date` | date | selection bound, primary sort key, `is_overdue` input |
| `payment_date` | date, nullable | **not exposed** — see note below |
| `status` | `LoanInstallmentStatus` | selection filter (`!= PAID`) and → `status` |

`payment_date` is deliberately omitted from the response: it is only set when an installment is fully settled, and every fully settled installment is filtered out. It would be `null` on every row.

### `LoanInstallmentPayment` — `related_name="payments"`

| Field | Type | Used for |
|-------|------|----------|
| `amount` | Decimal(10,2) | summed, then capped → `paid_amount` |

Several rows may exist per installment. `payment_date` and `notes` are not needed here — `GET /loan-installments/{id}/payments` already serves the per-installment payment history.

### `Loan` — `related_name="installments"`

| Field | Type | Used for |
|-------|------|----------|
| `id` | UUID (pk) | → `loan_id`, tertiary sort key |
| `partner` | FK → `Partner` | → `partner_id`, `partner_name` |
| `status` | `LoanStatus` | exclusion filter (`CANCELED` dropped) |

`principal_amount` / `total_amount` are **not** read. Unlike `period_summary`, this feature reports no capital/profit split, so no interest ratio is derived and none of that slice's rounding machinery applies.

### `Partner`

| Field | Type | Used for |
|-------|------|----------|
| `id` | UUID (pk) | → `partner_id`, optional filter |
| `name` | CharField(255) | → `partner_name` |

`active` is not filtered on: an inactive partner still owes what it owes. Consistent with `period_summary`.

---

## Selection rule

An installment appears in the result when **all** of the following hold:

1. Its loan's status is not `CANCELED`.
2. Its own status is not `PAID`. (Both `PENDING` and `PARTIALLY_PAID` qualify — see [research.md](./research.md) §3 for why status, and not the payments sum, is authoritative.)
3. `due_date <= end_date`.
4. **Either** `due_date >= start_date`, **or** `include_overdue` is true (in which case there is no lower bound at all — the window reaches back over the entire loan history).
5. If `partner_id` was supplied, the loan belongs to that partner.

Then: order by `due_date` ascending, `loan_id`, `installment_number`; truncate to `limit` if supplied.

Both date bounds are inclusive. Ordering is applied before truncation, so `limit` yields the *earliest-due* N rows, and repeated identical requests return the same rows in the same order.

---

## Derived fields

Computed per row in the application/domain layer; none of these are persisted.

| Field | Derivation |
|-------|-----------|
| `paid_amount` | `min(Σ payments[].amount, installment.amount)` |
| `remaining_amount` | `installment.amount - paid_amount` |
| `is_overdue` | `installment.due_date < date.today()` |

### The cap on `paid_amount`

`min(…, amount)` implements the overpayment edge case: `remaining_amount` can never be reported as negative. `register_payment` currently rejects a payment exceeding the remaining balance, so the cap should never bind in practice — it is defence against historical or directly-inserted data, and it keeps this slice's arithmetic identical to `period_summary`'s.

### Precision

`amount` and every payment `amount` are persisted as 2dp `Decimal`, so summing and subtracting them stays exact at 2dp — **no rounding step is needed or wanted anywhere in this feature**. This is simpler than `period_summary`, whose profit share is a full-precision ratio requiring a single deliberate `quantize`.

The one thing to carry over from 007: `Decimal` keeps its scale through serialization, so `Decimal("0")` renders as `0` while `Decimal("0.00")` renders as `"0.00"`. The `paid_amount` accumulator must be seeded `Decimal("0.00")`, or an installment with no payments yet — the common case on this endpoint — returns a bare `0` where every other money field shows two decimals.

### Invariants

Per row:

- `paid_amount + remaining_amount == amount`
- `paid_amount >= 0.00` and `remaining_amount >= 0.00`
- `remaining_amount > 0.00` for any data created through the API. `register_payment` rejects overpayment and flips status to `PAID` at exact settlement, so a row whose payments cover its amount is always excluded by the `PAID` filter. The one way to see `remaining_amount == 0.00` here is an installment whose payment rows were inserted directly into the database beyond its amount while its status stayed `PENDING` — the cap holds (never negative), but the row is still listed, because status is what decides settlement
- `status ∈ {PENDING, PARTIALLY_PAID}` — never `PAID`
- `paid_amount > 0.00` ⟺ `status == PARTIALLY_PAID`, for installments whose payments went through `register_payment`
- every money field carries two decimals, including zeros

Across the result:

- `due_date` is non-decreasing down the list
- each installment appears at most once
- with `include_overdue=false`, every `due_date` satisfies `start_date <= due_date <= end_date`
- with `include_overdue=true`, every row with `due_date < start_date` has `is_overdue == true`

---

## Relationship to `period_summary`

Both slices select from the same window and share the `min(Σ payments, amount)` cap, but they answer different questions and their selection rules differ in one respect:

| | `period_summary` | this feature |
|---|---|---|
| Fully `PAID` installments | included (they land in `received_amount`) | excluded |
| Output | totals + per-partner rollup | one row per installment |
| Reaches before `start_date` | never | when `include_overdue=true` |

So `Σ remaining_amount` over this endpoint's rows equals `period_summary`'s `outstanding_amount` for the same window when `include_overdue=false` — with the one documented exception where an installment was force-marked `PAID` through `PATCH /loan-installments/{id}/pay` without any payment row, which this endpoint treats as settled and the summary still counts as outstanding ([research.md](./research.md) §3).

---

## Enums (existing, unchanged)

- `LoanInstallmentStatus`: `PENDING`, `PARTIALLY_PAID`, `PAID` — only the first two ever appear in a response row.
- `LoanStatus`: `CANCELED` is the only value this feature reads, as an exclusion.

No enum changes, so `specs/api/shared.md` needs no update.
