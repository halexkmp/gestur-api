# Feature Specification: Bulk Employee Schedule & Attendance Verification

**Feature Branch**: `005-bulk-employee-schedule`

**Created**: 2026-07-21

**Status**: Draft

**Input**: User description: "implement a bulk get to return the employee schedule. The schedule by employee is degrading the server when have a lot of employees. The endpoint should return the same value. A front end enhacement also will be done later." Refined: "the goal of this spec is consolidate into single endpoint, the schedule and the verification attendance, receiving the filter by employee, month and year. Reducing the requests from front end to backend."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - HR loads schedule + attendance for all employees for a period in one call (Priority: P1)

An HR/Admin user needs to see, for a given month and year, both the weekly work schedule and the attendance verification (present / justified absence / unjustified absence per day) for every employee — e.g. to populate a monthly schedule/attendance overview screen. Today this requires two requests per employee (one to the weekly schedule endpoint, one to the attendance verification endpoint), and as the employee count grows this repeated, per-employee fetching slows down and degrades the server. Instead, the system should return both pieces of data, for every employee, in a single request for the requested month/year.

**Why this priority**: This is the core problem reported — per-employee, per-data-type lookups don't scale with headcount and are actively degrading the server. Solving this for the "get everyone for a period" case removes the majority of the load (2×N requests down to 1).

**Independent Test**: Call the new bulk endpoint with a month and year and no employee filter, against a dataset with many employees, and confirm a single response contains, for each employee that has a schedule, the same weekly schedule values and the same attendance verification days/classifications that the two existing per-employee endpoints would return individually for that employee and period.

**Acceptance Scenarios**:

1. **Given** multiple employees each have a weekly schedule and journey/absence data for the requested month, **When** an HR/Admin user calls the bulk endpoint with a month, year, and no employee filter, **Then** the response contains one entry per employee that has a schedule, each including the same day-flag values `GET /employees/schedule/{employee_id}` would return and the same per-day attendance classification and unjustified-absence count `GET /employees/attendance-verification/{employee_id}?month&year` would return for that employee and period.
2. **Given** an employee has no schedule configured, **When** the bulk endpoint is called, **Then** that employee is simply absent from the returned list (no error, no entry for them) — consistent with the existing per-employee endpoints treating "no schedule" as reportable emptiness rather than a hard failure.
3. **Given** no month/year is supplied, **When** the bulk endpoint is called, **Then** it defaults to the current month/year, matching the default behavior of the existing attendance verification endpoint.

---

### User Story 2 - HR loads schedule + attendance for a specific set of employees (Priority: P2)

An HR/Admin user working from a filtered or paginated employee list (rather than the full roster) needs schedule and attendance data, for a given month/year, for only that subset — without falling back to per-employee requests.

**Why this priority**: Extends the same consolidation to partial/filtered views, so no calling pattern in the product is left doing per-employee, per-endpoint lookups in a loop.

**Independent Test**: Call the bulk endpoint with an explicit set of employee IDs plus a month/year and confirm the response contains combined schedule + attendance entries only for those IDs (that have a schedule), matching the two existing per-employee endpoints.

**Acceptance Scenarios**:

1. **Given** a list of specific employee IDs and a month/year, **When** an HR/Admin user calls the bulk endpoint, **Then** the response contains combined schedule + attendance entries only for the requested employees that have a schedule configured.
2. **Given** an ID list that includes an employee ID which doesn't exist or has no schedule, **When** the bulk endpoint is called, **Then** that ID is silently skipped and entries for the remaining valid employees are still returned.

---

### Edge Cases

- No employees exist yet, or none of the requested/existing employees have a schedule configured → empty list, not an error.
- A very large number of employees (the scenario causing today's degradation) → the endpoint must still respond successfully in a single call for the requested month/year, rather than requiring the caller to loop per employee and per data type.
- A caller without HR/Admin permission calls the endpoint → rejected the same way the existing schedule/attendance-verification endpoints reject unauthorized callers.
- An explicitly requested employee ID doesn't correspond to any employee at all → skipped, not a hard failure for the whole request.
- An employee has a schedule but no linked user account, or is currently inactive, or the requested period predates their start date → that employee's attendance portion follows the same rules as the existing attendance verification endpoint (empty days / empty result for the affected period), while their weekly schedule values are still returned.
- Month/year omitted → defaults to the current month/year, same as the existing attendance verification endpoint.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a single endpoint that returns, for many employees in one request, both the weekly schedule and the attendance verification for a given month/year — replacing the need to call the existing per-employee schedule endpoint and the existing per-employee attendance verification endpoint separately, once per employee.
- **FR-002**: The schedule portion of each employee's entry MUST be identical in shape and values to what `GET /employees/schedule/{employee_id}` returns for that employee.
- **FR-003**: The attendance portion of each employee's entry MUST be identical in shape and values to what `GET /employees/attendance-verification/{employee_id}?month&year` returns for that employee and period (day-by-day classification and unjustified-absence count).
- **FR-004**: The endpoint MUST accept a month and a year to scope the attendance portion of the result, defaulting to the current month/year when omitted, consistent with the existing attendance verification endpoint's default.
- **FR-005**: Calling the endpoint with no employee filter MUST return combined entries for all employees that have a schedule configured.
- **FR-006**: The endpoint MUST also support scoping the result to an explicit set of employee IDs, returning combined entries only for that subset.
- **FR-007**: Employees with no schedule configured MUST be omitted from the result rather than causing an error or being represented with placeholder/default values.
- **FR-008**: An explicitly requested employee ID that doesn't exist, or has no schedule, MUST be skipped without failing the request for the other requested employees.
- **FR-009**: Only HUMAN_RESOURCES or ADMIN roles MUST be able to call this endpoint, matching the existing schedule and attendance-verification endpoints' permission rule.
- **FR-010**: The existing per-employee schedule endpoint and per-employee attendance verification endpoint MUST remain unchanged and continue to function, since the frontend migration to the bulk endpoint is a separate, later effort.
- **FR-011**: The endpoint's response time MUST NOT scale with employee count the way the current two-calls-per-employee pattern does — retrieval for schedule and attendance data across the requested employees MUST be done as bulk operations, not as repeated per-employee lookups performed server-side.

### Key Entities

- **Employee Weekly Schedule**: The existing per-employee record of which days of the week (Monday–Sunday) an employee works. Unchanged by this feature — only how many can be retrieved per call changes.
- **Attendance Verification Result**: The existing derived, per-employee, per-period (month/year) day-by-day classification (present / justified absence / unjustified absence) plus unjustified-absence count. Unchanged by this feature — only how many employees' results can be retrieved per call changes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Retrieving both the schedule and the attendance verification for the entire employee roster, for a given month/year, requires exactly one request, regardless of how many employees exist.
- **SC-002**: Fetching combined schedule + attendance data for a large employee roster (hundreds of employees) no longer causes the server slowdown observed with the current two-calls-per-employee pattern.
- **SC-003**: For every employee with a configured schedule, the schedule and attendance values returned by the bulk endpoint exactly match the values the existing per-employee endpoints return for that employee and period (no data discrepancy introduced by the new path).
- **SC-004**: The existing per-employee schedule and attendance-verification endpoints continue to work with no behavior change, so existing frontend integrations are unaffected until the planned frontend migration happens.

## Assumptions

- The frontend change to actually call this new bulk endpoint (instead of looping per employee across two endpoints) is a separate, later effort and is out of scope for this specification — this feature only covers the backend capability.
- "Return the same value" means per-employee, per-endpoint data parity with the existing schedule and attendance-verification responses, combined into one entry per employee rather than a new/different representation.
- Employees without a configured schedule are omitted from the bulk response, consistent with how the existing schedule endpoint treats "no schedule" as a meaningful absence-of-data state.
- Permission requirements mirror the existing endpoints (HUMAN_RESOURCES or ADMIN only) — no new role or self-service variant is required for this feature.
- Month/year apply only to the attendance-verification portion of each entry (the weekly schedule itself has no date range); omitting them defaults to the current month/year, matching existing behavior.
- No pagination is required for the "all employees" case for the currently expected data volumes; if the roster grows large enough to need pagination, that would be a follow-up enhancement.
