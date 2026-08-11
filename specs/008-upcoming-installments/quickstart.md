# Quickstart: Validating the Upcoming Installments List

Manual validation guide. **No automated tests** — this project's constitution forbids adding tests for new feature work, so these scenarios are the verification step.

See [contracts/loans-upcoming-installments.md](./contracts/loans-upcoming-installments.md) for the full response shape and [data-model.md](./data-model.md) for the invariants referenced below.

## Prerequisites

- `.env` configured for the local database (dev falls back to local Postgres defaults).
- Schema up to date — this feature adds no migration, but the loan tables must exist:

```bash
aerich upgrade
```

## Run

```bash
python app/main.py     # or: uvicorn app.main:app --reload
```

Interactive docs at <http://localhost:8000/docs> (available whenever `ENVIRONMENT != production`).

Get a token:

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -d 'username=<user>&password=<pass>' \
  -H 'Content-Type: application/x-www-form-urlencoded' | python3 -c 'import json,sys;print(json.load(sys.stdin)["access_token"])')
```

Convenience wrapper used throughout:

```bash
q() { curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/loans/upcoming-installments?$1" | python3 -m json.tool; }
```

## Seed data

Use the existing endpoints — no direct SQL needed. A `BUGGYMAN`-type partner is required (`create_loan` rejects others). Dates below assume "today" is around 2026-08-10; shift them to match your run.

1. `POST /loans/` for **Partner A** with a `start_date` in the **past** (e.g. `2026-06-01`), `installments_qty: 6` — this produces both already-overdue and still-future installments.
2. `POST /loans/` for **Partner B** with `start_date: 2026-08-03`, `installments_qty: 4`.
3. `POST /loans/` for **Partner C** with a `start_date` far in the future (e.g. `2027-01-04`) — should never appear in the windows below.
4. `GET /loans/{loan_id}/installments` on each loan to note real installment ids and due dates.
5. On Partner A's loan: `POST /loan-installments/{id}/payments` for a **partial** amount on one overdue installment.
6. On Partner B's loan: `POST /loan-installments/{id}/payments` for the **full** amount on one in-window installment.
7. `POST /loans/` a fourth loan and immediately `PUT /loans/{id}` to set status `CANCELED` (or use an existing canceled loan).

## Validation scenarios

### 1. In-window rows only (US1 · FR-001, FR-002, FR-004, FR-005)

```bash
q 'start_date=2026-08-01&end_date=2026-08-31'
```

Expect:

- Only installments with `due_date` between `2026-08-01` and `2026-08-31` inclusive.
- Partner A's June/July installments **absent** (overdue, flag is off).
- Partner C **absent** (due in 2027).
- The canceled loan's installments **absent**.
- The Partner B installment paid in full at seed step 6 **absent** — it is settled.
- Every row carries `partner_name`, and `status` is `PENDING` or `PARTIALLY_PAID`, never `PAID`.

### 2. Ordering and per-row arithmetic (US1 · FR-006, FR-007, FR-009)

Against the same output:

- `due_date` never decreases going down the list.
- On every row `paid_amount + remaining_amount == amount`, and `remaining_amount > 0`.
- The partially-paid installment shows a non-zero `paid_amount` with `status: "PARTIALLY_PAID"`.
- A never-touched installment shows `paid_amount: "0.00"` — two decimals, not `0`.

### 3. Boundary dates are inclusive (Edge case)

Pick a known due date `D` from step 4, then:

```bash
q "start_date=$D&end_date=$D"
```

Expect exactly the installments due on `D` and nothing else. Then re-run with `start_date=$D&end_date=2026-12-31` and confirm the `D` rows are still present — the lower bound includes its own date.

### 4. Overdue excluded by default, included on request (US2 · FR-010)

```bash
q 'start_date=2026-08-01&end_date=2026-08-31'                       # flag off
q 'start_date=2026-08-01&end_date=2026-08-31&include_overdue=true'  # flag on
```

Expect:

- The second result is a **superset** of the first.
- The extra rows all have `due_date < 2026-08-01` and `is_overdue: true`, and they sort **ahead** of the in-window rows.
- Partner A's partially-paid overdue installment from seed step 5 appears, with its partial `paid_amount`.
- No fully-settled past installment appears in either result.
- The overdue rows reach back over the entire history — there is no cutoff beyond which old debt is dropped.

### 5. `is_overdue` is judged against today, not the window (FR-008)

```bash
q 'start_date=2026-01-01&end_date=2026-12-31'
```

With a window spanning today, expect rows on both sides: `is_overdue: true` for rows whose `due_date` is before today, `false` for today and later — even though every row is in-window and the flag was never set. An installment due exactly today must read `false`.

### 6. Partner filter (US3 · FR-011)

```bash
q 'start_date=2026-08-01&end_date=2026-08-31&partner_id=<partner-a-id>'
q 'start_date=2026-08-01&end_date=2026-08-31&partner_id=<partner-c-id>'
q 'start_date=2026-08-01&end_date=2026-08-31&partner_id=00000000-0000-0000-0000-000000000000'
```

Expect: exactly Partner A's subset of scenario 1; then `[]` for Partner C (nothing due in August); then `[]` for the unknown id — **`200` with an empty array, not a `404`**.

### 7. Limit truncates the earliest-due rows (FR-012)

```bash
q 'start_date=2026-01-01&end_date=2026-12-31&include_overdue=true&limit=3'
```

Expect exactly 3 rows, identical to the first 3 of the same query without `limit`. Re-run it — same rows, same order.

### 8. Empty window is not an error (FR-013)

```bash
q 'start_date=2030-01-01&end_date=2030-01-31'
```

Expect `200` with `[]`.

### 9. Errors (FR-003, FR-014)

```bash
q 'start_date=2026-08-31&end_date=2026-08-01'          # reversed → 400
q 'start_date=2026-08-01'                               # missing end_date → 422
q 'start_date=2026-08-01&end_date=2026-08-31&limit=0'  # limit < 1 → 422
curl -s -o /dev/null -w '%{http_code}\n' \
  'http://localhost:8000/loans/upcoming-installments?start_date=2026-08-01&end_date=2026-08-31'  # no token → 401
```

The `400` body should carry a message naming the problem, matching how `GET /loans/period-summary` reports the same mistake.

### 10. Route is reachable, not shadowed (research.md §2)

The check that catches the registration-order bug:

```bash
curl -s -o /dev/null -w '%{http_code}\n' -H "Authorization: Bearer $TOKEN" \
  'http://localhost:8000/loans/upcoming-installments?start_date=2026-08-01&end_date=2026-08-31'
```

Must be `200`. A `422` complaining about UUID parsing means the new router was registered **after** `get_loan_router` in `app/slices/partner_loan/urls.py` and `GET /loans/{loan_id}` swallowed the literal path.

### 11. Reconciliation against the period summary (SC-002)

```bash
q 'start_date=2026-08-01&end_date=2026-08-31'
curl -s -H "Authorization: Bearer $TOKEN" \
  'http://localhost:8000/loans/period-summary?start_date=2026-08-01&end_date=2026-08-31' | python3 -m json.tool
```

Sum `remaining_amount` across the rows and compare with the summary's `outstanding_amount`. They must match.

> **Expected exception.** If any installment in the window was settled via
> `PATCH /loan-installments/{id}/pay` rather than `POST .../payments`, the two figures differ
> by exactly that installment's amount: this endpoint drops it (status says `PAID`), the
> summary still counts it as outstanding (no payment row exists). See
> [research.md](./research.md) §3 — a pre-existing disagreement between the two write paths,
> not a bug in either read endpoint. To confirm the reconciliation cleanly, seed payments only
> through `POST /loan-installments/{id}/payments`.

### 12. One query per request — no N+1 (SC-004)

The responsiveness criterion is really a query-count criterion: every row reaches through `loan → partner` and `payments`, so a missing prefetch turns one request into hundreds of queries and degrades as the loan book grows.

Enable SQL echo (`ENVIRONMENT` other than production already runs with reload; add Tortoise query logging if it is not already on), then run scenario 1 against a window holding at least a dozen installments across several loans and partners:

```bash
q 'start_date=2026-08-01&end_date=2026-08-31'
```

Expect a small, **constant** number of SQL statements — one for the installments plus one per prefetched relation — not one query per returned row. Widening the window so it returns twice as many rows must not increase the statement count.

If it scales with row count, `prefetch_related("loan__partner", "payments")` is missing or misspelled in `infra/repository.py` (T003).

## Contract sync check

Not optional, per the constitution (FR-015). After implementing, confirm
`specs/api/loans.md` documents the new route in its endpoint list, its four query
parameters, the response row shape, the selection and ordering rules, and the `400`/`422`
cases. The `update-api-contract` skill audits this.
