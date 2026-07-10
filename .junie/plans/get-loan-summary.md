---
sessionId: session-260710-114243-6oi5
---

# Requirements

### Overview & Goals
Provide a read-only endpoint `GET /loans/{loan_id}/summary` that aggregates and returns a comprehensive summary of a loan by its unique identifier in a single API call. This report consolidates the core loan details, borrower (partner) information, installment schedule, full chronological payment history per installment, and real-time calculated financial metrics.

### Scope
- **In Scope**:
  - A new FastAPI route under the `partner_loan` slice at `GET /loans/{loan_id}/summary`.
  - Simple authentication dependency using `get_current_user`.
  - Database retrieval utilizing Tortoise ORM prefetching of related `partner`, `installments`, and nested `payments` to prevent N+1 queries.
  - Sorting logic: Installments sorted by `installment_number ASC`, and payments of each installment sorted by `payment_date ASC`.
  - Calculation of financial summary metrics (Total Paid, Remaining Balance, Total Payments Count, counters for Paid/Partially Paid/Pending installments) computed dynamically during execution.
  - Custom typed data objects (DTOs) for passing data out of the Application layer to adhere to the rule prohibiting generic dictionaries crossing layers.
  - Update `app/slices/partner_loan/urls.py` to route the new endpoint.
  - Drafts of documentation files `docs/loan-summary/plan.md` and `docs/loan-summary/tasks.md`.
- **Out of Scope**:
  - File generation (PDF, Excel, etc.).
  - Email sending or printing.
  - Modification of any database records (Read-Only).

### Functional Requirements
- **FR-01**: Access via `GET /loans/{loan_id}/summary`.
- **FR-02**: Returns `404 Not Found` if the loan does not exist.
- **FR-03**: Includes core loan details, including partner name and id.
- **FR-04**: Returns all installments, ordered by `installment_number ASC`, including payment date.
- **FR-05**: Returns all payments per installment, ordered by `payment_date ASC`.
- **FR-06**: Calculates financial summaries (Total paid, Remaining balance, total payment count, installment status counters).

# Technical Design

### Current Implementation
- Slices live in `app/slices/`.
- Loan slices live under `app/slices/partner_loan/`.
- Router routing is defined in `app/slices/partner_loan/urls.py` which aggregates routes for `/loans` and `/loan-installments`.
- `Loan`, `LoanInstallment`, and `LoanInstallmentPayment` models are defined in `app/shared/db/models.py`.

### Key Decisions
1. **Vertical Slice Folder Structure**: Create the folder `app/slices/partner_loan/get_loan_summary/` with standard `application/`, `infra/`, and `ui/` sub-folders.
2. **DTOs Over Generic Dicts**: To satisfy the non-negotiable architectural constraint "No generic dictionaries (`dict`) cross architectural layers", define explicit DTO classes (`LoanSummaryDTO`, `InstallmentSummaryDTO`, `PaymentSummaryDTO`) in the Application layer.
3. **Eager Nest Prefetching**: Use Tortoise ORM's `.prefetch_related("partner", "installments__payments")` to query all required records in a highly optimized manner, preventing any N+1 database queries.
4. **Calculations in Application Layer**: All financial metrics will be calculated in `GetLoanSummary.execute()` to keep business rules out of the database and UI layers.

### File Structure
The new slice will be structured as:
```text
app/slices/partner_loan/get_loan_summary/
    application/
        use_case.py
    ui/
        route.py
        schemas.py
    infra/
        repository.py
```

### Components Interaction Diagram
```mermaid
graph TD
    Client[Client App] -->|GET /loans/{loan_id}/summary| Route[ui/route.py]
    Route -->|GetLoanSummary.execute(loan_id)| UseCase[application/use_case.py]
    UseCase -->|get_loan_with_details(loan_id)| Repository[infra/repository.py]
    Repository -->|Query with prefetch| DB[(Database)]
    DB -->|Loan, Partner, Installments & Payments| Repository
    Repository -->|ORM Models| UseCase
    UseCase -->|Sorts, Tallies & Calculates Metrics| UseCase
    UseCase -->|LoanSummaryDTO| Route
    Route -->|Serialized LoanSummaryResponse| Client
```

### Data Contracts
**Pydantic schemas (`ui/schemas.py`)**:
```python
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from app.shared.db.enums import LoanStatus, LoanInstallmentStatus

class PaymentSummaryResponse(BaseModel):
    id: UUID
    amount: Decimal
    payment_date: date
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class InstallmentSummaryResponse(BaseModel):
    id: UUID
    installment_number: int
    amount: Decimal
    due_date: date
    status: LoanInstallmentStatus
    payment_date: Optional[date] = None
    payments: list[PaymentSummaryResponse]

    class Config:
        from_attributes = True

class LoanSummaryResponse(BaseModel):
    id: UUID
    partner_id: UUID
    partner_name: str
    principal_amount: Decimal
    interest_rate: Decimal
    total_amount: Decimal
    installments_qty: int
    due_weekday: str
    start_date: date
    end_date: date
    status: LoanStatus
    created_at: datetime
    total_paid: Decimal
    remaining_balance: Decimal
    total_payments: int
    paid_installments: int
    partially_paid_installments: int
    pending_installments: int
    installments: list[InstallmentSummaryResponse]

    class Config:
        from_attributes = True
```

### Risks & Mitigations
- **Incorrect Orderings**: If installments or payments are loaded out of order, it can invalidate report reports.
  - *Mitigation*: Explicitly sort Python lists in the application layer using `sorted(..., key=...)` before returning the response.
- **Null Fields**: `notes` or `payment_date` could be missing.
  - *Mitigation*: Ensure schema definitions allow `Optional` values with a `None` default.

# Documentation Drafts

Here are the draft Markdown files to be created under `docs/loan-summary/` for alignment with the mandatory workflow guidelines:

#### 1. Draft for `docs/loan-summary/plan.md`
```markdown

# Technical Plan - Get Loan Summary

## Technical Approach
Implement a new vertical slice under `app/slices/partner_loan/get_loan_summary/` to implement the `GET /loans/{loan_id}/summary` endpoint. Eager-load all associations (Partner, Installments, Payments) in a single optimized query using nested prefetching. Explicitly sort results and calculate financial metrics in the Application layer, mapping output to strongly-typed DTOs to satisfy layered boundaries.

## Architectural Decisions
1. **Vertical Slice**: Standardize with application, ui, and infra layers.
2. **DTO Mapping**: Avoid generic dictionaries crossing layers.
3. **Tortoise Prefetching**: Use `partner` and `installments__payments` relation strings.

## Database Changes
None required.

## API Changes
Add `GET /loans/{loan_id}/summary` return contract `LoanSummaryResponse`.

## Validation Strategy
Handle nonexistent loan IDs with a explicit `ValueError` that translates to a `404 Not Found` HTTP response in the UI layer. Ensure decimal rounding to 2 decimal places.
```

#### 2. Draft for `docs/loan-summary/tasks.md`
```markdown

# Implementation Tasks - Get Loan Summary

## Phase 1 - Infrastructure
- [ ] Create `GetLoanSummaryRepository` in `app/slices/partner_loan/get_loan_summary/infra/repository.py`
- [ ] Implement `get_loan_with_details` using Tortoise ORM's `.prefetch_related("partner", "installments__payments")`

## Phase 2 - Application
- [ ] Create `GetLoanSummary` Use Case in `app/slices/partner_loan/get_loan_summary/application/use_case.py`
- [ ] Define explicit DTOs (`PaymentSummaryDTO`, `InstallmentSummaryDTO`, `LoanSummaryDTO`)
- [ ] Implement sorting logic (installments by number ASC, payments by date ASC)
- [ ] Implement financial tallies & calculated values logic
- [ ] Validate loan existence, throwing ValueError on missing records

## Phase 3 - UI
- [ ] Create Pydantic response schemas in `app/slices/partner_loan/get_loan_summary/ui/schemas.py`
- [ ] Create FastAPI route and dependency injection in `app/slices/partner_loan/get_loan_summary/ui/route.py`
- [ ] Register new router inside `app/slices/partner_loan/urls.py`

## Phase 4 - Documentation
- [ ] Create `docs/loan-summary/plan.md` with approved plan
- [ ] Create `docs/loan-summary/tasks.md` with complete checkbox items
```

# Delivery Steps

### ✓ Step 1: Implement Infrastructure Repository and Application DTOs
GetLoanSummaryRepository retrieves a complete, eager-loaded Loan entity, and Application DTOs are declared.

- Create `GetLoanSummaryRepository` class in `app/slices/partner_loan/get_loan_summary/infra/repository.py`.
- Define `get_loan_with_details` utilizing Tortoise ORM's nested prefetching via `.prefetch_related("partner", "installments__payments")`.
- Implement `PaymentSummaryDTO`, `InstallmentSummaryDTO`, and `LoanSummaryDTO` in `app/slices/partner_loan/get_loan_summary/application/use_case.py` to keep data boundaries explicit.

### ✓ Step 2: Implement Use Case Calculations and Sorting Logic
GetLoanSummary use case processes the eager-loaded data, performs financial calculations, and sorts installments/payments.

- Implement `GetLoanSummary.execute(loan_id)` in `app/slices/partner_loan/get_loan_summary/application/use_case.py`.
- Sort installments by `installment_number ASC` and their corresponding payments by `payment_date ASC`.
- Calculate metrics dynamically: total paid, remaining balance, total payment count, and counters for PAID, PARTIALLY_PAID, and PENDING statuses.
- Handle missing loan IDs by throwing a standard `ValueError("Loan not found")`.

### ✓ Step 3: Implement UI Schemas, Route, and Router Registration
The FastAPI route is exposed at GET /loans/{loan_id}/summary, returning fully serialized and validated responses.

- Create `PaymentSummaryResponse`, `InstallmentSummaryResponse`, and `LoanSummaryResponse` in `app/slices/partner_loan/get_loan_summary/ui/schemas.py`.
- Create the route handler in `app/slices/partner_loan/get_loan_summary/ui/route.py` using `Depends(get_current_user)` for security.
- Map the standard `ValueError` exception to an `HTTPException(status_code=404, detail="Loan not found")`.
- Register the route under the existing `loans_router` inside `app/slices/partner_loan/urls.py`.