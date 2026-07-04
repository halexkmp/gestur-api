# Technical Tasks - Loan Installment Payments

## Phase 1: Database Setup
- [x] T1.1: Add `LoanInstallmentStatus` enum to `app/shared/db/enums.py`
- [x] T1.2: Update `LoanInstallment` model in `app/shared/db/models.py` by removing `paid` and adding `status`
- [x] T1.3: Define `LoanInstallmentPayment` model in `app/shared/db/models.py`
- [x] T1.4: Update existing references to `paid` in `create_loan` use case
- [x] T1.5: Update existing schemas in `get_loan` and `list_loan_installments` to return `status`
- [x] T1.6: Update existing references to `paid` in `pay_loan_installment` for backwards compatibility

## Phase 2: Register Payment Slice (`POST /loan-installments/{installment_id}/payments`)
- [x] T2.1: Create `app/slices/partner_loan/register_payment/` directory
- [x] T2.2: Implement `ui/schemas.py` with validation and response formats
- [x] T2.3: Implement `infra/repository.py` with atomic transactional operations
- [x] T2.4: Implement `application/use_case.py` containing core payment validation and status update rules
- [x] T2.5: Implement `ui/route.py` for endpoint exposure

## Phase 3: List Payments Slice (`GET /loan-installments/{installment_id}/payments`)
- [x] T3.1: Create `app/slices/partner_loan/list_payments/` directory
- [x] T3.2: Implement `infra/repository.py` to retrieve payments sorted by date
- [x] T3.3: Implement `application/use_case.py` for fetching payment history
- [x] T3.4: Implement `ui/route.py` for endpoint exposure

## Phase 4: Routing & Integration
- [x] T4.1: Register new routers in `app/slices/partner_loan/urls.py` under the `installments_router`

## Phase 5: Testing & QA
- [x] T5.1: Write unit tests validating payment rules (payment amount > 0, payment exceeding remaining balance)
- [x] T5.2: Write integration tests for POST and GET payment endpoints
- [x] T5.3: Verify all test cases pass successfully
