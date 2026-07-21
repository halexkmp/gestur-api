# Feature Specification: Employee Weekly Work Schedule & Attendance Verification

**Feature Branch**: `004-employee-work-schedule`

**Created**: 2026-07-21

**Status**: Draft

**Input**: User description: "Create and schedule employee feature that will use to alocate employees by according the weekly work. This schedule should demonstrate which days the employee is working and which days not. Also, its possible to add justified absences. This schedule will be use to match journeys register and verify if the employee has or not a register journey on those work day, which means an absence (not justified)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Define an employee's weekly work schedule (Priority: P1)

An HR/Admin user sets up which days of the week a given employee is expected to work (e.g. Monday–Friday working, Saturday–Sunday off), so the system knows when that employee's presence is expected.

**Why this priority**: Every other capability in this feature (absence justification, attendance verification) depends on a schedule existing first. Without it, there is no baseline to compare journey registers against.

**Independent Test**: Can be fully tested by an HR/Admin user creating a weekly schedule for an employee and then retrieving it, confirming the working/non-working days are stored and returned exactly as set — delivers value on its own as a source of truth for expected work days.

**Acceptance Scenarios**:

1. **Given** an employee with no schedule yet, **When** HR/Admin sets a weekly schedule marking specific weekdays as working days and the rest as non-working, **Then** the system stores the schedule and returns it associated with that employee.
2. **Given** an employee already has a weekly schedule, **When** HR/Admin updates it to change which days are working days, **Then** the system replaces the previous schedule with the new one and applies it going forward.
3. **Given** an employee has a weekly schedule, **When** anyone with permission requests that employee's schedule, **Then** the system returns the current working/non-working status for each day of the week.

---

### User Story 2 - Record a justified absence (Priority: P2)

An HR/Admin user records that an employee's absence on a specific scheduled work day is justified (e.g. medical leave, approved personal leave), so that day is not later flagged as an unexplained absence.

**Why this priority**: This is the mechanism that prevents legitimate, approved absences from being misclassified as attendance failures — it must exist before the verification story can be considered trustworthy.

**Independent Test**: Can be fully tested by recording a justified absence for an employee on a specific date and confirming it is stored and retrievable, independent of whether attendance verification has run.

**Acceptance Scenarios**:

1. **Given** an employee is scheduled to work on a given date, **When** HR/Admin records a justified absence for that employee on that date, **Then** the system stores the justified absence with its reason/note and date.
2. **Given** a justified absence already exists for an employee on a date, **When** HR/Admin views that employee's records for that period, **Then** the justified absence is clearly listed as justified, not as a missing/unjustified absence.
3. **Given** HR/Admin attempts to record a justified absence for a date that is not one of the employee's scheduled work days, **When** the request is submitted, **Then** the system rejects it since attendance is not expected on that day.

---

### User Story 3 - Verify attendance against the schedule (Priority: P3)

HR/Admin reviews, for an employee and a given period, which scheduled work days had a matching journey register (present), which scheduled work days have a justified absence, and which scheduled work days have neither (unjustified absence), so they can identify unexplained attendance gaps.

**Why this priority**: This is the payoff of the feature — turning the schedule and justified-absence data into an actionable comparison against actual journey registers. It depends on Stories 1 and 2 already existing.

**Independent Test**: Can be fully tested by seeding an employee's schedule, a set of journey registers, and a justified absence, then requesting the attendance verification for a period and confirming each scheduled day is classified correctly (present, justified absence, or unjustified absence) and non-work days are excluded.

**Acceptance Scenarios**:

1. **Given** an employee is scheduled to work on a date and has at least one journey register that day, **When** attendance is verified for that period, **Then** that date is classified as present (no absence).
2. **Given** an employee is scheduled to work on a date, has no journey register that day, and has no justified absence for that date, **When** attendance is verified, **Then** that date is classified as an unjustified absence.
3. **Given** an employee is scheduled to work on a date and has a justified absence recorded for that date, **When** attendance is verified, **Then** that date is classified as a justified absence, regardless of whether a journey register also exists.
4. **Given** a date falls on a non-working day per the employee's schedule, **When** attendance is verified, **Then** that date is excluded from both the present and absence counts.

---

### Edge Cases

- What happens when an employee has no weekly schedule defined at all? The system MUST treat that employee as having no expected work days, so no dates are ever flagged as an unjustified absence until a schedule is created.
- What happens when a journey register exists for an employee on a day their schedule marks as non-working (e.g. they worked an unscheduled Saturday)? That day is not part of the scheduled-workday comparison and MUST NOT be flagged as an absence of any kind.
- What happens when attendance verification is requested for a period before the employee's start date? Those dates MUST be excluded, even on a nominally scheduled weekday. What happens when the employee is currently inactive? The system excludes their **entire** requested period once inactive, since it has no record of the exact date they became inactive — only a current flag. This may under-report unjustified absences that genuinely occurred while still active, in a period that also includes the deactivation; this is an accepted, documented limitation (see Assumptions).
- What happens when the employee being verified has no linked user account? Journey registers are recorded against a user account, not directly against an employee, so the system can never detect a matching journey register for an unlinked employee. The system MUST report an empty result (zero days) rather than flagging every scheduled work day as an unjustified absence, since the gap is a missing account link, not an attendance failure.
- What happens when the weekly schedule is updated mid-period? Verification for past dates MUST use the schedule currently in effect (the latest one saved); this feature does not retain a history of prior schedule versions (see Assumptions).
- What happens when HR/Admin tries to record a duplicate justified absence for the same employee and date? The system MUST reject the duplicate rather than creating two records for the same date.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow HR/Admin to create a weekly work schedule for an employee, specifying for each day of the week (Monday through Sunday) whether it is a working day or a non-working day.
- **FR-002**: System MUST allow HR/Admin to update an employee's existing weekly work schedule, replacing the prior working/non-working pattern.
- **FR-003**: System MUST allow retrieving an employee's current weekly work schedule.
- **FR-004**: System MUST allow HR/Admin to record a justified absence for an employee, capturing at minimum the date and a reason/note.
- **FR-005**: System MUST reject a justified absence recorded for a date that is not a scheduled working day for that employee.
- **FR-006**: System MUST reject a duplicate justified absence for the same employee and the same date.
- **FR-007**: System MUST allow HR/Admin to list an employee's recorded justified absences for a given period.
- **FR-008**: System MUST allow HR/Admin to remove a previously recorded justified absence.
- **FR-009**: System MUST provide an attendance verification for an employee over a given period (e.g. a month) that, for every scheduled working day in that period, classifies the day as one of: present (has a matching journey register), justified absence (has a recorded justified absence), or unjustified absence (neither).
- **FR-010**: System MUST exclude non-working days, per the employee's schedule, from the attendance verification's present/absence classification.
- **FR-011**: System MUST exclude dates before the employee's start date from the attendance verification. For an employee who is currently inactive, the system MUST exclude the entire requested period rather than attempting to clip only the days after deactivation — the system does not track a precise deactivation date, only a current active/inactive flag (see Assumptions).
- **FR-012**: System MUST treat an employee with no weekly schedule defined as having zero expected work days, so no unjustified absences can be produced for that employee until a schedule exists.
- **FR-013**: System MUST restrict weekly schedule management (create/update) and justified absence management (create/list/delete) to HR/Admin users.
- **FR-014**: System MUST allow an employee to view their own current weekly work schedule.
- **FR-015**: Attendance verification MUST NOT modify or trigger any salary/payroll calculation as part of this feature; it is a reporting/visibility capability only (see Assumptions).
- **FR-016**: System MUST report an empty attendance verification result (no days classified, zero unjustified absences) for an employee with no linked user account, rather than classifying every scheduled work day as an unjustified absence, since presence cannot be determined without a linked account.

### Key Entities

- **Employee Weekly Schedule**: The recurring weekly pattern of working vs. non-working days for one employee. One active schedule per employee at a time; replacing it applies going forward only.
- **Justified Absence**: A record that an employee's absence on a specific scheduled work day is excused, including the date and a reason/note. Always tied to a single employee and a single date that must be one of that employee's scheduled work days.
- **Attendance Verification Result**: A derived (computed on demand, not separately stored) per-day classification for an employee over a period — present, justified absence, or unjustified absence — produced by comparing the Employee Weekly Schedule, recorded Justified Absences, and existing journey register data.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: HR/Admin can set up a new employee's weekly work schedule in under 1 minute.
- **SC-002**: For any employee/period with a schedule defined, attendance verification correctly classifies 100% of scheduled work days as present, justified absence, or unjustified absence, with zero non-working days incorrectly included.
- **SC-003**: HR/Admin can identify all unjustified absences for an employee in a given month in a single request, without manually cross-referencing schedules, journey logs, and absence records by hand.
- **SC-004**: Recording a justified absence takes HR/Admin under 30 seconds and is reflected immediately in the next attendance verification for that employee.

## Assumptions

- HR/Admin records justified absences directly (e.g. after receiving a medical certificate or approved leave request through channels outside this system); this feature does not include an employee-initiated request/approval workflow, consistent with how other employee records (e.g. salary advances, lateness configuration) are managed directly by HR/Admin in this codebase today.
- The weekly schedule is a simple recurring working/non-working flag per weekday (no partial days, shifts, or specific work hours) — time-of-day expectations (e.g. expected entrance time) are already covered by the existing lateness configuration feature and are out of scope here.
- Only one weekly schedule is active per employee at a time; schedule changes apply prospectively. This feature does not version or retain historical copies of past schedules.
- Public holidays and company-wide non-working days are out of scope for this feature; only the per-employee weekly pattern and per-date justified absences determine expected work days.
- A "matching journey register" for attendance verification means at least one journey register exists for the employee on that calendar day (the existing journey registration feature is the source of this data; no new journey behavior is introduced).
- Flagging an unjustified absence is a reporting/visibility outcome only; it does not automatically create a salary deduction. Payroll integration (e.g. deducting pay for unjustified absences, similar to the existing lateness deduction) is out of scope for this feature and would be a separate follow-up feature.
- Employee records only track a current `active`/`inactive` flag, not a deactivation date/timestamp. Attendance verification for a currently-inactive employee therefore excludes their entire requested period rather than clipping to an exact (unknown) deactivation date. Adding a deactivation timestamp to `Employee` is out of scope for this feature.
