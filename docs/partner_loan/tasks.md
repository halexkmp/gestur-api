# Technical Tasks - Buggyman Loan Management

## Phase 1: Database Setup
- [x] T1.1: Add `LoanStatus` enum to `app/shared/db/enums.py`
- [x] T1.2: Define `Loan` model in `app/shared/db/models.py`
- [x] T1.3: Define `LoanInstallment` model in `app/shared/db/models.py`
- [x] T1.4: Generate and execute database migrations using Aerich

## Phase 2: Create Loan Slice (`POST /loans`)
- [x] T2.1: Create `app/slices/partner_loan/create_loan/` directory
- [x] T2.2: Implement `ui/schemas.py` with validation and responses
- [x] T2.3: Implement due date generation algorithm and partner check in `domain/rules.py`
- [x] T2.4: Implement `application/use_case.py` coordinating database transactions
- [x] T2.5: Implement `infra/repository.py` supporting transaction-safe saves
- [x] T2.6: Implement `ui/route.py` for endpoint exposure

## Phase 3: Retrieve, List & Update Loans
- [x] T3.1: Create and implement `get_loan` slice (UI, Application, Infra)
- [x] T3.2: Create and implement `list_loans` slice (UI, Application, Infra)
- [x] T3.3: Create and implement `update_loan` slice (UI, Application, Infra)

## Phase 4: Installment Management
- [x] T4.1: Create and implement `list_loan_installments` slice (UI, Application, Infra)
- [x] T4.2: Create and implement `pay_loan_installment` slice (UI, Application, Infra)

## Phase 5: Routing & URL Registration
- [x] T5.1: Create `app/slices/partner_loan/urls.py` router file
- [x] T5.2: Register `partner_loan_router` in `app/main.py`

## Phase 6: Testing & QA
- [x] T6.1: Write unit tests for due date generation and partner eligibility rules
- [x] T6.2: Write integration tests for all loan API endpoints
- [x] T6.3: Run all tests to ensure full correctness
