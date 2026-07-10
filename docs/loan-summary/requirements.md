# Feature Requirements

# Feature

Get Loan Summary

---

# Objective

Provide a read-only endpoint that returns the complete summary of a loan by its identifier.

The endpoint is intended to support customer-facing reports by returning all information related to the loan in a single response.

The response must consolidate:

- Loan information
- Borrower information
- Installment schedule
- Payment history for each installment
- Calculated financial totals

The endpoint must be optimized to avoid multiple client requests.

---

# User Story

## US-01 - Retrieve Loan Summary

As a client application,

I want to retrieve the complete summary of a loan,

So that I can generate a complete report containing the loan history.

### Acceptance Criteria

- The endpoint returns the complete loan summary.
- The endpoint requires only the loan identifier.
- The endpoint returns all installments.
- Each installment contains its payment history.
- The response is ordered and ready for report generation.
- No additional API requests are required.

---

# Functional Requirements

## FR-01

Create a new endpoint.

```
GET /loans/{loan_id}/summary
```

---

## FR-02

The endpoint must retrieve the loan identified by `loan_id`.

If the loan does not exist, return:

```
404 Not Found
```

---

## FR-03

The response must include the complete loan information.

At minimum:

- Loan identifier
- Partner identifier
- Partner name
- Principal amount
- Interest rate
- Total amount
- Total installments
- Due weekday
- Start date
- End date
- Loan status
- Creation date

---

## FR-04

The response must include every installment belonging to the loan.

Each installment must include:

- Installment identifier
- Installment number
- Original amount
- Due date
- Installment status
- Final payment date (if fully paid)

Installments must be ordered by installment number.

---

## FR-05

Each installment must include every registered payment.

Each payment must include:

- Payment identifier
- Amount
- Payment date
- Notes (when available)

Payments must be ordered chronologically.

---

## FR-06

The response must include calculated financial information.

The backend must calculate:

- Total amount paid
- Remaining balance
- Total number of payments
- Paid installments
- Partially paid installments
- Pending installments

These values must be calculated during request execution.

---

# Business Rules

## Loan Validation

The loan must exist.

Otherwise:

```
404 Not Found
```

---

## Ordering

Installments:

```
installment_number ASC
```

Payments:

```
payment_date ASC
```

---

## Read Only

The endpoint must not modify any data.

No business state may change during execution.

---

## Calculated Values

The following values must be derived from the payment history.

### Total Paid

The sum of every payment registered for every installment.

### Remaining Balance

Loan total amount minus total paid.

### Installment Counters

The backend must calculate:

- Paid installments
- Partially paid installments
- Pending installments

The client must not calculate these values.

---

# Performance Requirements

The endpoint must retrieve the complete report efficiently.

The implementation should eagerly load:

- Partner
- Loan
- Installments
- Installment payments

Avoid N+1 queries.

The endpoint should execute using the minimum number of database queries possible.

---

# Non-Functional Requirements

- Follow the existing Vertical Slice Architecture.
- Use asynchronous database operations.
- Repository contains only persistence and data retrieval logic.
- Business calculations belong to the Application or Domain layer.
- Return strongly typed response models.
- Use Decimal for monetary values.
- Use UUID identifiers.
- Follow existing project naming conventions.
- Implement unit tests.
- Implement integration tests.

---

# Out of Scope

The following features are not part of this implementation:

- PDF generation.
- Excel export.
- Email delivery.
- Report customization.
- Printing.
- Editing loans.
- Editing installments.
- Editing payments.
- Loan renegotiation.