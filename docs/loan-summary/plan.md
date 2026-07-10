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
