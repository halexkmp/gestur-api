# Phase 0 Research: Upcoming Loan Installments List

All items below were resolved against the existing codebase. No NEEDS CLARIFICATION remains. The one open scope question from `/speckit-specify` — how far back the overdue option reaches — was confirmed by the user: **all time, behind a flag that defaults to off** (FR-010).

---

## 1. Which context and slice should own this?

**Decision**: New slice `app/slices/partner_loan/upcoming_installments/`.

**Rationale**: The feature reads only loan-domain entities (`Loan`, `LoanInstallment`, `LoanInstallmentPayment`, `Partner`) and is the row-level counterpart to the aggregate `period_summary` slice added in 007. Keeping it in `partner_loan` means one context owns all loan reads and the contract update lands in `specs/api/loans.md`, next to the summary a frontend developer will already be reading.

**Alternatives considered**:

- **Extending `period_summary` with an `installments[]` array** — rejected. It would couple a lightweight dashboard aggregate to an unbounded row list, and the two have genuinely different parameters (this one adds `include_overdue`, `partner_id`, `limit`, none of which mean anything to a totals response). The spec's Assumptions section commits to leaving the summary unchanged.
- **Extending `list_loan_installments`** — rejected. That slice answers "the installments of *this* loan" from a path parameter; this one spans the whole book from a date window. Different input, different selection rule, and widening it would break the existing per-loan contract.
- **`app/slices/reports/`** — rejected for the same reason 007 rejected it: it would split loan reads across two contexts and two contract files for no domain reason.

---

## 2. Route path and registration order

**Decision**: `GET /loans/upcoming-installments`, with its router included in `app/slices/partner_loan/urls.py` **before** `get_loan_router`.

**Rationale**: Identical to the trap 007 documented and `urls.py:17-19` already carries a comment about. FastAPI resolves in registration order; `get_loan_router` declares `GET /{loan_id}` with `loan_id: UUID`, so a request to `/loans/upcoming-installments` registered after it matches the UUID route and dies with a 422 before this handler is consulted. The new router goes next to `period_summary_router`, above `get_loan_router`.

The `upcoming-installments` name keeps it distinct from `GET /loans/{loan_id}/installments`, which remains the per-loan listing.

**Alternatives considered**:

- `GET /loans/installments` — rejected; reads as "all installments" and sits one path segment away from the per-loan route, inviting confusion in client code.
- A new `/loan-installments/upcoming` route on the existing `installments_router` — genuinely tempting, since that prefix already exists and has **no** collision risk. Rejected because every route under `/loan-installments/` today addresses one installment by id (`/{installment_id}/pay`, `/{installment_id}/payments`); a collection query rooted at the loan book belongs with `/loans/period-summary`, which it will always be read alongside.

---

## 3. What counts as "already settled"? (FR-005)

This is the one place where the codebase is not self-consistent, and it decides the selection rule.

There are two ways an installment gets settled today, and they do **not** agree:

- `register_payment` (`POST /loan-installments/{id}/payments`) inserts a `LoanInstallmentPayment` row and then sets `status = PAID` when the payments sum reaches `installment.amount`, or `PARTIALLY_PAID` otherwise. Status and payment rows stay in sync.
- `pay_loan_installment` (`PATCH /loan-installments/{id}/pay`) sets `status = PAID` and stamps `payment_date` **without inserting any payment row**. An installment can therefore be `PAID` with zero recorded payments.

**Decision**: select on `status != PAID`. Do not derive settlement from the payments sum.

**Rationale**: `status` is the explicit operator signal — someone marked that installment settled, and a collections list must not keep nagging about it. Deriving settlement from payment rows instead would resurrect every installment closed via `PATCH /pay` as if nothing had been received, which is precisely the wrong answer for the one screen this feature exists to power. `status` is also a superset of the payments-derived condition: `register_payment` guarantees `PAID` whenever the sum reaches the amount (and rejects overpayment outright), so no fully-paid installment can slip past a status filter. Filtering on an indexed-ish scalar column also keeps the selection in SQL rather than in Python.

**Consequence for SC-002, stated plainly**: the spec asks that the returned installments reconcile with `period_summary`'s `outstanding_amount` for the same window. That holds exactly for installments settled through `register_payment`. It does **not** hold for an installment force-marked `PAID` via `PATCH /pay`: this list excludes it (status says settled), while `period_summary` computes `received` purely from payment rows and so still counts its full amount as outstanding. The divergence is pre-existing — it is `period_summary` and `pay_loan_installment` disagreeing with each other, not something this feature introduces — and it is left alone here under Principle IV. The reconciliation caveat is documented in the contract so the dashboard does not treat a mismatch as a bug in either endpoint.

**Alternatives considered**:

- **Settlement from `min(Σ payments, amount) >= amount`** — rejected per above; it ignores the `PATCH /pay` path and would show settled debts as unpaid.
- **Select on both conditions (`status != PAID` AND payments sum < amount)** — rejected as redundant. `register_payment` already flips status to `PAID` at exactly the point the sum condition trips, so the second clause can never exclude a row the first one kept.
- **Fixing `pay_loan_installment` to write a payment row, or `period_summary` to honour status** — out of scope. It is a real inconsistency worth a follow-up, but this feature is read-only and Principle IV forbids the drive-by fix. Flagged, not fixed.

---

## 4. Overdue semantics and the reference date

**Decision**: `is_overdue = due_date < date.today()`, evaluated per row at request time. `include_overdue` (default `false`) controls only *selection*; the `is_overdue` flag is reported on every row either way.

**Rationale**: Separating the two keeps the flag honest. With `include_overdue=false` and a window that starts in the past, in-window rows can still be overdue — the flag has to say so. Because the query already filters `status != PAID` (§3), the "and not fully settled" half of FR-008 is satisfied by construction, so the comparison reduces to the date test. An installment due *today* is not overdue: FR-008 says strictly earlier.

`date.today()` matches what `pay_loan_installment` and `register_payment` already use. It resolves against the server's local date, which is UTC on Vercel while the business runs at UTC-3 — so between 21:00 and 24:00 local time the server has already rolled to tomorrow and an installment due "tomorrow" will read as due today. This affects only the boundary flag, is pre-existing across the loan slices, and is not corrected here; introducing a timezone-aware clock in one slice would make this slice the odd one out.

**Alternatives considered**:

- **Judging overdue against `start_date` instead of today** — rejected; it would make the flag mean "before the window", which the caller already knows from the dates it sent.
- **Passing a caller-supplied reference date** — rejected as speculative surface area; nothing in the spec asks for it.

---

## 5. Query shape: one round trip, filtering and limiting in SQL

**Decision**: a single repository method with explicit optional parameters:

```python
async def list_due_installments(
    self,
    start_date: Optional[date],   # None ⇒ no lower bound (overdue included)
    end_date: date,
    partner_id: Optional[UUID],
    limit: Optional[int],
) -> list[LoanInstallment]
```

built as `LoanInstallment.filter(due_date__lte=end_date).exclude(loan__status=CANCELED).exclude(status=PAID)`, conditionally narrowed by `due_date__gte=start_date` and `loan__partner_id=partner_id`, then `.prefetch_related("loan__partner", "payments").order_by("due_date", "loan_id", "installment_number")` and `.limit(limit)` when given.

**Rationale**: The `include_overdue` boolean is a business rule, so the **use case** resolves it into a lower bound (`start_date` or `None`) and the repository only ever sees persistence-level arguments — Principle I, no business rules in `infra/`. `prefetch_related` mirrors `period_summary`'s repository and avoids the N+1 that a naive partner/payments walk would cause. Applying `limit` in SQL rather than slicing in Python matters precisely because `include_overdue=true` is unbounded on the low side: the whole point of `limit` is to not haul the entire back catalogue into memory to show five rows. The ordering is applied before the limit, and is fully deterministic (`loan_id` breaks same-day ties across loans, `installment_number` within a loan), so the truncated set is stable across identical requests.

**Alternatives considered**:

- **Two repository methods, one per overdue mode** — rejected; the queries differ by a single bound, and duplicating the prefetch/order/limit chain is the kind of near-copy Principle IV warns about.
- **Passing `include_overdue: bool` into the repository** — rejected; that is the business rule leaking into `infra/`.
- **SQL-side aggregation of payments (`annotate(Sum)`)** — rejected for the reason 007 gives: the per-installment cap (`min(Σ payments, amount)`) is a business rule, and prefetch keeps it in the domain layer where the same rule already lives.
- **Python-side slicing for `limit`** — rejected; defeats the purpose under `include_overdue=true`.

---

## 6. Reusing `received_for_installment` across slices

**Decision**: re-declare the rule in this slice's own `domain/rules.py`. Do **not** import it from `period_summary/domain/rules.py`.

**Rationale**: Principle I makes slices self-contained; a cross-slice import into another feature's `domain/` creates exactly the coupling VSA exists to prevent, and would mean a change to the period summary's rules silently retargets this endpoint. The rule is four lines. `app/shared/` is not the answer either — the constitution reserves it for stable cross-cutting concerns, and a payment-allocation cap is feature logic that moves when business rules move.

The duplicated cap is the same one-liner: `min(sum(payments), installment.amount)`, which implements the overpayment edge case (remaining never goes negative) even though `register_payment` currently rejects overpayment at write time.

**Alternatives considered**:

- **Promote to `app/shared/`** — rejected per the constitution's explicit carve-out.
- **Import across slices** — rejected; direct Principle I violation.

---

## 7. Response shape: flat array, not an envelope

**Decision**: return a bare JSON array of installment rows.

**Rationale**: Every existing list endpoint in this context returns a flat array (`GET /loans/` → `List[LoanResponse]`, `GET /loans/{id}/installments` → `List[LoanInstallmentResponse]`, `GET /loan-installments/{id}/payments`). An envelope with counts and totals would duplicate what `period_summary` already returns for the same window, and would be the only shape of its kind in the context.

Row fields follow FR-006: `installment_id`, `loan_id`, `partner_id`, `partner_name`, `installment_number`, `due_date`, `amount`, `paid_amount`, `remaining_amount`, `status`, `is_overdue`. The id field is named `installment_id` rather than the bare `id` used by `LoanInstallmentResponse` because three ids appear side by side in one row and an unqualified `id` would be ambiguous at the call site.

**Alternatives considered**:

- **`{ items: [...], count: n, total_remaining: x }`** — rejected; totals for a window are `period_summary`'s job, and adding a second source for them invites the two to disagree.
- **Reusing `LoanInstallmentResponse` from `list_loan_installments`** — rejected on two counts: it lacks the loan/partner/payment fields this row needs, and Principle I keeps Pydantic schemas private to their own slice.

---

## 8. Parameter validation and error mapping

**Decision**:

- `start_date`, `end_date` required; `end_date < start_date` → `ValueError` in the domain rule → `400` in the route, mirroring `period_summary/ui/route.py` exactly.
- `limit` declared as `Query(None, ge=1)` → FastAPI returns `422` for `limit=0` or negative.
- `partner_id` that matches no partner → empty array, **not** `404`.

**Rationale**: The `400`-for-reversed-range path is copied verbatim from the sibling slice so the two endpoints behave identically on the same mistake. `limit` is a pure input-shape constraint with no business meaning, so FastAPI's own validator is the right layer and `422` is the honest status. Not 404-ing on an unknown partner matches `list_loans`, which filters by `partner_id` without an existence check — and "this partner owes nothing in this window" is a legitimate empty result indistinguishable, to a collections user, from "no such partner".

**Alternatives considered**:

- **Validating `limit` in the domain rule for a `400`** — rejected; inconsistent with how FastAPI already reports malformed dates on the sibling endpoint (`422`).
- **`404` on unknown `partner_id`** — rejected; would require an extra query solely to distinguish two cases that produce the same answer, and diverges from `list_loans`.

---

## 9. No schema change

**Decision**: no new model, no new column, no Aerich migration.

**Rationale**: Every reported value is derived from existing rows — `loan_installment` supplies the amount, due date, number and status; `loan_installment_payment` supplies what was received; `loan` supplies cancellation and the partner link; `partner` supplies the name. `is_overdue` and `remaining_amount` are computed per request and deliberately not persisted, since both are functions of the current date and current payments.
