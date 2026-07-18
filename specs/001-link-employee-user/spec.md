# Feature Specification: Link Employee to User Account

**Feature Branch**: `001-link-employee-user`

**Created**: 2026-07-17

**Status**: Draft

**Input**: User description: "Add the improvement to associate an employee with and user. Update the employee table to receive the user id when create a new employee or edit an old one."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Link a user account while creating an employee (Priority: P1)

An HR staff member is registering a new employee and wants to attach that person's existing system login (user account) to the employee record at the moment of creation, so the two records are connected from day one.

**Why this priority**: This is the core of the requested improvement and covers the most common real-world moment this link is needed — onboarding.

**Independent Test**: Can be fully tested by creating a new employee while supplying an existing, unlinked user account's identifier, and confirming the resulting employee record shows that user as associated.

**Acceptance Scenarios**:

1. **Given** an existing user account that is not yet linked to any employee, **When** HR creates a new employee and supplies that user's identifier, **Then** the new employee record is saved with that user associated.
2. **Given** no user account is supplied, **When** HR creates a new employee, **Then** the employee record is saved successfully with no user associated.
3. **Given** a user identifier that does not correspond to any existing user account, **When** HR tries to create an employee with that identifier, **Then** the system rejects the request and no employee record is created.
4. **Given** a user account that is already linked to a different, existing employee, **When** HR tries to create a new employee using that same user identifier, **Then** the system rejects the request and no employee record is created.

---

### User Story 2 - Link, change, or remove a user account on an existing employee (Priority: P2)

An HR staff member needs to update an existing employee record — for example, an employee who didn't have system access before now needs it, or an employee's account needs to be corrected or unlinked.

**Why this priority**: Covers the ongoing lifecycle case (not just onboarding), which is explicitly called out in the request ("or edit an old one").

**Independent Test**: Can be fully tested by editing an existing employee record to add, change, or clear its associated user identifier, and confirming the stored association reflects the change.

**Acceptance Scenarios**:

1. **Given** an existing employee with no linked user account, **When** HR edits the employee and supplies an existing, unlinked user's identifier, **Then** the employee record is updated to show that user associated.
2. **Given** an existing employee already linked to a user account, **When** HR edits the employee and supplies a different, existing, unlinked user's identifier, **Then** the employee's association is updated to the new user.
3. **Given** an existing employee already linked to a user account, **When** HR edits the employee and explicitly clears the user association, **Then** the employee record no longer shows any linked user.
4. **Given** a user identifier that does not correspond to any existing user account, **When** HR edits an employee using that identifier, **Then** the system rejects the request and the employee's existing association is left unchanged.
5. **Given** a user account that is already linked to a different existing employee, **When** HR edits another employee to use that same user identifier, **Then** the system rejects the request and the employee's existing association is left unchanged.

---

### User Story 3 - View which user account is linked to an employee (Priority: P3)

Anyone authorized to view employee details can see, directly on the employee record, which user account (if any) is currently associated with that employee.

**Why this priority**: Without visibility, the association captured in Stories 1 and 2 has no practical value to its consumers (e.g. the frontend).

**Independent Test**: Can be fully tested by retrieving an employee record and confirming the linked user identifier (or absence of one) is present in the returned data.

**Acceptance Scenarios**:

1. **Given** an employee linked to a user account, **When** their employee record is retrieved, **Then** the response includes the linked user's identifier.
2. **Given** an employee with no linked user account, **When** their employee record is retrieved, **Then** the response indicates no user is associated.

---

### Edge Cases

- Supplying the employee's own current user identifier again on edit (no-op) MUST succeed without being treated as a conflict.
- Deactivating or deleting a user account elsewhere in the system does not automatically remove its association from the linked employee record — the link remains until explicitly changed.
- Attempting to link a user account to an employee while that same user is already linked to the employee being edited (i.e., unchanged) is not an error.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow an authorized HR user to optionally specify an existing user account when creating a new employee record.
- **FR-002**: System MUST allow an authorized HR user to add, change, or remove the user account associated with an existing employee record when editing it.
- **FR-003**: Associating a user account with an employee MUST be optional — an employee record MAY exist with no linked user account, both at creation and thereafter.
- **FR-004**: A given user account MUST be associated with at most one employee record at any time.
- **FR-005**: System MUST reject any create or edit request that would associate a user account with an employee when that user account is already associated with a different employee record.
- **FR-006**: System MUST reject any create or edit request that references a user identifier that does not correspond to an existing user account.
- **FR-007**: Employee records MUST expose the identifier of their currently associated user account (or clearly indicate none is associated) wherever employee details are returned.
- **FR-008**: Only users authorized to manage employee records (the existing Human Resources permission already required on employee endpoints) MAY create or change an employee's user association.

### Key Entities

- **Employee**: The existing HR employee record. Gains an optional reference to a single User account, representing that employee's system login (if any).
- **User**: The existing system account entity. Each user account can be referenced by at most one Employee record at a time.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: HR can attach a user account to an employee in the same action used to create or edit the employee — no separate workflow or extra request is required.
- **SC-002**: 100% of employee records accurately reflect their linked user account (or the absence of one) immediately after being created or edited.
- **SC-003**: 100% of attempts to link a user account to more than one employee at the same time are rejected, with no employee record left in a conflicting state.
- **SC-004**: Any caller authorized to view an employee's details can determine which user account, if any, is linked to that employee without consulting any other record.

## Assumptions

- The association between an employee and a user account is one-to-one and optional in both directions: an employee may have zero or one linked user account, and a user account may be linked to zero or one employee record.
- Any active or inactive user account may be linked to an employee, regardless of that user's assigned role — no role restriction is placed on which user accounts are eligible to be linked.
- The permission required to set or change this association is the same Human Resources permission already enforced on the existing employee create/edit endpoints; no new permission level is introduced.
- Removing or changing a user's account elsewhere in the system does not cascade to automatically clear the employee-side association; that remains a separate, explicit HR action.
