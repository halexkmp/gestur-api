# Phase 0 Research: Loan Period Summary

All items below were resolved against the existing codebase; no NEEDS CLARIFICATION remains.

---

## 1. Which context and slice should own this?

**Decision**: New slice `app/slices/partner_loan/period_summary/`.

**Rationale**: The feature reads only loan-domain entities (`Loan`, `LoanInstallment`, `LoanInstallmentPayment`, `Partner`) and is conceptually the period-level sibling of the existing `get_loan_summary` slice. Keeping it in `partner_loan` means one context owns all loan reads, and the contract update lands in `specs/api/loans.md` where a frontend developer would look for it.

**Alternatives considered**:

- **`app/slices/reports/`** — the `reports` context already holds aggregate/dashboard reads (`filter_sales`, `get_partner_customers_by_sales`) and, being prefixed `/reports`, has zero path-collision risk with `/loans/{loan_id}`. Rejected because it would split loan reads across two contexts and two contract files for no domain reason; the collision is solved by router ordering (§2). Worth revisiting only if a future dashboard needs one endpoint spanning sales *and* loans.
- **Extending `get_loan_summary`** — rejected outright: different input (a range, not a loan id), different output shape, and it would break the existing per-loan contract.

---

## 2. Route path and registration order

**Decision**: `GET /loans/period-summary`, with its router included in `app/slices/partner_loan/urls.py` **before** `get_loan_router`.

**Rationale**: FastAPI resolves routes in registration order. `get_loan_router` declares `GET /{loan_id}` with `loan_id: UUID`; if it is registered first, a request to `/loans/period-summary` matches it and fails UUID validation with a 422 before the new handler is ever consulted. Registering the literal path first is the standard FastAPI fix and costs one line placed in one specific position.

The name `period-summary` (rather than `summary`) keeps it visibly distinct from the existing `/loans/{loan_id}/summary`, so neither the contract file nor the frontend can confuse the two.

**Alternatives considered**:

- `GET /loans/summary` — rejected as too easily confused with the per-loan summary in docs and client code.
- Nesting under a new prefix such as `/loan-reports/` — rejected; a third router prefix in one context for a single endpoint is unjustified structure.
- Making the path a non-colliding shape like `/loans/reports/period` — rejected; deeper nesting without a second sibling endpoint is speculative.

---

## 3. Money arithmetic and the exact-invariant requirement

Three invariants from the spec must hold **exactly**, not approximately: `capital + profit == expected_revenue` (FR-005, SC-003), `received + outstanding == expected_revenue` (FR-007, SC-003), and `Σ partner.scheduled == expected_revenue` (SC-002).

**Decision**: derive one side of each pair and subtract for the other, never round both independently.

- `expected_revenue = Σ installment.amount` over selected installments. Each `amount` is already a 2dp `Decimal` persisted by `create_loan`, so the sum is exact with no rounding at all. Partner subtotals sum the same values, so SC-002 holds by construction.
- `profit` — accumulate at full `Decimal` precision using each installment's own loan ratio, then quantize **once** at the end: `profit_i = amount_i * (loan.total_amount - loan.principal_amount) / loan.total_amount`. Then `capital = expected_revenue - profit`. Rounding capital independently would let the pair drift by a cent.
- `received` — computed per installment as `min(Σ payment.amount, installment.amount)`, summed. Then `outstanding = expected_revenue - received`. The `min` cap implements the overpayment edge case (outstanding never goes negative) and, because per-partner received uses the same capped per-installment values, per-partner and overall figures stay mutually consistent.
- Per partner: `partner.outstanding = partner.scheduled - partner.received`, same subtract-don't-round-twice rule.

**Rationale**: This matches how `get_loan_summary` already behaves (`remaining_balance = total_amount - total_paid`, rounded once) and is the only approach that satisfies the invariants for arbitrary interest rates.

**Scale, not just value**: `Decimal` carries its scale as part of its value and keeps it through serialization — `Decimal("0")` renders as `0`, `Decimal("0.00")` as `0.00`. Every money accumulator must therefore be seeded `Decimal("0.00")`, or an empty range returns bare zeros and violates FR-014. `get_loan_summary` already seeds `total_paid = Decimal("0.00")`; follow it. Summing 2dp values into a 2dp seed stays at 2dp, so no other field needs rounding — and none should get it, since re-rounding is exactly what breaks the invariants above. Full detail in [data-model.md](./data-model.md) §Precision.

**Note on an existing rounding artifact** (not introduced here, not fixed here): `create_loan` sets every installment to `round(total_amount / installments_qty, 2)`, so `Σ installment.amount` can differ from `loan.total_amount` by a few cents on loans that do not divide evenly. This feature deliberately treats **the installments as the source of truth for what will be collected** — that is what the partner actually owes on those dates. It is called out in the contract so the dashboard does not expect a full-loan `total_amount` to reconcile exactly against a sum of per-period figures.

**Alternatives considered**:

- Rounding profit and capital independently, then asserting they sum — rejected; fails for common ratios.
- Deriving profit from `interest_rate` directly (`amount × rate / (100 + rate)`) — rejected; the persisted `total_amount` is the authoritative figure and may have been edited via `update_loan` independently of `interest_rate`. Using the stored `principal_amount`/`total_amount` pair keeps the split consistent with what the loan actually says.
- SQL-side aggregation (`annotate`/`Sum`) — rejected; see §5.

---

## 4. Selecting installments: filter, exclusions, and prefetch

**Decision**: a single query in the repository —

```text
LoanInstallment
  .filter(due_date__gte=start_date, due_date__lte=end_date)
  .exclude(loan__status=LoanStatus.CANCELED)
  .prefetch_related("loan__partner", "payments")
  .order_by("due_date", "installment_number")
```

**Rationale**:

- `due_date__gte` / `due_date__lte` gives the inclusive-both-ends range the spec requires (FR-001, US1 scenario 3), and mirrors the `created_at__gte` / `created_at__lte` pattern already used in `filter_sales/infra/repository.py`.
- `.exclude(loan__status=CANCELED)` implements FR-010 as a database-side filter rather than a Python skip, so canceled installments never reach the aggregation. Loans with status `PAID` are *not* excluded — a historical range must still show them as received (spec edge case "Fully settled loans").
- `prefetch_related("loan__partner", "payments")` collapses what would otherwise be N+1 lookups per installment into a bounded number of queries, and gives the use case everything it needs: the loan's `principal_amount`/`total_amount` for the profit split, the partner's `id`/`name` for grouping, and the payments for the received calculation.
- Deterministic ordering keeps output stable between identical requests.

**Alternatives considered**:

- Querying `Loan` first and walking `loan.installments` — rejected; would load installments outside the range and force Python-side filtering.
- Filtering by loan `start_date`/`end_date` overlap — rejected; a loan can span the range while none of its installments fall inside it, which would inflate the partner list.

---

## 5. Where to aggregate: Python vs. SQL

**Decision**: aggregate in Python in the use case, over the prefetched result set.

**Rationale**: The per-installment profit split depends on its *own loan's* ratio and must be accumulated at full precision before a single final rounding (§3) — expressible in SQL only awkwardly, and Tortoise's aggregation API would not keep the exact-invariant guarantees legible. The existing `get_loan_summary` use case already aggregates installments and payments in Python, so this is the established pattern (Principle IV). At the stated scale — hundreds of installments per range — the cost is negligible, and business rules stay out of the repository as Principle I requires.

**Alternatives considered**: Tortoise `annotate(Sum(...))` with `group_by` — rejected on the precision/consistency grounds above, and because it would push the profit formula (a business rule) into `infra/`.

---

## 6. Input validation and error mapping

**Decision**: `start_date` and `end_date` are required `date` query parameters. `end_date < start_date` raises `ValueError` from `domain/rules.py`, which the route maps to **HTTP 400** with the message as `detail`.

**Rationale**: FastAPI already rejects malformed dates with its own 422. The only business-level input rule is the inverted range, and 400 matches how `create_loan`, `update_loan`, and `register_payment` in this same context already surface `ValueError` for invalid input (404 is used only for genuine "not found", which does not apply to an aggregate query). `start_date == end_date` is valid and covers a single day.

Empty results are **not** an error: FR-012 requires a 200 with zeroed totals and an empty partner list.

**Alternatives considered**:

- Optional dates defaulting to the current month — rejected; the spec's Assumptions section explicitly states both dates are required and no implicit range is applied.
- A Pydantic query model with a `model_validator` — rejected as heavier than the one-line rule; the codebase validates in `domain/rules.py` (see `create_loan/domain/rules.py::validate_amount_dates`).

---

## 7. Authorization

**Decision**: `Depends(get_current_user)` only — no role guard.

**Rationale**: FR-013 says access matches the existing loan endpoints, and every current route in `partner_loan/urls.py` (`list_loans`, `get_loan`, `get_loan_summary`, `list_loan_installments`, …) is authenticated-only with no call to `ensure_admin`/`ensure_hr`. Adding a role gate here would make the aggregate stricter than the per-loan data it summarizes, which is inconsistent and outside the spec.

**Alternatives considered**: `ensure_admin` — rejected; not requested, and any authenticated user can already reconstruct these figures from the existing loan endpoints.

---

## 8. Partner list ordering

**Decision**: sort partners by `scheduled_amount` descending, tie-broken by `partner_name` ascending.

**Rationale**: The spec sets no ordering requirement, and the dashboard use case is "who do I follow up with" — largest debtor first is the most useful default, and the name tie-break makes the order fully deterministic for identical amounts.

**Alternatives considered**: alphabetical by name (less actionable for the stated purpose); insertion order from the query (non-deterministic across equal amounts).
