# Contract: Loan Period Summary

> This is the feature-time contract. On implementation, the same endpoint MUST also be
> folded into the standing contract at `specs/api/loans.md` (constitution, Principle III).

## Endpoint

```text
GET /loans/period-summary
```

**Auth**: Bearer token required (`get_current_user`). No role guard — same as every other endpoint in the loans context.

**Registration order**: this route MUST be included in `app/slices/partner_loan/urls.py` **before** `get_loan_router`, otherwise `GET /loans/{loan_id}` shadows it and returns 422 on the literal segment `period-summary`.

---

## Query parameters

| Name | Type | Required | Notes |
|------|------|----------|-------|
| `start_date` | `date` (`YYYY-MM-DD`) | yes | inclusive lower bound on installment due date |
| `end_date` | `date` (`YYYY-MM-DD`) | yes | inclusive upper bound; must be `>= start_date` |

No partner filter, no pagination.

---

## Response `200 OK`

```text
start_date              # date, echo of the request
end_date                # date, echo of the request
expected_revenue        # decimal, total scheduled to be received in the range
expected_capital        # decimal, principal portion of expected_revenue
expected_profit         # decimal, interest portion of expected_revenue
received_amount         # decimal, already paid against those installments
outstanding_amount      # decimal, still to collect
installments_count      # int, installments falling in the range
partners_count          # int, distinct partners in the range
partners: [
  {
    partner_id          # uuid
    partner_name        # string
    scheduled_amount    # decimal
    received_amount     # decimal
    outstanding_amount  # decimal
    installments_count  # int
  }
]
```

`partners` is ordered by `scheduled_amount` descending, then `partner_name` ascending.

### Guarantees the client can rely on

- `expected_capital + expected_profit == expected_revenue`
- `received_amount + outstanding_amount == expected_revenue`
- `sum(partners[].scheduled_amount) == expected_revenue`
- `sum(partners[].received_amount) == received_amount`
- per entry: `received_amount + outstanding_amount == scheduled_amount`
- no amount is negative; a partner appears at most once
- every money field always carries two decimals, **including zeros** (`"0.00"`, never `"0"`)
- `partners` ordering is deterministic, so identical requests return identical lists

### What "expected revenue" counts

Installments whose **due date** falls inside the range, regardless of when (or whether) they were paid. Installments on `CANCELED` loans are excluded entirely. Installments on fully `PAID` loans are included and land in `received_amount`.

> **Reconciliation note for the dashboard**: per-period figures sum the persisted installment amounts, which `create_loan` rounds to 2dp each. On a loan whose total does not divide evenly by its installment count, the sum of all its installments can differ from the loan's own `total_amount` by a few cents. The installments are authoritative for what a partner actually owes on a date; do not expect a full-loan `total_amount` to reconcile exactly against a sum of period summaries.

### Example

```json
{
  "start_date": "2026-08-01",
  "end_date": "2026-08-31",
  "expected_revenue": "4500.00",
  "expected_capital": "3750.00",
  "expected_profit": "750.00",
  "received_amount": "1200.00",
  "outstanding_amount": "3300.00",
  "installments_count": 9,
  "partners_count": 2,
  "partners": [
    {
      "partner_id": "3f1a...",
      "partner_name": "Carlos Buggy",
      "scheduled_amount": "3000.00",
      "received_amount": "1200.00",
      "outstanding_amount": "1800.00",
      "installments_count": 6
    },
    {
      "partner_id": "9b2c...",
      "partner_name": "Ana Passeios",
      "scheduled_amount": "1500.00",
      "received_amount": "0.00",
      "outstanding_amount": "1500.00",
      "installments_count": 3
    }
  ]
}
```

### Empty range

A range with no matching installments is **not** an error:

```json
{
  "start_date": "2030-01-01",
  "end_date": "2030-01-31",
  "expected_revenue": "0.00",
  "expected_capital": "0.00",
  "expected_profit": "0.00",
  "received_amount": "0.00",
  "outstanding_amount": "0.00",
  "installments_count": 0,
  "partners_count": 0,
  "partners": []
}
```

---

## Errors

| Status | When | Body |
|--------|------|------|
| `400` | `end_date` is earlier than `start_date` | `{"detail": "end_date must be on or after start_date"}` |
| `401` | missing or invalid bearer token | standard auth error |
| `422` | `start_date` or `end_date` missing or not a valid date | FastAPI validation error |

---

## Unchanged endpoints

`GET /loans/{loan_id}/summary`, `GET /loans/`, `GET /loans/{loan_id}`, `GET /loans/{loan_id}/installments` and all `/loan-installments/*` routes keep their current paths, parameters, and response shapes. This feature is purely additive.
