# Feature Requirements

# Feature

Loan Installment Payments

---

# Objective

Implement the ability to register one or more payments for a loan installment.

The feature must support partial payments, allowing an installment to be paid over multiple transactions until its full amount is settled.

Each payment must be permanently recorded to provide a complete financial history.

This feature is backend-only and will be exposed through the existing Python API.

---

# Business Rules

## Payment Registration

A payment must always be associated with exactly one loan installment.

Each payment records:

- Installment reference
- Payment amount
- Payment date
- Optional notes

Multiple payments may exist for the same installment.

---

## Partial Payments

An installment may receive multiple payments before being fully paid.

Example:

Installment amount:

```
1000.00
```

Payments:

```
300.00
200.00
500.00
```

The installment becomes fully paid only when the total paid amount equals its original amount.

---

## Payment Validation

The system must validate:

- Installment exists.
- Payment amount is greater than zero.
- Payment amount cannot exceed the remaining installment balance.
- Payment date is required.

Attempts to overpay an installment must be rejected.

---

## Installment Status

The installment status must be derived from its payments.

Possible statuses:

- PENDING
- PARTIALLY_PAID
- PAID

Status rules:

### PENDING

No payments have been registered.

### PARTIALLY_PAID

Total paid amount is greater than zero but less than the installment amount.

### PAID

Total paid amount equals the installment amount.

---

## Payment Date

The installment payment date should represent the date of the final payment that fully settles the installment.

Until then, the payment date remains null.

---

# Data Model

## LoanInstallment

The existing model must be updated.

### Fields

| Field | Type |
|--------|------|
| id | UUID |
| loan_id | UUID |
| installment_number | Integer |
| amount | Decimal |
| due_date | Date |
| payment_date | Date (nullable) |
| status | Enum |
| created_at | Datetime |
| updated_at | Datetime |

---

## LoanInstallmentPayment

New entity.

| Field | Type |
|--------|------|
| id | UUID |
| loan_installment_id | UUID |
| amount | Decimal |
| payment_date | Date |
| notes | String (nullable) |
| created_at | Datetime |
| updated_at | Datetime |

---

# Status Enum

```
PENDING

PARTIALLY_PAID

PAID
```

---

# API Requirements

## Register Payment

Create a payment for an installment.

```
POST /loan-installments/{installment_id}/payments
```

Request:

```json
{
    "amount": 300.00,
    "payment_date": "2026-07-10",
    "notes": "Advance payment"
}
```

Response:

Returns the created payment.

---

## List Payments

Retrieve every payment registered for an installment.

```
GET /loan-installments/{installment_id}/payments
```

Response:

Returns payments ordered by payment date.

---

# Automatic Behavior

Whenever a payment is created:

1. Validate installment exists.
2. Validate payment amount.
3. Validate remaining balance.
4. Persist the payment.
5. Recalculate the installment status.
6. If fully paid:
   - Update installment status to `PAID`.
   - Set installment payment date using the payment date of the last payment.
7. Otherwise:
   - Update installment status to `PARTIALLY_PAID`.
   - Keep installment payment date as null.

All operations must occur inside the same database transaction.

---

# Validation Rules

- Installment must exist.
- Payment amount must be greater than zero.
- Payment amount must not exceed remaining balance.
- Payment date is required.
- Notes are optional.

---

# Derived Values

The following values must always be calculated from registered payments.

## Total Paid

```
SUM(payment.amount)
```

## Remaining Balance

```
installment.amount - total_paid
```

## Installment Status

```
total_paid == 0
    -> PENDING

0 < total_paid < installment.amount
    -> PARTIALLY_PAID

total_paid == installment.amount
    -> PAID
```

These values must never be persisted independently.

---

# Non-Functional Requirements

- Follow the existing Vertical Slice Architecture.
- Use asynchronous database operations.
- Keep business rules inside the Application or Domain layer.
- Repository must contain only persistence logic.
- All monetary values must use Decimal.
- Use UUID identifiers.
- Database operations must be transactional.
- Implement unit tests.
- Implement integration tests.
- Follow existing coding standards and naming conventions.

---

# Out of Scope

The following features are not part of this implementation:

- Editing payments.
- Deleting payments.
- Payment reversal.
- Automatic late fees.
- Automatic interest recalculation.
- Loan renegotiation.
- Payment receipts.
- Financial reports.