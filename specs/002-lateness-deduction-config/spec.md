# Feature Specification: HR Lateness Tolerance & Salary Deduction Configuration

**Feature Branch**: `002-lateness-deduction-config`

**Created**: 2026-07-18

**Status**: Draft

**Input**: User description: "Add configurations on human resources about tolerance for delays, salary deduction for lateness (hourly), hour of entrance and a flag that enable or disable this configuration. The configuration is unique for entire system. Also improve the salary summary endpoint to show the delays and late payment discount."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - HR configures lateness rules (Priority: P1)

An HR user sets up the system-wide lateness rules: the expected entrance time, a tolerance (grace period, in minutes) before a late arrival counts against the employee, how much money is deducted, the time block (in minutes) that must be reached before that deduction applies, and whether the whole rule set is currently active.

**Why this priority**: Foundational — no delay tracking or deduction can happen anywhere else in the system until this configuration exists.

**Independent Test**: Can be fully tested by submitting configuration values and reading them back unchanged, independent of any salary summary being viewed.

**Acceptance Scenarios**:

1. **Given** no configuration exists yet, **When** HR submits entrance time, tolerance, deduction value, deduction interval, and enables it, **Then** the system stores a single configuration record with those values.
2. **Given** a configuration already exists, **When** HR updates any value, **Then** the existing record is replaced with the new values rather than a second record being created.
3. **Given** HR submits a negative tolerance, a negative or zero deduction interval, or a negative deduction value, **When** saving, **Then** the system rejects the update and the previous values remain in effect.

---

### User Story 2 - HR reviews delay and deduction on an employee's salary summary (Priority: P2)

An HR user opens an employee's monthly salary summary and can see how many minutes/days the employee was late and how much was deducted for lateness, with the net salary already reflecting that deduction alongside existing advances.

**Why this priority**: This is the primary value the configuration exists to deliver — visibility and correct pay calculation — but it depends on User Story 1 already being in place.

**Independent Test**: With a configuration enabled and known attendance data for an employee, request the salary summary and verify the delay and deduction figures match manual calculation from the configured rules.

**Acceptance Scenarios**:

1. **Given** the configuration is enabled and the employee had one or more days late beyond the tolerance in the requested month, **When** HR requests the salary summary, **Then** the response includes total delay minutes, count of late days, total lateness deduction, and a net salary reduced by that deduction (in addition to advances).
2. **Given** the configuration is enabled and the employee had no late arrivals in the month, **When** HR requests the salary summary, **Then** delay minutes, late days, and deduction are all zero, and net salary equals gross salary minus advances only.
3. **Given** a day where the employee's delay exceeded the tolerance but did not reach one full deduction interval, **When** the summary is requested, **Then** that day counts toward the late-days count but contributes zero to the monetary deduction.
4. **Given** a day where the employee's delay reached more than one full deduction interval, **When** the summary is requested, **Then** the deduction for that day scales by the number of full intervals reached (e.g. two full intervals reached deducts twice the configured value).

---

### User Story 3 - HR disables lateness deductions without losing the configured rules (Priority: P3)

An HR user turns the configuration off, immediately stopping lateness deductions on all salary summaries, and can turn it back on later without re-entering the tolerance, deduction value, interval, or entrance time.

**Why this priority**: Operational flexibility that is used less often than configuring or viewing, but still required by the feature description ("flag that enable or disable this configuration").

**Independent Test**: Disable the configuration, request a salary summary that previously showed a deduction, and confirm the deduction is now zero while gross salary and advances are unaffected; re-enable and confirm the original values are still in effect.

**Acceptance Scenarios**:

1. **Given** a configuration with a deduction previously applied to an employee's month, **When** HR disables it, **Then** subsequent salary summary requests for that same month show zero lateness deduction and zero delay information.
2. **Given** the configuration is disabled, **When** HR re-enables it without resubmitting any values, **Then** the previously stored entrance time, tolerance, deduction value, and deduction interval are still in effect and immediately apply again.

---

### Edge Cases

- Employee has no attendance check-in at all on a given day (absence): that day is not evaluated for lateness — this feature does not track absences.
- Employee's earliest check-in of the day is at or before the expected entrance time: zero delay, not a late day.
- Delay exceeds the tolerance but is smaller than one deduction interval: day is flagged late, deduction is zero for that day.
- Delay spans multiple deduction intervals: deduction scales linearly per full interval reached; any remainder below a full interval is not charged.
- No lateness configuration has ever been created: salary summaries behave as if lateness tracking is disabled (zero delay, zero deduction) rather than failing.
- Requested salary summary month is in the past and attendance/configuration values have since changed: the summary always reflects the configuration and attendance data as they exist at request time (no historical snapshotting).
- Lateness deduction combined with existing advances could reduce net salary below zero: this is not capped, consistent with existing behavior where advances already are not capped against gross salary.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide one system-wide (singleton) lateness configuration containing: expected entrance time, tolerance in minutes, deduction interval in minutes, deduction value (monetary amount), and an enabled/disabled flag.
- **FR-002**: Authorized HR users MUST be able to view the current lateness configuration values.
- **FR-003**: Authorized HR users MUST be able to create the configuration (if none exists) or update it; because it is unique for the entire system, an update MUST replace the values of the single existing record rather than creating an additional one.
- **FR-004**: System MUST reject configuration values where tolerance is negative, deduction interval is zero or negative, or deduction value is negative.
- **FR-005**: The tolerance MUST represent the number of minutes an employee may arrive after the expected entrance time without that day counting as late.
- **FR-006**: An employee's daily delay MUST be calculated as the number of minutes between the expected entrance time and the employee's earliest recorded attendance check-in for that day, only when that check-in is later than the expected entrance time.
- **FR-007**: A day MUST be classified as "late" only when its calculated delay exceeds the configured tolerance.
- **FR-008**: For a late day, the monetary deduction MUST be computed from the full delay measured from the expected entrance time (not reduced by the tolerance): divide the delay minutes by the configured deduction interval discarding any remainder, then multiply by the configured deduction value (e.g. a 125-minute delay with a 60-minute interval and a 6.80 deduction value yields floor(125/60) × 6.80 = 13.60).
- **FR-009**: A late day whose delay does not reach at least one full deduction interval MUST count toward the late-days total but MUST NOT generate any monetary deduction.
- **FR-010**: When the configuration is disabled, no delay evaluation or monetary deduction MUST be applied to any salary summary — delay minutes, late-days count, and deduction all report as zero.
- **FR-011**: The salary summary for an employee MUST include, for the requested month: total delay minutes accumulated across late days, count of late days, and total lateness deduction amount.
- **FR-012**: The salary summary's net salary MUST subtract the total lateness deduction, in addition to the existing advances deduction, when the configuration is enabled.
- **FR-013**: Only authorized HR personnel MUST be able to view or modify the lateness configuration, and to view the delay/deduction details in an employee's salary summary, consistent with existing access controls already applied to salary data.
- **FR-014**: If no lateness configuration has ever been created, the system MUST treat salary summaries as if lateness tracking is disabled rather than failing the request.

### Key Entities

- **Lateness Configuration**: The single, system-wide set of rules governing late-arrival deductions — expected entrance time, tolerance (minutes), deduction interval (minutes), deduction value (money), and enabled/disabled flag. Exactly one instance exists at any time.
- **Salary Summary** *(existing, extended)*: An employee's monthly pay breakdown. Extended to carry total delay minutes, late-days count, and total lateness deduction, with net salary reflecting the deduction.
- **Attendance Check-in** *(existing)*: An employee's recorded clock-in event for a day. The earliest check-in of each calendar day is used as that day's entrance time for delay calculation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: HR can view and update all lateness configuration values (entrance time, tolerance, deduction value, deduction interval, enabled flag) in a single action.
- **SC-002**: For 100% of employees with recorded attendance in a given month, the salary summary's delay and deduction figures match manual calculation using the configured tolerance/interval/value rules.
- **SC-003**: Disabling the configuration removes lateness deductions and delay figures from every salary summary requested afterward, with no other data changes required.
- **SC-004**: HR can determine how many minutes/days an employee was late and the resulting deduction for a given month directly from the salary summary, without consulting raw attendance records.

## Assumptions

- Only the earliest attendance check-in of a calendar day is treated as that day's entrance time; later check-ins that day (e.g. returning from lunch, end-of-day) are not considered for lateness.
- Days with no attendance check-in at all (absence) are out of scope for this feature; absence tracking is a separate concern.
- The expected entrance time applies uniformly to every day; this feature does not support per-weekday or per-shift entrance times.
- Viewing/modifying the lateness configuration and viewing the enriched salary summary reuse the same HR-level access control already protecting the existing salary summary endpoint.
- Lateness deduction is not capped against gross salary; net salary can go negative in extreme cases, matching how advances already behave in the existing salary summary.
- This feature does not change how attendance check-ins are captured; it only reads existing attendance data to compute delay.
