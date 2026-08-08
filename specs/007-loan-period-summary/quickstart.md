# Quickstart: Validating Loan Period Summary

Manual validation guide. **No automated tests** — this project's constitution forbids adding tests for new feature work, so these scenarios are the verification step.

See [contracts/loans-period-summary.md](./contracts/loans-period-summary.md) for the full response shape and [data-model.md](./data-model.md) for the invariants referenced below.

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

## Seed data

Use the existing endpoints — no direct SQL needed. A `BUGGYMAN`-type partner is required (`create_loan` rejects others).

1. `POST /loans/` for **Partner A** — e.g. `principal_amount: 1000`, `interest_rate: 25`, `installments_qty: 4`, `start_date: 2026-08-03`. Installments fall weekly from `2026-08-10`.
2. `POST /loans/` for **Partner B** — a second loan with a different `interest_rate`, so the profit split is not uniform across the book.
3. `POST /loans/` for **Partner C** with a `start_date` far outside the range you will query (e.g. `2027-01-04`).
4. `GET /loans/{loan_id}/installments` on Partner A's loan to note real installment ids and due dates.
5. `POST /loan-installments/{id}/payments` — pay one of Partner A's in-range installments **in full**, and a second one **partially**.

## Validation scenarios

### 1. Totals and the capital/profit split (US1)

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/loans/period-summary?start_date=2026-08-01&end_date=2026-08-31" | python3 -m json.tool
```

Expect:

- `expected_revenue` equals the sum of the in-range installment amounts you saw in step 4 (Partner A + Partner B, **not** Partner C).
- `expected_capital + expected_profit == expected_revenue` exactly (INV-1).
- `expected_profit` is non-zero and reflects both loans' differing rates.
- `installments_count` matches the number of in-range installments.

### 2. Inclusive boundaries (US1 scenario 3)

Query a range whose `start_date` is exactly one installment's due date and whose `end_date` is exactly another's. Both must be counted — narrow the range by one day on either end and confirm the corresponding installment drops out.

### 3. Partner list (US2)

- Partners A and B appear; Partner C does not.
- `sum(partners[].scheduled_amount) == expected_revenue` (INV-3).
- `partners_count == len(partners)` (INV-7).
- Entries are ordered by `scheduled_amount` descending.
- Add a **second loan for Partner A** with in-range installments, re-query, and confirm A still appears **exactly once** with the amounts combined (US2 scenario 2).

### 4. Received vs. outstanding (US3)

Given step 5's one full and one partial payment:

- `received_amount` equals the full payment plus the partial payment.
- `received_amount + outstanding_amount == expected_revenue` (INV-2).
- Partner A's entry: `received_amount + outstanding_amount == scheduled_amount` (INV-5).
- `sum(partners[].received_amount) == received_amount` (INV-4).

Then register a payment **dated outside the range** against an installment **due inside** the range: `received_amount` must increase — attribution follows due date, not payment date.

### 5. Canceled loans excluded (FR-010)

`PUT /loans/{loan_id}` on Partner B's loan with `status: "CANCELED"`, then re-query. Partner B disappears from `partners`, and all totals drop by Partner B's contribution. Revert afterwards.

### 6. Empty range (FR-012)

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/loans/period-summary?start_date=2030-01-01&end_date=2030-01-31"
```

Expect `200` with both counts `0` and `partners: []` — not a 404, not an error (INV-8).

**Inspect the raw JSON, not a pretty-printed view**: every money field must read `0.00`, **not** `0`. `Decimal` carries its scale through serialization, so an accumulator seeded `Decimal("0")` instead of `Decimal("0.00")` produces a bare zero here and violates FR-014. This is the single easiest thing to get wrong in the whole feature.

### 7. Single-day range

`start_date == end_date` on a known due date returns exactly that day's installments.

### 8. Error handling

| Request | Expect |
|---------|--------|
| `?start_date=2026-08-31&end_date=2026-08-01` | `400`, `detail` explains the inverted range |
| `?start_date=2026-08-01` (no `end_date`) | `422` |
| `?start_date=not-a-date&end_date=2026-08-31` | `422` |
| no `Authorization` header | `401` |

### 9. Overpayment guard (INV-6)

Register a payment larger than an in-range installment's amount. `outstanding_amount` must floor at `0.00` for that installment's contribution — never negative, overall or per partner.

### 10. Existing endpoints untouched

`GET /loans/{loan_id}/summary` and `GET /loans/?partner_id=...` must still respond exactly as before — in particular, confirm `/loans/{loan_id}` still resolves a real UUID after the router reordering in `urls.py`.

### 11. Inclusion rules that are easy to get wrong

Three spec edge cases that are correct by construction in the repository query, but worth confirming once:

- **Inactive partner**: set a partner with in-range installments to `active: false`. They must still appear — the debt is still owed, and the query does not filter on `active`.
- **Fully settled loan**: a loan whose `status` is `PAID` still contributes its in-range installments to `expected_revenue`, landing in `received_amount`. Only `CANCELED` is excluded.
- **Multi-month range**: query `start_date=2026-08-01&end_date=2027-02-28`. Installments across every month in between are included; no implicit month or year boundary is applied.

### 12. Performance and query count (SC-005, SC-006)

Time a one-month range and a twelve-month range against a representative loan book — expect under 1s and under 2s respectively. Then enable Tortoise query logging and confirm the **query count does not grow with the range**: a range covering ten times more installments must issue the same number of queries. A rising count means the `prefetch_related("loan__partner", "payments")` is not taking effect and the endpoint has an N+1.

## Completion check

- [ ] All twelve scenarios pass
- [ ] `specs/api/loans.md` documents the new endpoint, its query params, response shape, and error codes
- [ ] No test files added
- [ ] No migration generated (this feature touches no model)
