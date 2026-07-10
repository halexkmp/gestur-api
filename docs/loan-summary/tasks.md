# Implementation Tasks - Get Loan Summary

## Phase 1 - Infrastructure
- [x] Create `GetLoanSummaryRepository` in `app/slices/partner_loan/get_loan_summary/infra/repository.py`
- [x] Implement `get_loan_with_details` using Tortoise ORM's `.prefetch_related("partner", "installments__payments")`

## Phase 2 - Application
- [x] Create `GetLoanSummary` Use Case in `app/slices/partner_loan/get_loan_summary/application/use_case.py`
- [x] Define explicit DTOs (`PaymentSummaryDTO`, `InstallmentSummaryDTO`, `LoanSummaryDTO`)
- [x] Implement sorting logic (installments by number ASC, payments by date ASC)
- [x] Implement financial tallies & calculated values logic
- [x] Validate loan existence, throwing ValueError on missing records

## Phase 3 - UI
- [x] Create Pydantic response schemas in `app/slices/partner_loan/get_loan_summary/ui/schemas.py`
- [x] Create FastAPI route and dependency injection in `app/slices/partner_loan/get_loan_summary/ui/route.py`
- [x] Register new router inside `app/slices/partner_loan/urls.py`

## Phase 4 - Documentation
- [x] Create `docs/loan-summary/plan.md` with approved plan
- [x] Create `docs/loan-summary/tasks.md` with complete checkbox items
