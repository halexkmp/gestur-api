---
sessionId: session-260704-185035-13ug
---

# Requirements

### Overview & Goals
The objective is to implement the backend capability to register and retrieve one or more payments for a specific loan installment. This allows supporting partial payments, where an installment status progresses from `PENDING` to `PARTIALLY_PAID` and finally `PAID` as multiple payments accumulate. Each payment is permanently recorded for financial history and auditability.

### Scope
- **In Scope:**
  - Database schema changes including a new `LoanInstallmentStatus` enum and `LoanInstallmentPayment` table.
  - Refactoring existing files referencing `paid` to maintain project consistency and prevent compilation errors.
  - Implementation of a granular `register_payment` slice for `POST /loan-installments/{installment_id}/payments`.
  - Implementation of a granular `list_payments` slice for `GET /loan-installments/{installment_id}/payments`.
  - Transaction-safe updates of payments and parent installment status.
  - Comprehensive unit and integration tests.
  - Generation of `plan.md` and `tasks.md` documentation in `docs/installment_payments/`.

- **Out of Scope:**
  - Editing, deleting, or reversing payments.
  - Automatic late fees or interest recalculation.
  - Loan renegotiation, payment receipts, or financial reports.

### User Stories
- **As a system operator**, I want to register a payment of any positive amount up to the remaining balance for an installment so that partners can perform partial payments.
- **As a manager**, I want to list all registered payments of an installment ordered by date so that I have a reliable financial audit trail.

### Functional Requirements
- **Validation:**
  - Installment must exist.
  - Payment amount must be greater than zero.
  - Payment amount cannot exceed the remaining balance.
  - Payment date is required.
- **Status Rules:**
  - `PENDING`: Total paid amount is zero.
  - `PARTIALLY_PAID`: Total paid amount > 0 and < installment amount.
  - `PAID`: Total paid amount == installment amount.
- **Derived Values:**
  - `Total Paid` = sum of payment amounts.
  - `Remaining Balance` = installment amount - total paid.
- **Final payment date:**
  - Set installment `payment_date` to the date of the final payment when `PAID`. Otherwise, it remains `null`.

# Technical Design

### Current Implementation
- Slices reside under `app/slices/partner_loan/`.
- `LoanInstallment` model uses `paid: bool` and has references across multiple existing slices (`create_loan`, `get_loan`, `list_loan_installments`, `pay_loan_installment`).

### Key Decisions
- **Granular Feature Slices:** Implement two dedicated slices under `app/slices/partner_loan/`: `register_payment` and `list_payments`. This maintains consistency with the existing codebase structure where each use case is a single business action.
- **Model Evolution:** Replace `paid` with `status: CharEnumField` on `LoanInstallment` to support `PARTIALLY_PAID`.
- **Backward Compatibility:** Update existing slices referring to `paid` to use `status` instead, keeping `pay_loan_installment` compatible.
- **Transaction Safety:** Wrap payment registration, status recalculation, and installment update inside an atomic database transaction.

### Proposed Changes

#### 1. Enums & Database Models
- Update `app/shared/db/enums.py`:
  ```python
  class LoanInstallmentStatus(str, Enum):
      PENDING = "PENDING"
      PARTIALLY_PAID = "PARTIALLY_PAID"
      PAID = "PAID"
  ```
- Update `app/shared/db/models.py`:
  - `LoanInstallment` updates:
    ```python
    status = fields.CharEnumField(LoanInstallmentStatus, default=LoanInstallmentStatus.PENDING)
    ``` (remove `paid = fields.BooleanField(default=False)`)
  - Create new model:
    ```python
    class LoanInstallmentPayment(models.Model):
        id = fields.UUIDField(pk=True)
        loan_installment = fields.ForeignKeyField("models.LoanInstallment", related_name="payments")
        amount = fields.DecimalField(max_digits=10, decimal_places=2)
        payment_date = fields.DateField()
        notes = fields.TextField(null=True)
        created_at = fields.DatetimeField(auto_now_add=True)
        updated_at = fields.DatetimeField(auto_now=True)

        class Meta:
            table = "loan_installment_payment"
    ```

#### 2. Adapting Existing Slices
- `create_loan/application/use_case.py`: Instantiate `LoanInstallment` with `status=LoanInstallmentStatus.PENDING`.
- `get_loan` and `list_loan_installments` schemas: Update `paid: bool` to `status: LoanInstallmentStatus`.
- `pay_loan_installment/application/use_case.py`: Set `status = LoanInstallmentStatus.PAID` and `payment_date` (for compatibility with the direct pay API).

#### 3. New Slice: `register_payment`
- **Use Case Steps:**
  - Load the installment and its payments inside a transaction block.
  - Calculate `total_paid = sum(payments)`.
  - Validate payment amount > 0 and <= remaining balance (`installment.amount - total_paid`).
  - Persist `LoanInstallmentPayment`.
  - Update `installment.status` (either `PARTIALLY_PAID` or `PAID`).
  - If status becomes `PAID`, set `installment.payment_date = payment_date`.

#### 4. New Slice: `list_payments`
- Retrieve payments filtered by `loan_installment_id` and order by `payment_date`.

### Architecture Diagram
```mermaid
graph TD
    Client[HTTP Client] -->|POST /loan-installments/{id}/payments| UI[ui/route.py]
    UI -->|1. Validate schemas.py| UI
    UI -->|2. Invoke execute| App[application/use_case.py]
    
    subgraph Transaction Block [DB Transaction]
        App -->|3. Get installment & payments| Repo[infra/repository.py]
        Repo -->|Query payments & installment| DB[(Database)]
        
        App -->|4. Validate amount & remaining balance| App
        
        App -->|5. Create payment & update status| Repo
        Repo -->|Insert payment & Update installment| DB
    end
    
    App -->|6. Return Payment & Updated Installment| UI
    UI -->|7. JSON HTTP Response| Client
```

### File Structure
The following folders and files will be added/modified:
```text
app/
  shared/
    db/
      enums.py (modified)
      models.py (modified)
  slices/
    partner_loan/
      create_loan/
        application/
          use_case.py (modified)
      get_loan/
        ui/
          schemas.py (modified)
      list_loan_installments/
        ui/
          schemas.py (modified)
      pay_loan_installment/
        application/
          use_case.py (modified)
      register_payment/ (new feature slice)
        application/
          use_case.py
        infra/
          repository.py
        ui/
          route.py
          schemas.py
      list_payments/ (new feature slice)
        application/
          use_case.py
        infra/
          repository.py
        ui/
          route.py
          schemas.py
      urls.py (modified)
docs/
  installment_payments/
    plan.md (new)
    tasks.md (new)
```

# Plan & Tasks Files (Docs)

Below are the contents for `plan.md` and `tasks.md` to be placed inside `docs/installment_payments/`.

### `docs/installment_payments/plan.md`
```markdown

# Implementation Plan - Loan Installment Payments

This plan describes the technical steps to implement the Loan Installment Payments system, supporting partial payments, status recalculations, and transaction-safe operations.

## 1. Database & Foundation Layer
- **DB-1: Enum Update**
  - Add `LoanInstallmentStatus` enum with values `PENDING`, `PARTIALLY_PAID`, `PAID` to `app/shared/db/enums.py`.
- **DB-2: Model Modifications**
  - Update `LoanInstallment` model in `app/shared/db/models.py`:
    - Remove `paid` boolean field.
    - Add `status` field of type `CharEnumField` with default `PENDING`.
  - Create `LoanInstallmentPayment` model in `app/shared/db/models.py`:
    - Define fields: `id` (UUID), `loan_installment` (ForeignKeyField to `LoanInstallment`), `amount` (Decimal), `payment_date` (Date), `notes` (TextField, nullable), `created_at` (Datetime), `updated_at` (Datetime).
- **DB-3: Existing Code Adaptation**
  - Update `create_loan/application/use_case.py` to instantiate installments with `status=LoanInstallmentStatus.PENDING` instead of `paid=False`.
  - Update response schemas in `get_loan` and `list_loan_installments` to return `status: LoanInstallmentStatus` instead of `paid: bool`.
  - Update `pay_loan_installment/application/use_case.py` to set `status=LoanInstallmentStatus.PAID` instead of `paid=True`.

## 2. Slice Implementation
We will implement two separate slices under `app/slices/partner_loan/`:

### Slice 1: Register Payment (`POST /loan-installments/{installment_id}/payments`)
- **UI Layer**
  - `ui/schemas.py`: Define `PaymentRegisterRequest` (amount, payment_date, notes) and `PaymentResponse` representing the registered payment.
  - `ui/route.py`: Receive request, authorize using `get_current_user`, invoke use case, translate errors.
- **Application Layer**
  - `application/use_case.py`: Load installment, validate, execute transaction-safe logic:
    1. Check remaining balance: `installment.amount - sum(existing_payments)`.
    2. Ensure `payment_amount <= remaining_balance`.
    3. Persist the `LoanInstallmentPayment`.
    4. Recalculate status and update installment's `status` and `payment_date`.
- **Infrastructure Layer**
  - `infra/repository.py`: Get installment, compute sum of existing payments, save payment and installment inside a transaction block.

### Slice 2: List Payments (`GET /loan-installments/{installment_id}/payments`)
- **UI Layer**
  - `ui/route.py`: Expose the list endpoint, authorize, invoke use case.
  - `ui/schemas.py`: Return list of `PaymentResponse` schemas.
- **Application Layer**
  - `application/use_case.py`: Load and return all payments for a given installment.
- **Infrastructure Layer**
  - `infra/repository.py`: Retrieve payments ordered by `payment_date`.

## 3. Route Registration
- Include `register_payment` and `list_payments` routers in `app/slices/partner_loan/urls.py` under the `/loan-installments` prefix.

## 4. Verification & Testing
- Implement unit tests for the use cases and business rules (validation of zero amount, remaining balance overrun).
- Implement integration tests using `pytest` and `httpx.AsyncClient` to verify endpoints.
```

### `docs/installment_payments/tasks.md`
```markdown

# Technical Tasks - Loan Installment Payments

## Phase 1: Database Setup
- [ ] T1.1: Add `LoanInstallmentStatus` enum to `app/shared/db/enums.py`
- [ ] T1.2: Update `LoanInstallment` model in `app/shared/db/models.py` by removing `paid` and adding `status`
- [ ] T1.3: Define `LoanInstallmentPayment` model in `app/shared/db/models.py`
- [ ] T1.4: Update existing references to `paid` in `create_loan` use case
- [ ] T1.5: Update existing schemas in `get_loan` and `list_loan_installments` to return `status`
- [ ] T1.6: Update existing references to `paid` in `pay_loan_installment` for backwards compatibility

## Phase 2: Register Payment Slice (`POST /loan-installments/{installment_id}/payments`)
- [ ] T2.1: Create `app/slices/partner_loan/register_payment/` directory
- [ ] T2.2: Implement `ui/schemas.py` with validation and response formats
- [ ] T2.3: Implement `infra/repository.py` with atomic transactional operations
- [ ] T2.4: Implement `application/use_case.py` containing core payment validation and status update rules
- [ ] T2.5: Implement `ui/route.py` for endpoint exposure

## Phase 3: List Payments Slice (`GET /loan-installments/{installment_id}/payments`)
- [ ] T3.1: Create `app/slices/partner_loan/list_payments/` directory
- [ ] T3.2: Implement `infra/repository.py` to retrieve payments sorted by date
- [ ] T3.3: Implement `application/use_case.py` for fetching payment history
- [ ] T3.4: Implement `ui/route.py` for endpoint exposure

## Phase 4: Routing & Integration
- [ ] T4.1: Register new routers in `app/slices/partner_loan/urls.py` under the `installments_router`

## Phase 5: Testing & QA
- [ ] T5.1: Write unit tests validating payment rules (payment amount > 0, payment exceeding remaining balance)
- [ ] T5.2: Write integration tests for POST and GET payment endpoints
- [ ] T5.3: Verify all test cases pass successfully
```

# Testing

### Validation Approach
Verification of the new implementation will utilize automated pytest suites to validate behavior under various scenarios, following existing testing conventions.

### Key Scenarios
- **First Partial Payment:**
  - Register payment for less than the installment amount.
  - Verify payment is saved, installment status is updated to `PARTIALLY_PAID`, and payment_date remains `null`.
- **Second Final Payment:**
  - Register payment for the exact remaining balance of the installment.
  - Verify payment is saved, installment status becomes `PAID`, and payment_date is set to the final payment's date.
- **Overpayment Prevention:**
  - Attempt to register a payment exceeding the remaining balance.
  - Verify the API rejects with a `400 Bad Request` / `ValueError` and rolls back any database operations.
- **Negative Payment Amount:**
  - Attempt to register a payment with a negative or zero amount.
  - Verify request-level schemas reject the input.
- **List Payments:**
  - Register multiple payments.
  - Fetch history and verify list contains all payments ordered chronologically by payment date.

# Delivery Steps

### ✓ Step 1: database-setup-and-models-migration
The database and existing code are prepared to use the new installment status Enum and the payments history table.

- Add `LoanInstallmentStatus` enum to `app/shared/db/enums.py`.
- Update `LoanInstallment` model in `app/shared/db/models.py` by replacing `paid` with `status`.
- Add `LoanInstallmentPayment` model in `app/shared/db/models.py`.
- Update references to `paid` in `create_loan` use case and response schemas for `get_loan` and `list_loan_installments`.
- Refactor `pay_loan_installment` use case to use `status` instead of `paid` for backwards compatibility.

### ✓ Step 2: implement-register-payment-slice
The register payment POST endpoint is fully implemented with validation and status recalculation logic.

- Create `app/slices/partner_loan/register_payment` directory.
- Define request and response schemas in `ui/schemas.py`.
- Create transaction-safe save and validation logic in `application/use_case.py`.
- Implement persistence methods in `infra/repository.py`.
- Implement FastAPI route handler in `ui/route.py`.

### ✓ Step 3: implement-list-payments-slice-and-routing
The payment history GET endpoint is implemented and all routes are integrated in the application router.

- Create `app/slices/partner_loan/list_payments` directory.
- Define payment history response schemas in `ui/schemas.py`.
- Implement query operations in `infra/repository.py` to retrieve payments ordered by payment date.
- Implement business logic in `application/use_case.py`.
- Implement FastAPI route handler in `ui/route.py`.
- Register both new routers in `app/slices/partner_loan/urls.py`.

### ✓ Step 4: create-docs-and-add-testing
Unit and integration tests are added, and the project documentation is completed.

- Write unit tests validating payment amount limits and status progression logic.
- Write integration tests for GET and POST payment endpoints.
- Create `docs/installment_payments/plan.md` with technical design details.
- Create `docs/installment_payments/tasks.md` with granular checklist tasks.