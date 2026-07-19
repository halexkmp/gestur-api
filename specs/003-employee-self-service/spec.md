# Feature Specification: Employee Self-Service Salary Access

**Feature Branch**: `003-employee-self-service`

**Created**: 2026-07-19

**Status**: Draft

**Input**: User description: "Employee self-service: add dedicated endpoints for the logged-in employee to view their own salary summary and salary advances, without requiring HR role. Two endpoints: GET /employees/me/salary-summary (equivalent to the existing HR-only GET /employees/salary-summary/{employee_id}, but scoped to the calling employee via their linked user account, taking month/year as optional query params) and GET /employees/me/salary-advances (equivalent to the existing HR-only GET /employees/salary-advances?employee_id=..., scoped to the calling employee, with optional month/year filters). Access is restricted to users with the Employee role who have a linked Employee record (via the existing User-Employee one-to-one link) — the employee_id is always derived from the authenticated user's token, never from a client-supplied parameter. If the calling user has no linked Employee record, the request is rejected rather than failing unexpectedly. Open question to resolve during spec: whether the self-service salary summary should include the lateness delay/deduction breakdown introduced by spec 002 (which currently restricts that detail to HR only), or omit/limit it for employee self-view."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Employee views their own salary summary (Priority: P1)

A logged-in employee opens their own monthly salary summary — gross salary, advances deducted, and net salary for a given month — without needing an HR user to look it up for them.

**Why this priority**: This is the core self-service value: employees currently have no way to see their own pay breakdown and must ask HR. It delivers standalone value even before salary-advance history is available self-service.

**Independent Test**: Log in as a user with the Employee role and a linked employee record, request the summary for a month with known salary/advance data, and verify the figures match what HR sees for the same employee/month via the existing HR endpoint.

**Acceptance Scenarios**:

1. **Given** a logged-in user with the Employee role and a linked employee record, **When** they request their salary summary for a month with recorded advances, **Then** the response shows their gross salary, total advances, and net salary for that month, matching the equivalent HR-facing view for the same employee.
2. **Given** no month/year is supplied, **When** the employee requests their salary summary, **Then** the system defaults to the current calendar month, consistent with the existing HR-facing salary summary endpoint's default behavior.
3. **Given** a logged-in user with the Employee role but no linked employee record, **When** they request the self-service salary summary, **Then** the request is rejected and no salary data is returned.
4. **Given** a logged-in user without the Employee role (e.g. HR, Manager, Admin, Operator), **When** they call the self-service salary summary endpoint, **Then** the request is rejected regardless of whether that user happens to also have a linked employee record.

---

### User Story 2 - Employee views their own salary advance history (Priority: P2)

A logged-in employee reviews the list of salary advances taken against their pay, optionally filtered to a specific month/year, without HR needing to pull the list on their behalf.

**Why this priority**: Complements User Story 1 — advances are already summarized in the salary summary total, but employees may want the itemized history (dates, amounts, notes). Slightly lower priority than the summary because the aggregate total is already visible once Story 1 ships.

**Independent Test**: Log in as an employee with known advances on record, request the self-service advances list (with and without month/year filters), and verify the returned items match the employee's own advances only.

**Acceptance Scenarios**:

1. **Given** a logged-in employee with one or more recorded salary advances, **When** they request their advance history with no filters, **Then** all of their own advances are returned and no other employee's advances appear.
2. **Given** a logged-in employee with advances spanning multiple months, **When** they request their advance history filtered to a specific month/year, **Then** only advances from that month/year are returned.
3. **Given** a logged-in employee with no recorded advances, **When** they request their advance history, **Then** an empty list is returned rather than an error.
4. **Given** a logged-in user with the Employee role but no linked employee record, **When** they request the self-service advance history, **Then** the request is rejected.

---

### Edge Cases

- Logged-in user has the Employee role but no linked employee record (e.g. an employee account created before being linked, or a role assigned without ever creating the employee record): both self-service endpoints reject the request rather than returning empty/null data or a server error.
- Logged-in user has a linked employee record but not the Employee role (e.g. an HR user who is also on payroll): self-service endpoints reject the request — these endpoints are gated on role, not merely on having a linked record.
- Employee requests a month/year with no salary-relevant activity at all: summary still returns (zero advances, zero deduction, net salary equal to gross), matching how the existing HR-facing summary already handles quiet months.
- Employee attempts to pass another employee's identifier to either endpoint: not possible by design — these endpoints never accept a client-supplied employee identifier; the employee is always resolved from the authenticated session.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a self-service endpoint for the authenticated employee to retrieve their own monthly salary summary, accepting optional month and year parameters and defaulting to the current month when omitted, consistent with the existing HR-facing salary summary's default behavior.
- **FR-002**: System MUST provide a self-service endpoint for the authenticated employee to retrieve their own salary advance history, accepting optional month and year filters.
- **FR-003**: Both self-service endpoints MUST resolve the employee whose data is returned exclusively from the authenticated user's own session/token — no client-supplied employee identifier MUST be accepted or honored by these endpoints.
- **FR-004**: Both self-service endpoints MUST be accessible only to authenticated users holding the Employee role.
- **FR-005**: Both self-service endpoints MUST reject requests from an authenticated Employee-role user who has no linked employee record, rather than returning empty, null, or default data.
- **FR-006**: The self-service salary summary MUST report the same gross salary, advances total, and net salary figures for the calling employee as the existing HR-facing salary summary would report for that same employee and month.
- **FR-007**: The self-service salary advance history MUST only ever return advances belonging to the calling employee, regardless of any parameters supplied.
- **FR-008**: The self-service salary summary MUST include the lateness delay/deduction breakdown (total delay minutes, late-days count, lateness deduction amount) for the calling employee's own data, applying the same system-wide lateness configuration and calculation rules already defined for the HR-facing salary summary.

### Key Entities

- **Employee** *(existing)*: The individual whose salary data is being viewed; resolved from the calling user's linked employee record rather than from a request parameter.
- **Salary Summary** *(existing, reused)*: An employee's monthly pay breakdown (gross salary, advances, lateness deduction, net salary); the self-service view surfaces the same data already defined for the HR-facing summary, scoped to one's own record.
- **Salary Advance** *(existing, reused)*: A recorded advance payment against an employee's salary; the self-service view lists only the calling employee's own advances.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An employee can retrieve their own current-month salary summary in a single request, without any HR involvement.
- **SC-002**: An employee can retrieve their own salary advance history, optionally filtered by month/year, in a single request, without any HR involvement.
- **SC-003**: 100% of self-service requests from users without a linked employee record are rejected, with zero instances of another employee's data being returned to a requester.
- **SC-004**: Figures shown to an employee in their self-service salary summary match, to the cent and minute, what HR sees for that same employee/month via the existing HR-facing endpoint.

## Assumptions

- Both endpoints reuse the calculation logic of the existing HR-facing `salary-summary` and `salary-advances` endpoints; this feature only adds a self-scoped access path and identity resolution, not new business rules for salary, advances, or lateness calculation.
- An authenticated user's employee identity is resolved via the existing one-to-one User-Employee link established by the employee/user-linking feature; this spec does not change how or when that link is created.
- Rejected requests (missing Employee role, or Employee role without a linked record) are treated as an authorization failure, consistent with how other role-gated endpoints in this system already respond to unauthorized access.
- The self-service salary summary intentionally includes lateness delay/deduction detail for the employee's own record — this extends spec 002's FR-013 restriction (previously HR-only) to also permit an employee to view their own delay/deduction figures, since seeing why one's own pay was reduced is core to this feature's value; HR-only visibility is unaffected for viewing *other* employees' data.
- Default month/year behavior (defaulting to the current calendar month when omitted) mirrors the existing HR-facing salary summary endpoint exactly.
- No new data is captured by this feature; it only exposes existing salary, advance, and lateness data through a new, identity-scoped access path.
