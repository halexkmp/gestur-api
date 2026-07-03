# Implementation Plan - Buggyman Loan Management

This plan describes the technical steps to implement the Buggyman Loan Management backend system, ensuring adherence to the Vertical Slice Architecture guidelines.

## 1. Foundation & Database Layer
- **DB-1: Enum Update**
  - Add `LoanStatus` enum (`ACTIVE`, `PAID`, `CANCELED`) to `app/shared/db/enums.py`.
- **DB-2: Database Models**
  - Create `Loan` and `LoanInstallment` models in `app/shared/db/models.py`.
  - Configure relationships: `Loan` references `Partner`, `LoanInstallment` references `Loan`.
- **DB-3: Migrations**
  - Generate and run database migrations using Aerich.

## 2. Slice Implementation
Group all feature slices under the new context directory `app/slices/partner_loan/`.

### Slice 1: Create Loan (`POST /loans`)
- **UI Layer**
  - `ui/schemas.py`: Define `LoanCreateRequest` with strict Pydantic validations (`principal_amount > 0`, `due_day` between 1 and 28, etc., with `total_amount` removed since it's calculated internally) and `LoanResponse`.
  - `ui/route.py`: Receive request, call use case, return response.
- **Application Layer**
  - `application/use_case.py`: Load partner, validate eligibility, calculate total amount, execute rules, start database transaction, persist loan and installments.
- **Domain Layer**
  - `domain/rules.py`: Implement due date generator helper and partner eligibility checks. Includes `calculate_total_amount` logic: `total_amount = round(principal_amount * (1 + interest_rate / 100), 2)`.

### Slice 2: Retrieve & List Loans (`GET /loans/{loan_id}`, `GET /loans`)
- **Get Loan Slice**
  - Retrieve details of a single loan.
- **List Loans Slice**
  - Query and return all loans in the database.

### Slice 3: Update Loan Metadata (`PUT /loans/{loan_id}`)
- Update fields like `principal_amount`, `interest_rate`, and dates (with `total_amount` recalculated and updated if principal or interest rate is updated), while leaving generated installments unchanged.

### Slice 4: List Loan Installments (`GET /loans/{loan_id}/installments`)
- Fetch and display all installments associated with the given loan, ordered sequentially by `installment_number`.

### Slice 5: Pay Installment (`POST /loan-installments/{installment_id}/pay`)
- Mark a specific installment as paid, updating `paid = True` and filling `payment_date`.

## 3. Route Registration
- Define routing in `app/slices/partner_loan/urls.py`.
- Include the `partner_loan_router` inside `app/main.py`.

## 4. Verification & Testing
- Write and execute unit and integration tests under `tests/partner_loan/`.
- Ensure all business rules (partner type, invalid due days, transactional rollback) are validated.
