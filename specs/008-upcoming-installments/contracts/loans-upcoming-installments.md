# Contract: `GET /loans/upcoming-installments`

Row-level view of what the loan book still has to collect in a date window, across all
partners. The companion to `GET /loans/period-summary`, which answers the same question as
totals.

This file is the Phase 1 design contract for feature 008. On implementation, the same
content is folded into the standing contract at `specs/api/loans.md` (FR-015).

---

## Request

```text
GET /loans/upcoming-installments
```

Auth: `Authorization: Bearer <token>` required. Any authenticated user; no role guard —
same access level as `GET /loans/period-summary`.

### Query parameters

| Parameter | Type | Required | Default | Meaning |
|-----------|------|----------|---------|---------|
| `start_date` | date (`YYYY-MM-DD`) | **yes** | — | Inclusive lower bound on installment due date. Ignored as a bound when `include_overdue=true`, but still required. |
| `end_date` | date (`YYYY-MM-DD`) | **yes** | — | Inclusive upper bound on due date. Must be `>= start_date`. |
| `include_overdue` | bool | no | `false` | When true, additionally returns every unsettled installment due **before** `start_date`, with no lower cutoff — the whole loan history. |
| `partner_id` | UUID | no | — | Restrict to one partner's installments. |
| `limit` | int `>= 1` | no | — | Return at most this many rows. Applied **after** ordering, so you get the earliest-due N. |

---

## Response `200`

A JSON array — no envelope. Empty array when nothing matches.

```text
[
  {
    installment_id
    loan_id
    partner_id
    partner_name
    installment_number
    due_date
    amount              # scheduled for this installment
    paid_amount         # already received against it, capped at amount
    remaining_amount    # amount - paid_amount
    status              # PENDING | PARTIALLY_PAID  (never PAID)
    is_overdue          # due_date < today
  }
]
```

Example:

```json
[
  {
    "installment_id": "3f1c…",
    "loan_id": "9a02…",
    "partner_id": "c471…",
    "partner_name": "Partner A",
    "installment_number": 2,
    "due_date": "2026-07-20",
    "amount": "312.50",
    "paid_amount": "100.00",
    "remaining_amount": "212.50",
    "status": "PARTIALLY_PAID",
    "is_overdue": true
  },
  {
    "installment_id": "77be…",
    "loan_id": "9a02…",
    "partner_id": "c471…",
    "partner_name": "Partner A",
    "installment_number": 3,
    "due_date": "2026-08-17",
    "amount": "312.50",
    "paid_amount": "0.00",
    "remaining_amount": "312.50",
    "status": "PENDING",
    "is_overdue": false
  }
]
```

### Selection rule

An installment is returned when its loan is not `CANCELED`, its own status is not `PAID`,
its `due_date` is `<= end_date`, and either `due_date >= start_date` or
`include_overdue=true`. A `partner_id`, if given, further restricts to that partner.

Fully settled installments are **excluded** — this endpoint lists what is still owed, not
payment history. Inactive partners are included; an inactive partner still owes what it
owes.

### Ordering

`due_date` ascending, then `loan_id`, then `installment_number`. Deterministic: identical
requests return identical rows in identical order, which is what makes `limit` meaningful.

### Guarantees

- per row: `paid_amount + remaining_amount == amount`
- `remaining_amount >= 0.00` on every row, and `> 0.00` for any data created through the API (payments recorded directly in the database beyond an installment's amount are the only way to see `0.00` here)
- `status` is never `PAID`
- no negative amounts — payments beyond an installment's amount are capped
- every money field carries two decimals, including zeros (`"0.00"`, never `"0"`)
- `due_date` is non-decreasing down the list
- each installment appears at most once
- with `include_overdue=false`: `start_date <= due_date <= end_date` on every row
- with `include_overdue=true`: every row with `due_date < start_date` has `is_overdue: true`

`is_overdue` is evaluated against the server's current date at request time, independent of
the window — so with `include_overdue=false` and a window starting in the past, in-window
rows can legitimately come back `is_overdue: true`. An installment due **today** is not
overdue.

---

## Errors

| Status | When |
|--------|------|
| `400` | `end_date` is earlier than `start_date` |
| `401` | missing or invalid token |
| `422` | `start_date` or `end_date` missing or malformed; `limit` less than 1; `partner_id` not a valid UUID |

A `partner_id` that matches no partner is **not** an error — it returns `[]`. So does a
window in which nothing is due.

Authentication is resolved before query-parameter validation: a request with no token and a
malformed parameter returns `401`, not `422`. The `422` cases above assume a valid token.

---

## Reconciliation with `GET /loans/period-summary`

For the same window with `include_overdue=false`, the sum of `remaining_amount` across
these rows equals the summary's `outstanding_amount`.

> **One documented exception.** There are two ways to settle an installment and they record
> different things. `POST /loan-installments/{id}/payments` writes a payment row and updates
> status. `PATCH /loan-installments/{id}/pay` sets status to `PAID` **without** writing a
> payment row. This endpoint trusts status, so it drops such an installment; the period
> summary derives `received_amount` from payment rows only, so it still counts that
> installment's full amount as outstanding. The two will differ by exactly those amounts.
> This is a pre-existing disagreement between the two write paths, not a defect in either
> read endpoint, and feature 008 does not change it.

The reconciliation note already in `specs/api/loans.md` also applies: installment amounts
are each rounded to 2dp at loan creation, so a loan's installments need not sum exactly to
its `total_amount`.
