# Feature Specification: Salary Summary for All Employees

**Feature Branch**: `006-salary-summary-all-employees`

**Created**: 2026-07-25

**Status**: Draft

**Input**: User description: "change the salary summary endpoint to receive only the month and year, not the employee anymore. This endpoint will return for all employees. Also, add on response the salary advances filter by year and month."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - HR reviews salary summaries for every employee at once (Priority: P1)

An HR user wants the salary summary (gross salary, advances, lateness deductions, net salary) for a given month and year, for the whole company at once, instead of requesting it one employee at a time.

**Why this priority**: This is the core change requested — moving from a single-employee lookup to a company-wide report is the entire point of the feature. Without it, there is no feature.

**Independent Test**: Can be fully tested by calling the salary summary endpoint with only a month and year (no employee identifier) and verifying the response contains one summary entry per employee in the system.

**Acceptance Scenarios**:

1. **Given** the company has multiple employees, **When** HR requests the salary summary for a specific month and year, **Then** the response contains one salary summary entry for every employee, each with gross salary, advances total, late delay minutes, late days count, late deduction total, and net salary for that period.
2. **Given** HR does not supply a month or year, **When** the request is made, **Then** the system defaults to the current month and year, same as the previous single-employee behavior.
3. **Given** a non-HR user, **When** they call this endpoint, **Then** the request is denied, same as the previous single-employee behavior.

---

### User Story 2 - HR sees itemized salary advances alongside each summary (Priority: P2)

An HR user reviewing a summary wants to see the individual salary advance records that make up an employee's "advances total" for the requested month and year, without making a separate request per employee.

**Why this priority**: This enriches the P1 report with the itemized detail HR needs to explain or audit the advances total; it depends on P1 existing first but is independently verifiable once P1 is in place.

**Independent Test**: Can be fully tested by giving an employee one or more salary advances dated within the requested month/year (and, separately, one dated outside it) and confirming the response's advances list contains only the in-period records and that they sum to the reported advances total.

**Acceptance Scenarios**:

1. **Given** an employee has salary advances recorded in the requested month and year, **When** HR requests the summary, **Then** that employee's entry includes the list of those advances (amount, date, and note) alongside the existing advances total.
2. **Given** an employee has a salary advance recorded outside the requested month and year, **When** HR requests the summary for that month and year, **Then** that advance does not appear in the returned list.
3. **Given** an employee has no salary advances in the requested month and year, **When** HR requests the summary, **Then** that employee's advances list is empty and the advances total is zero.

---

### Edge Cases

- What happens when there are no employees registered at all? The response is an empty list rather than an error.
- What happens for an employee with no linked user account? Lateness cannot be determined (no journey data to evaluate), so late delay minutes, late days count, and late deduction total are zero for that employee, consistent with current single-employee behavior.
- What happens for an inactive employee? They are still included in the report, consistent with the current single-employee endpoint not filtering by active status.
- What happens when the lateness configuration is disabled or missing? Late delay minutes, late days count, and late deduction total are zero for every employee, consistent with current behavior.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a salary summary report covering every employee for a single request, replacing the requirement to identify one employee per request.
- **FR-002**: System MUST accept an optional month and an optional year as the only filters for the report; when either is omitted, it MUST default to the current month and/or year.
- **FR-003**: System MUST no longer require or accept an employee identifier as an input to this report.
- **FR-004**: For each employee, the report MUST include the same computed fields as the previous single-employee summary: gross salary, advances total, late delay minutes, late days count, late deduction total, and net salary, all computed for the requested month and year.
- **FR-005**: For each employee, the report MUST additionally include the list of that employee's individual salary advances dated within the requested month and year.
- **FR-006**: The advances total reported for an employee MUST equal the sum of that employee's itemized advances list included in the same response.
- **FR-007**: Access to this report MUST remain restricted to users with HR permission, same as the previous single-employee endpoint.
- **FR-008**: System MUST return an empty report (no entries) when there are no employees, rather than an error.

### Key Entities *(include if feature involves data)*

- **Employee**: Existing entity; each report entry corresponds to one employee and their salary for the requested period.
- **Salary Advance**: Existing entity; the itemized list attached to each employee's report entry is the set of that employee's advances dated within the requested month and year.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: HR can obtain the full company's salary summary for a given month in a single request, eliminating the need for one request per employee.
- **SC-002**: For a company with 100 employees, HR retrieves the complete month's salary report (including itemized advances) in one call instead of 100 sequential calls.
- **SC-003**: 100% of the salary advances shown for an employee in the report fall within the requested month and year — none from other periods appear.
- **SC-004**: Every employee present in the system appears exactly once in the report for a given request.

## Assumptions

- The existing "my salary summary" self-service endpoint (an employee viewing their own summary) keeps its current behavior, route, and response shape unchanged by this feature — it continues to accept only month/year for the current authenticated employee. It currently reuses this feature's response schema via a cross-slice import; that import is removed as part of this change so each slice owns its own schema, but this is an internal-only touch with no effect on the endpoint's external contract (same path, same fields, same behavior).
- Inactive employees remain included in the report, matching the current single-employee endpoint's behavior of not filtering by active status.
- The report is not paginated; company size is assumed small enough (consistent with existing employee list endpoints) that returning all employees in one response is acceptable.
- No new sorting requirement was specified; entries may be returned in a stable, implementation-defined order.
