# Feature Requirements

## Feature

Buggyman Loan Management

---

# Objective

Implement a loan management feature for partners whose `partner_type` is `BUGGYMAN`.

The feature must allow the system to register loans, automatically generate installments, and track payment status.

This feature is backend-only and will be exposed through the existing Python API.

---

# Business Rules

## Loan Eligibility

- Only partners with `partner_type = BUGGYMAN` can receive loans.
- Validation must occur before creating a loan.

---

## Loan

A loan contains:

- Loan start date
- Loan end date
- Principal amount
- Interest rate (percentage)
- Total amount to be repaid
- Total number of installments
- Due day (1-28)
- Associated Buggyman (Partner)

---

## Installments

When a loan is created:

- The API must automatically generate all installments.
- One database record must be created per installment.
- Installments must be sequentially numbered starting from 1.

Each installment contains:

- Installment number
- Installment amount
- Due date
- Payment date (nullable)
- Paid flag
- Loan reference

---

## Due Date Generation

The user informs:

- Start date
- Due day
- Number of installments

The system generates installment due dates using the provided due day.

Example:

Loan Start:
2026-01-15

Due Day:
10

Installments:
3

Generated Due Dates:

1. 2026-02-10
2. 2026-03-10
3. 2026-04-10

If the due day does not exist in a month (e.g. 31st), the due date should become the last valid day of that month.

---

## Payment

Each installment may be marked as paid.

When paid:

- payment_date is filled
- paid = true

Otherwise:

- payment_date remains null
- paid = false

---

# Data Model

## Loan

| Field | Type |
|--------|------|
| id | UUID |
| partner_id | UUID (FK Partner) |
| principal_amount | Decimal |
| interest_rate | Decimal |
| total_amount | Decimal |
| installments | Integer |
| due_day | Integer |
| start_date | Date |
| end_date | Date |
| status | Enum |
| created_at | Datetime |
| updated_at | Datetime |

---

## LoanInstallment

| Field | Type |
|--------|------|
| id | UUID |
| loan_id | UUID (FK Loan) |
| installment_number | Integer |
| amount | Decimal |
| due_date | Date |
| payment_date | Date (nullable) |
| paid | Boolean |
| created_at | Datetime |
| updated_at | Datetime |

---

# Validation Rules

- Partner must exist.
- Partner must be a BUGGYMAN.
- Principal amount must be greater than zero.
- Interest rate cannot be negative.
- Total amount must be greater than zero.
- Installments must be greater than zero.
- Due day must be between 1 and 28 (recommended to avoid invalid dates).
- End date cannot be before start date.

---

# API Requirements

The feature must expose endpoints to:

- Create a loan
- Retrieve a loan
- List loans
- Update loan information (excluding generated installments)
- List loan installments
- Mark an installment as paid

---

# Automatic Behavior

On loan creation:

1. Validate partner.
2. Persist loan.
3. Generate all installments.
4. Persist installments inside the same database transaction.

If any step fails, the transaction must be rolled back.

---

# Non-Functional Requirements

- Follow existing project architecture.
- Use asynchronous database operations.
- Keep business logic inside the service layer.
- Database operations must be transactional.
- Use UUIDs for identifiers.
- Use Decimal for monetary values.
- Implement unit and integration tests.
- Follow existing coding standards and naming conventions.