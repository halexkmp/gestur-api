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
