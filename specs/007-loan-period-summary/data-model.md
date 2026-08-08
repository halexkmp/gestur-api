# Phase 1 Data Model: Loan Period Summary

**No persistence change.** No new table, no new column, no new index, no Aerich migration. This feature is a read-only projection over entities that already exist in `app/shared/db/models.py`.

---

## Existing entities consumed

### `Loan` (table `loan`)

| Field | Used for |
|-------|----------|
| `id` | grouping / traceability |
| `partner` (FK → `Partner`) | grouping installments by partner |
| `principal_amount` (Decimal 10,2) | capital side of the profit split |
| `total_amount` (Decimal 10,2) | denominator of the interest-share ratio |
| `status` (`LoanStatus`) | `CANCELED` loans are excluded from the whole summary |

`interest_rate` is **not** used — the split is derived from the stored `principal_amount` / `total_amount` pair (see [research.md](./research.md) §3).

### `LoanInstallment` (table `loan_installment`)

| Field | Used for |
|-------|----------|
| `id` | payment allocation, counting |
| `loan` (FK → `Loan`) | reaching `principal_amount` / `total_amount` / `status` / `partner` |
| `amount` (Decimal 10,2) | the unit of expected revenue |
| `due_date` (Date) | **the range filter** — inclusive on both ends |
| `installment_number` | deterministic secondary ordering |

`status` is deliberately **not** used to compute received/outstanding — the actual payment rows are, so partially paid installments split correctly (US3 scenario 2).

### `LoanInstallmentPayment` (table `loan_installment_payment`)

| Field | Used for |
|-------|----------|
| `loan_installment` (FK) | allocation to the selected installment |
| `amount` (Decimal 10,2) | the received figure |

`payment_date` is **not** used as a filter — attribution follows the installment's `due_date`, per the spec's "Payment recorded outside the range" edge case.

### `Partner` (table `partner`)

| Field | Used for |
|-------|----------|
| `id`, `name` | identifying each entry in the partner list |

`active` is not filtered on — inactive partners with scheduled installments are still included (spec edge case).

---

## Derived (in-memory) model

These are transient DTOs in `application/use_case.py`, not persisted. They mirror the `@dataclass` style already used by `get_loan_summary/application/use_case.py`.

### `PartnerPeriodEntryDTO`

| Field | Type | Derivation |
|-------|------|------------|
| `partner_id` | `UUID` | `installment.loan.partner.id` |
| `partner_name` | `str` | `installment.loan.partner.name` |
| `scheduled_amount` | `Decimal` | Σ `installment.amount` for this partner in range |
| `received_amount` | `Decimal` | Σ `min(Σ payments, installment.amount)` for this partner |
| `outstanding_amount` | `Decimal` | `scheduled_amount − received_amount` |
| `installments_count` | `int` | count of this partner's selected installments (FR-015) |

### `LoanPeriodSummaryDTO`

| Field | Type | Derivation |
|-------|------|------------|
| `start_date` | `date` | echo of the request (FR-017) |
| `end_date` | `date` | echo of the request (FR-017) |
| `expected_revenue` | `Decimal` | Σ `installment.amount` over all selected installments |
| `expected_capital` | `Decimal` | `expected_revenue − expected_profit` |
| `expected_profit` | `Decimal` | Σ (full precision) `amount × (total_amount − principal_amount) / total_amount`, quantized once to 2dp |
| `received_amount` | `Decimal` | Σ per-installment capped receipts |
| `outstanding_amount` | `Decimal` | `expected_revenue − received_amount` |
| `installments_count` | `int` | number of selected installments |
| `partners_count` | `int` | number of entries in `partners` |
| `partners` | `list[PartnerPeriodEntryDTO]` | sorted by `scheduled_amount` desc, then `partner_name` asc (FR-016) |

---

## Selection rule

An installment is **selected** when all hold:

1. `start_date <= installment.due_date <= end_date`
2. `installment.loan.status != LoanStatus.CANCELED`

Nothing else filters. `LoanStatus.PAID` loans, `LoanInstallmentStatus` of any value, and inactive partners all remain in scope.

---

## Invariants the implementation must preserve

| # | Invariant | Enforced by |
|---|-----------|-------------|
| INV-1 | `expected_capital + expected_profit == expected_revenue` | capital derived by subtraction, never rounded separately |
| INV-2 | `received_amount + outstanding_amount == expected_revenue` | outstanding derived by subtraction |
| INV-3 | `Σ partners[].scheduled_amount == expected_revenue` | both sum the same 2dp installment amounts |
| INV-4 | `Σ partners[].received_amount == received_amount` | both sum the same capped per-installment receipts |
| INV-5 | `entry.received_amount + entry.outstanding_amount == entry.scheduled_amount` | per-entry outstanding derived by subtraction |
| INV-6 | `outstanding_amount >= 0` and `entry.outstanding_amount >= 0` | per-installment receipt capped at `min(Σ payments, amount)` |
| INV-7 | `partners_count == len(partners)`, and each partner appears at most once | dictionary keyed by `partner_id` during aggregation |
| INV-8 | empty range ⇒ all money fields `0.00`, both counts `0`, `partners == []` | every money accumulator seeded as `Decimal("0.00")` — see "Precision" below |

## Precision

`Decimal` carries its scale as part of its value, and that scale survives serialization: `Decimal("0")` renders as `0`, while `Decimal("0.00")` renders as `0.00`. An accumulator seeded with `Decimal("0")` therefore produces a **bare zero** on an empty range, breaking INV-8 and FR-014.

Rules:

1. **Seed every money accumulator as `Decimal("0.00")`**, never `Decimal("0")` — overall and per partner. This matches `get_loan_summary/application/use_case.py`, which already seeds `total_paid = Decimal("0.00")`.
2. Summing 2dp values into a 2dp seed keeps the result at 2dp, so no post-hoc rounding is needed on `expected_revenue`, `received_amount`, or any partner subtotal — and none should be applied, since re-rounding is what breaks INV-1 through INV-5.
3. The **only** value needing explicit quantization is `expected_profit`: its per-installment shares are full-precision ratios, summed unrounded and quantized to 2dp exactly once at the end.
4. Everything else is derived by subtraction from two 2dp operands, which is closed at 2dp.

An earlier draft of INV-8 claimed the `0.00` scale "falls out of empty accumulators". It does not — that assumption was the defect this section exists to prevent.

## Validation rules

| Rule | Source | Failure |
|------|--------|---------|
| `start_date` required | FR-002 | FastAPI 422 |
| `end_date` required | FR-002 | FastAPI 422 |
| well-formed `YYYY-MM-DD` dates | FastAPI | 422 |
| `end_date >= start_date` | FR-002 | `ValueError` in `domain/rules.py` → **HTTP 400** |
| authenticated caller | FR-013 | 401 from `get_current_user` |
