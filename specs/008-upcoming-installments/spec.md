# Feature Specification: Upcoming Loan Installments List

**Feature Branch**: `008-upcoming-installments`

**Created**: 2026-08-10

**Status**: Draft

**Input**: User description: "based on the previous analises create the new slice to list upcoming installments"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See which installments come due in a window (Priority: P1)

A manager looking at the loan dashboard picks a date window (for example, the next 30 days)
and wants the individual installments that fall due inside it — not just the totals. For
each one they need to know who owes it, which loan it belongs to, when it is due, how much
was scheduled, how much has already been received, and how much is still open.

**Why this priority**: This is the whole point of the feature. Today the loan book can only
be viewed either as an aggregate over a period (totals plus a per-partner rollup) or as the
full installment list of one single loan. There is no way to answer "what is coming due
soon, across all partners" — which is the question a collections routine starts from.

**Independent Test**: Set a window that contains known installments from several loans and
partners, request the list, and confirm every unsettled installment due inside that window
appears exactly once with the correct partner, due date, scheduled amount, received amount,
and remaining amount. This alone is a usable, shippable collections view.

**Acceptance Scenarios**:

1. **Given** installments due on dates inside and outside the requested window, **When** the
   manager requests the list for that window, **Then** only the installments due inside the
   window (inclusive of both boundary dates) are returned.
2. **Given** an installment that has been fully settled, **When** the list is requested for a
   window containing its due date, **Then** that installment is not returned.
3. **Given** an installment that has received a partial payment, **When** the list is
   requested, **Then** it is returned with the amount already received and the remaining
   balance shown separately.
4. **Given** installments belonging to a canceled loan, **When** the list is requested,
   **Then** those installments are not returned.
5. **Given** several matching installments, **When** the list is requested, **Then** they are
   ordered by due date, soonest first, so the most urgent collection appears at the top.
6. **Given** a window in which nothing is due, **When** the list is requested, **Then** an
   empty list is returned rather than an error.

---

### User Story 2 - Include what is already overdue (Priority: P2)

The same manager wants the option to see, alongside what is coming due, everything that is
already late — unsettled installments whose due date has passed before the start of the
window. These are the collections that need attention first.

**Why this priority**: Valuable, but the in-range list is useful on its own, and this
behavior is deliberately opt-in so that the default result stays a clean, exact mirror of
the requested window and reconciles with the period summary totals.

**Independent Test**: With at least one unsettled installment due before the window start,
request the list twice — once with the overdue option off and once on — and confirm the
overdue installment is absent the first time and present, marked as overdue, the second
time.

**Acceptance Scenarios**:

1. **Given** an unsettled installment due before the window start, **When** the list is
   requested without the overdue option, **Then** that installment is not returned.
2. **Given** the same installment, **When** the list is requested with the overdue option
   enabled, **Then** it is returned, flagged as overdue, and ordered ahead of the in-window
   installments because its due date is earlier.
3. **Given** an installment due before the window start that has been fully settled, **When**
   the list is requested with the overdue option enabled, **Then** it is still not returned.

---

### User Story 3 - Narrow the list to one partner (Priority: P3)

When following up with a specific partner, the manager wants the same window view limited to
that partner's installments only, instead of filtering a long mixed list by eye.

**Why this priority**: A convenience filter over an already-complete list. Useful for the
one-partner follow-up conversation, but the feature delivers its value without it.

**Independent Test**: Request the same window with and without a partner filter and confirm
the filtered result contains exactly the subset belonging to that partner.

**Acceptance Scenarios**:

1. **Given** matching installments across several partners, **When** the list is requested
   with a partner filter, **Then** only that partner's installments are returned.
2. **Given** a partner with no installments due in the window, **When** the list is requested
   with that partner filter, **Then** an empty list is returned.

---

### Edge Cases

- **Window end before window start**: rejected as an invalid request with a clear message,
  consistent with how the existing period summary handles the same mistake.
- **Single-day window** (start equals end): valid; returns installments due on exactly that
  day.
- **Overpaid installment**: the received amount reported is capped at the scheduled amount so
  the remaining balance can never be shown as negative.
- **Installment due exactly on the window boundary**: included — both boundary dates are
  inclusive.
- **Installment due exactly today, unsettled**: not overdue; today has not yet passed.
- **Overdue option enabled with no lower bound in sight**: all unsettled installments due
  before the window start are included, however far back they go — there is no separate
  cutoff.
- **Loan whose installments are all settled**: contributes nothing to the list.
- **Unauthenticated request**: rejected, consistent with every other loan endpoint.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a way to list individual loan installments due within a
  caller-specified date window, spanning all loans and all partners.
- **FR-002**: The window start and end dates MUST both be required. The end date MUST always
  be treated as an inclusive upper bound on the installment due date. The start date MUST be
  treated as an inclusive lower bound, except where FR-010 removes that bound — it stays
  required either way.
- **FR-003**: The system MUST reject a request whose window end is earlier than its window
  start, returning a client error with an explanatory message rather than an empty list.
- **FR-004**: The system MUST exclude installments belonging to canceled loans.
- **FR-005**: The system MUST exclude installments that are already fully settled, since a
  settled installment is not a pending collection.
- **FR-006**: For each returned installment, the system MUST report: the installment's own
  identifier, the loan it belongs to, the owing partner's identifier and name, the
  installment's sequence number within its loan, its due date, its scheduled amount, the
  amount already received against it, the amount still remaining, its settlement status, and
  whether it is overdue.
- **FR-007**: The amount reported as received MUST be the sum of payments recorded against
  the installment, capped at the scheduled amount so the remaining amount is never negative.
- **FR-008**: An installment MUST be reported as overdue when its due date is earlier than
  the current date and it is not fully settled.
- **FR-009**: The system MUST order results by due date ascending, breaking ties by loan and
  then by installment sequence number, so the most urgent collection appears first.
- **FR-010**: The system MUST accept an optional flag that, when enabled, additionally
  includes every unsettled, non-canceled installment whose due date falls before the window
  start. When the flag is absent or disabled, the result MUST contain only installments due
  inside the window.
- **FR-011**: The system MUST accept an optional partner filter that restricts the result to
  installments owed by a single partner.
- **FR-012**: The system MUST accept an optional maximum result count that truncates the
  ordered list, so a caller can ask for just the next few installments.
- **FR-013**: A window with no matching installments MUST return an empty list, not an error.
- **FR-014**: The listing MUST require an authenticated caller and MUST be available to any
  authenticated user, matching the access level of the existing loan period summary.
- **FR-015**: The published API contract MUST be updated to describe the new listing, its
  parameters, and its response shape.

### Key Entities

- **Loan Installment**: One scheduled payment obligation within a loan. Carries a sequence
  number, a scheduled amount, a due date, and a settlement status (pending, partially paid,
  paid). This is the unit the list is built from.
- **Installment Payment**: A recorded receipt against a single installment, carrying an
  amount and a payment date. Several may exist per installment; together they determine how
  much of the installment has been received.
- **Loan**: The agreement an installment belongs to. Supplies the owing partner and may be
  canceled, in which case its installments are not collectible.
- **Partner**: The counterparty who owes the loan. Identified by name in the list so the
  reader knows who to contact without a second lookup.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can see every installment coming due in a chosen window, across all
  partners, in a single request — a view that requires an unbounded number of per-loan
  lookups today.
- **SC-002**: For any window, the still-owed amounts of the returned installments reconcile
  with the outstanding amount reported by the existing period summary for that same window.
  The one known exception is an installment that was marked settled without any payment being
  recorded against it: this list treats it as settled while the period summary still counts it
  as outstanding. That disagreement predates this feature and is not corrected by it.
- **SC-003**: 100% of returned rows identify the owing partner by name, so a collections
  follow-up can be started without any additional lookup.
- **SC-004**: The list returns results for a one-month window over the full loan book within
  the same responsiveness users already experience from the period summary — no perceptible
  wait.
- **SC-005**: A request whose window is reversed is rejected with a message that states the
  problem, so the user can correct it without guessing.
- **SC-006**: Enabling the overdue option surfaces every still-unpaid past-due installment,
  with none missed and none already-settled included.

## Assumptions

- Access matches the existing loan period summary: any authenticated user may read the list;
  no additional role restriction is introduced.
- "Unsettled" means the installment is not fully paid. Both untouched and partially paid
  installments appear in the list.
- Overdue is judged against the current date at the time of the request, independent of the
  requested window.
- The overdue option has no lower cutoff — when enabled it reaches back over the entire loan
  history. Callers who want a bounded look-back can simply widen the window start instead.
- No pagination is introduced, consistent with every other listing in this project. The
  optional maximum result count covers the "show me the next few" case; the expected volume
  for a typical window is well within what a single response can carry.
- The list is read-only. Recording payments and settling installments continue to happen
  through the existing payment endpoints and are out of scope here.
- No new stored data is introduced. Every reported value is derived from existing loans,
  installments, and recorded payments, so no schema change or migration is expected.
- The existing period summary is left unchanged; this listing stands alongside it rather than
  extending its response.
