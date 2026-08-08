# Feature Specification: Loan Period Summary

**Feature Branch**: `007-loan-period-summary`

**Created**: 2026-08-08

**Status**: Draft

**Input**: User description: "create a endpoint to summmary loans based on date filter. Its be will use on a dashboard to show how will be the revenues, the profits and list of parters that will pay (and how much) on those data range."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Manager sees expected revenue and profit for a period (Priority: P1)

A manager opens the loans dashboard, picks a date range (for example, the current month, or next week), and immediately sees how much money the business is scheduled to receive from partner loan installments in that range, and how much of that money is profit (interest) rather than returned capital.

**Why this priority**: This is the headline number the dashboard exists to show. Delivered alone, it already answers "how will my cash look in this period?" and is a viable MVP without any per-partner breakdown.

**Independent Test**: Can be fully tested by creating loans whose installments fall inside and outside a chosen range, requesting the summary for that range, and verifying the reported expected revenue equals the sum of the in-range installment amounts and that the reported profit equals the interest share of those same installments.

**Acceptance Scenarios**:

1. **Given** several loans with installments scheduled across different dates, **When** a manager requests the summary for a date range, **Then** the response reports the total amount scheduled to be received in that range (expected revenue), the total capital portion of that amount, and the total interest portion of that amount (expected profit).
2. **Given** a loan whose installments all fall outside the requested range, **When** the summary is requested, **Then** none of that loan's amounts contribute to any total.
3. **Given** an installment scheduled exactly on the first day or exactly on the last day of the requested range, **When** the summary is requested, **Then** that installment is included (range boundaries are inclusive on both ends).
4. **Given** no installments are scheduled in the requested range, **When** the summary is requested, **Then** all totals are zero and the request still succeeds.

---

### User Story 2 - Manager sees which partners will pay and how much (Priority: P2)

A manager viewing the same period wants to know *who* is behind those numbers: a list of partners with a scheduled payment in the range, each showing how much that partner is scheduled to pay, so the manager can follow up with the right people.

**Why this priority**: This turns the aggregate number into an actionable collection list. It depends on the same period filtering as P1 but is independently verifiable once P1 exists.

**Independent Test**: Can be fully tested by giving two partners installments inside the range and one partner installments only outside it, then confirming the returned partner list contains exactly the two in-range partners with per-partner amounts that sum to the overall expected revenue.

**Acceptance Scenarios**:

1. **Given** multiple partners have installments scheduled in the requested range, **When** the summary is requested, **Then** the response includes one entry per partner with a scheduled installment in that range, identifying the partner and the total amount that partner is scheduled to pay in the range.
2. **Given** a partner has more than one loan with installments scheduled in the range, **When** the summary is requested, **Then** that partner appears exactly once, with the amounts from all their loans combined.
3. **Given** a partner has no installment scheduled in the requested range, **When** the summary is requested, **Then** that partner does not appear in the list at all.
4. **Given** the per-partner amounts are added together, **When** compared to the reported expected revenue for the range, **Then** the two values match exactly.

---

### User Story 3 - Manager distinguishes money already received from money still to collect (Priority: P3)

Within the selected range, some scheduled installments have already been paid (fully or partially). A manager needs to see how much of the period's expected revenue has already landed and how much is still outstanding, both overall and per partner, so the dashboard reflects reality rather than only the original schedule.

**Why this priority**: Without it, a range covering past dates would overstate what is still collectible. It refines P1 and P2 but is not required for them to be useful on a forward-looking range.

**Independent Test**: Can be fully tested by taking a range where one installment is fully paid, one is partially paid, and one is untouched, then verifying the reported received and outstanding amounts split the expected revenue correctly, overall and per partner.

**Acceptance Scenarios**:

1. **Given** installments scheduled in the range with varying payment states, **When** the summary is requested, **Then** the response reports how much of the period's expected revenue has already been received and how much remains outstanding.
2. **Given** an installment scheduled in the range that has been partially paid, **When** the summary is requested, **Then** the paid part counts toward received and the remainder counts toward outstanding.
3. **Given** the received and outstanding amounts for the range, **When** they are added together, **Then** they equal the expected revenue for that range.
4. **Given** a partner entry in the list, **When** its received and outstanding amounts are added together, **Then** they equal that partner's scheduled amount for the range.

---

### Edge Cases

- **Empty range**: A range with no scheduled installments returns zeros and an empty partner list, not an error.
- **Inverted range**: An end date earlier than the start date is rejected as an invalid request.
- **Single-day range**: Start date equal to end date is valid and covers exactly that one day.
- **Canceled loans**: Installments belonging to canceled loans are excluded from every total and from the partner list — they will not be collected.
- **Fully settled loans**: A loan already marked as fully paid still contributes its in-range installments to expected revenue and to received (not outstanding), so historical ranges stay accurate.
- **Inactive partners**: A partner marked inactive who still has scheduled installments in the range is included — the debt is still owed.
- **Payment recorded outside the range**: A payment made on a date outside the range against an installment *scheduled* inside the range still counts as received for that range; attribution follows the installment's scheduled date, not the payment date.
- **Overpayment**: If recorded payments against an installment exceed its amount, the outstanding amount for that installment is treated as zero rather than negative.
- **Range spanning multiple months or years**: Supported; no implicit month or year boundary is applied.
- **Zero-interest loan**: Contributes to expected revenue with a profit contribution of zero.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a loan summary for an arbitrary date range, defined by a start date and an end date, both inclusive.
- **FR-002**: System MUST require both a start date and an end date, and MUST reject a request where the end date is earlier than the start date.
- **FR-003**: System MUST select the loan installments to summarize by their scheduled due date falling within the requested range.
- **FR-004**: System MUST report, for the requested range, the total expected revenue — the sum of the amounts of all selected installments.
- **FR-005**: System MUST report, for the requested range, the total expected profit — the interest portion of the selected installments — and the corresponding capital (principal) portion, such that capital plus profit equals expected revenue.
- **FR-006**: System MUST derive each installment's profit portion from its own loan's ratio of interest to total amount, so that loans with different interest rates contribute proportionally.
- **FR-007**: System MUST report, for the requested range, how much of the expected revenue has already been received and how much is still outstanding, where received plus outstanding equals expected revenue.
- **FR-008**: System MUST return a list of partners having at least one selected installment in the range, each entry identifying the partner and reporting that partner's scheduled amount, received amount, and outstanding amount for the range.
- **FR-009**: System MUST aggregate a partner's installments across all of that partner's loans into a single entry per partner.
- **FR-010**: System MUST exclude installments belonging to canceled loans from all totals and from the partner list.
- **FR-011**: System MUST report the number of installments and the number of distinct partners covered by the requested range.
- **FR-012**: System MUST return a successful response with zeroed totals and an empty partner list when no installments fall within the requested range.
- **FR-013**: System MUST restrict this summary to authenticated users, consistent with the existing loan endpoints.
- **FR-014**: All monetary values reported MUST be expressed in the same currency and precision as the underlying loan and installment amounts — including when a value is zero, which MUST still carry the standard two-decimal precision rather than a bare zero.
- **FR-015**: Each partner entry MUST report how many of that partner's installments fall within the requested range.
- **FR-016**: The partner list MUST be returned in a deterministic order — largest scheduled amount first, with equal amounts ordered by partner name — so repeated identical requests produce an identical list.
- **FR-017**: The response MUST echo the requested start date and end date, so a dashboard can confirm which range the figures describe.

### Key Entities *(include if feature involves data)*

- **Loan**: Existing entity. Supplies the principal amount, the total amount owed, and the loan status used to decide inclusion and to derive the interest-versus-capital split.
- **Loan Installment**: Existing entity. Its scheduled due date is the filter for the date range; its amount is the unit of expected revenue.
- **Loan Installment Payment**: Existing entity. Recorded payments against a selected installment determine how much of that installment is already received.
- **Partner**: Existing entity. The debtor grouping for the partner list; identified by name so the dashboard can display who to follow up with.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A manager can see the expected revenue, expected profit, and the full list of paying partners for any chosen date range in a single request, with no per-loan or per-partner follow-up requests needed.
- **SC-002**: For any requested range, the sum of the per-partner scheduled amounts equals the reported expected revenue exactly, with no rounding drift.
- **SC-003**: For any requested range, reported capital plus reported profit equals reported expected revenue, and reported received plus reported outstanding equals reported expected revenue.
- **SC-004**: 100% of the installments reflected in the summary have a scheduled date inside the requested range, and none belong to canceled loans.
- **SC-005**: A request covering a one-month range across the full loan book returns in under 1 second, and a 12-month range in under 2 seconds, measured end to end from the dashboard.
- **SC-006**: The number of database queries used to answer a request does not grow with the number of loans, partners, or installments in the range — a range covering ten times more installments issues the same number of queries.

## Assumptions

- **"Revenue" means scheduled installment amounts, not cash movements.** Expected revenue for a range is what is *due* in that range, based on installment due dates. This makes the summary forward-looking, matching the stated dashboard purpose ("how will be the revenues... partners that will pay").
- **"Profit" means the interest portion.** The principal returned by a partner is capital coming back, not earnings, so profit is the interest share of the installments due in the range. Each installment's profit share is derived from its loan's overall interest-to-total ratio. Both the capital portion and the profit portion are reported so the dashboard can show either.
- **Both dates are required.** No implicit default range (such as "current month") is applied; the dashboard always supplies an explicit range.
- **No partner filter in this feature.** The summary always covers all partners. Narrowing to a single partner is already served by the existing per-partner loan listing and the per-loan summary.
- **Not paginated.** The partner list is returned in full, consistent with existing list endpoints in this project.
- **Access follows existing loan endpoints.** Any authenticated user may request the summary; no new role restriction is introduced, since the existing loan read endpoints are not role-gated.
- **Existing capabilities are untouched.** The existing single-loan summary keeps its current shape and behavior; this feature adds a separate, period-level summary alongside it.
- **No new data is stored.** The summary is derived entirely from existing loans, installments, and payments; no new persistence model or migration is required.
