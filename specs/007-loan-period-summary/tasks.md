---

description: "Task list for Loan Period Summary"
---

# Tasks: Loan Period Summary

**Input**: Design documents from `/specs/007-loan-period-summary/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/loans-period-summary.md](./contracts/loans-period-summary.md), [quickstart.md](./quickstart.md)

**Tests**: NO test tasks. This project's constitution ("Development Workflow & Quality Gates") explicitly forbids adding automated tests for new feature work. Verification is the manual [quickstart.md](./quickstart.md) run in Phase 6.

**Organization**: Tasks are grouped by user story. Note the honest constraint recorded in "Parallel Opportunities" below — this feature is a single endpoint, so the three stories layer onto the *same* files and must be done in priority order, not in parallel.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Exact file paths are included in every task

## Path Conventions

Vertical Slice Architecture. All new code lives in `app/slices/partner_loan/period_summary/`; the only files touched outside it are `app/slices/partner_loan/urls.py` and `specs/api/loans.md`.

---

## Phase 1: Setup

**Purpose**: Create the slice skeleton

- [X] T001 Create the slice directory tree `app/slices/partner_loan/period_summary/` with `ui/`, `application/`, `domain/`, and `infra/` subdirectories (no `__init__.py` files — sibling slices under `app/slices/partner_loan/` use namespace packages)

**Note**: No dependency install, no `aerich migrate`, no lint config. This feature adds no model, no column, and no third-party dependency.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The data access and input validation every story needs

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 [P] Create `app/slices/partner_loan/period_summary/domain/rules.py` with `validate_date_range(start_date: date, end_date: date) -> None`, raising `ValueError("end_date must be on or after start_date")` when `end_date < start_date`; `start_date == end_date` is valid. Pure function, no framework imports — follow the style of `app/slices/partner_loan/create_loan/domain/rules.py`
- [X] T003 [P] Create `app/slices/partner_loan/period_summary/infra/repository.py` with `PeriodSummaryRepository.list_installments_in_range(start_date: date, end_date: date) -> list[LoanInstallment]` running a single query: `LoanInstallment.filter(due_date__gte=start_date, due_date__lte=end_date).exclude(loan__status=LoanStatus.CANCELED).prefetch_related("loan__partner", "payments").order_by("due_date", "installment_number")`. Persistence only — no aggregation, no business rules (Constitution Principle I). See [research.md](./research.md) §4

**Checkpoint**: The range can be queried and validated — user story implementation can begin

---

## Phase 3: User Story 1 - Manager sees expected revenue and profit for a period (Priority: P1) 🎯 MVP

**Goal**: A working `GET /loans/period-summary` returning expected revenue for the range plus its capital/profit split and the installment count.

**Independent Test**: Create loans with installments inside and outside a range, call the endpoint, and confirm `expected_revenue` equals the sum of in-range installment amounts and that `expected_capital + expected_profit == expected_revenue` exactly. Per [quickstart.md](./quickstart.md) scenarios 1, 2, 6, 7, 8.

### Implementation for User Story 1

- [X] T004 [US1] Add `installment_profit_share(amount: Decimal, principal_amount: Decimal, total_amount: Decimal) -> Decimal` to `app/slices/partner_loan/period_summary/domain/rules.py`, returning `amount * (total_amount - principal_amount) / total_amount` at **full Decimal precision with no rounding** (the caller quantizes once after summing). Guard `total_amount == 0` by returning `Decimal("0.00")`. Derive from the stored `principal_amount`/`total_amount` pair, never from `interest_rate` — see [research.md](./research.md) §3
- [X] T005 [US1] Create `app/slices/partner_loan/period_summary/application/use_case.py` with a `@dataclass LoanPeriodSummaryDTO` (`start_date`, `end_date`, `expected_revenue`, `expected_capital`, `expected_profit`, `installments_count`) and `class PeriodSummary` taking `PeriodSummaryRepository` in `__init__`. `execute(self, start_date: date, end_date: date) -> LoanPeriodSummaryDTO` — explicit typed params, no `dict`/`**kwargs` (Constitution Principle II) — calls `validate_date_range`, fetches via the repository, sums `installment.amount` into `expected_revenue`, accumulates `installment_profit_share(...)` unrounded then quantizes **once** to 2dp for `expected_profit`, and sets `expected_capital = expected_revenue - expected_profit`. **Seed every money accumulator as `Decimal("0.00")`, never `Decimal("0")`** — `Decimal` carries its scale through serialization, so a `Decimal("0")` seed renders an empty range as `0` instead of `0.00` and breaks FR-014 and INV-8 (see [data-model.md](./data-model.md) §Precision). `get_loan_summary/application/use_case.py` already seeds `total_paid = Decimal("0.00")`; follow it, along with its dataclass-DTO style. Satisfies INV-1
- [X] T006 [P] [US1] Create `app/slices/partner_loan/period_summary/ui/schemas.py` with `LoanPeriodSummaryResponse` (`start_date`, `end_date`, `expected_revenue`, `expected_capital`, `expected_profit`, `installments_count`) using `Decimal` for money and `class Config: from_attributes = True`, matching the schema style of `app/slices/partner_loan/get_loan_summary/ui/schemas.py`
- [X] T007 [US1] Create `app/slices/partner_loan/period_summary/ui/route.py` declaring `router = APIRouter()` and module-level `use_case = PeriodSummary(PeriodSummaryRepository())` (the wiring pattern used across this codebase). Add `@router.get("/period-summary", response_model=LoanPeriodSummaryResponse)` with **required** `start_date: date` and `end_date: date` query params and `current_user=Depends(get_current_user)` — no role guard, matching every other loans route (FR-013). Catch `ValueError` and raise `HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))`, as `create_loan`/`update_loan` do. Empty results return 200, never 404 (FR-012)
- [X] T008 [US1] Wire the new router into `app/slices/partner_loan/urls.py`: import it and add `loans_router.include_router(period_summary_router)` **positioned before `loans_router.include_router(get_loan_router)`**. FastAPI resolves in registration order, so if `GET /{loan_id}` is registered first it shadows the literal `period-summary` segment and returns 422 on UUID parsing. See [research.md](./research.md) §2. **Verify after this task that `GET /loans/{real-uuid}` still resolves correctly**
- [X] T009 [US1] Update `specs/api/loans.md`: add `GET /loans/period-summary` to the Endpoints list and a "Loan Period Summary" section documenting the two required query params, the response fields delivered so far, the 400/401/422 error cases, and the due-date-based selection rule with `CANCELED` loans excluded. Mandatory per Constitution Principle III — the slice change is not complete without it

**Checkpoint**: `GET /loans/period-summary?start_date=…&end_date=…` returns correct revenue/capital/profit totals. This is a shippable MVP on its own — the dashboard's headline numbers work without any per-partner breakdown.

---

## Phase 4: User Story 2 - Manager sees which partners will pay and how much (Priority: P2)

**Goal**: The same response additionally carries a per-partner list of who is scheduled to pay and how much.

**Independent Test**: Give two partners in-range installments and a third only out-of-range installments; confirm exactly the two appear, that a partner with two loans appears once with combined amounts, and that `sum(partners[].scheduled_amount) == expected_revenue`. Per [quickstart.md](./quickstart.md) scenario 3.

### Implementation for User Story 2

- [X] T010 [US2] In `app/slices/partner_loan/period_summary/application/use_case.py`, add a `@dataclass PartnerPeriodEntryDTO` (`partner_id`, `partner_name`, `scheduled_amount`, `installments_count`) and extend `LoanPeriodSummaryDTO` with `partners_count: int` and `partners: list[PartnerPeriodEntryDTO]`. Accumulate into a dict keyed by `installment.loan.partner.id` during the existing single pass so each partner appears exactly once regardless of how many loans they hold (FR-009, INV-7). `installments_count` per entry satisfies FR-015. Seed each partner's `scheduled_amount` accumulator as `Decimal("0.00")`, per T005. Sort the final list by `scheduled_amount` descending, tie-broken by `partner_name` ascending (FR-016, [research.md](./research.md) §8). Because partner subtotals sum the same 2dp installment amounts as `expected_revenue`, INV-3 holds by construction — do not re-round them
- [X] T011 [US2] In `app/slices/partner_loan/period_summary/ui/schemas.py`, add `PartnerPeriodEntryResponse` (`partner_id`, `partner_name`, `scheduled_amount`, `installments_count`) and add `partners_count: int` plus `partners: List[PartnerPeriodEntryResponse]` to `LoanPeriodSummaryResponse`
- [X] T012 [US2] Update the "Loan Period Summary" section of `specs/api/loans.md` with the `partners[]` array, its fields, its ordering guarantee, and the `sum(partners[].scheduled_amount) == expected_revenue` guarantee

**Checkpoint**: US1 and US2 both work — the dashboard shows totals *and* the collection list. Note that **FR-008 is only partially satisfied here**: partner entries carry `scheduled_amount` but not yet `received_amount`/`outstanding_amount`, which arrive in US3 (T014/T015). This is intentional incremental delivery, not a gap — do not mark FR-008 complete until Phase 5 lands.

---

## Phase 5: User Story 3 - Manager distinguishes money already received from money still to collect (Priority: P3)

**Goal**: Both the overall totals and each partner entry split into already-received and still-outstanding.

**Independent Test**: In one range, have a fully paid installment, a partially paid one, and an untouched one; confirm `received + outstanding == expected_revenue` overall and per partner. Per [quickstart.md](./quickstart.md) scenarios 4, 9.

### Implementation for User Story 3

- [X] T013 [US3] Add `received_for_installment(payment_amounts: list[Decimal], installment_amount: Decimal) -> Decimal` to `app/slices/partner_loan/period_summary/domain/rules.py`, returning `min(sum(payment_amounts), installment_amount)`. The cap is what keeps outstanding from going negative on an overpaid installment (INV-6, spec edge case "Overpayment")
- [X] T014 [US3] In `app/slices/partner_loan/period_summary/application/use_case.py`, extend `PartnerPeriodEntryDTO` with `received_amount` and `outstanding_amount`, and `LoanPeriodSummaryDTO` with `received_amount` and `outstanding_amount`. In the existing pass, compute each installment's receipt via `received_for_installment(...)` over its prefetched `payments`, accumulating into both the overall and the per-partner totals — this shared source is what makes INV-4 hold. Seed both received accumulators as `Decimal("0.00")`, per T005. Derive both outstanding figures by **subtraction** (`expected_revenue - received_amount`, `entry.scheduled_amount - entry.received_amount`), never by independent rounding (INV-2, INV-5). Do **not** filter payments by `payment_date` and do **not** read `installment.status` — attribution follows the installment's due date, per [data-model.md](./data-model.md)
- [X] T015 [US3] In `app/slices/partner_loan/period_summary/ui/schemas.py`, add `received_amount` and `outstanding_amount` to both `LoanPeriodSummaryResponse` and `PartnerPeriodEntryResponse`
- [X] T016 [US3] Update the "Loan Period Summary" section of `specs/api/loans.md` with `received_amount`/`outstanding_amount` at both levels, the `received + outstanding == expected_revenue` guarantee, and the note that payments made outside the range still count when the installment is due inside it

**Checkpoint**: All three stories functional. The response matches [contracts/loans-period-summary.md](./contracts/loans-period-summary.md) in full.

---

## Phase 6: Polish & Cross-Cutting Concerns

> **Status**: T017, T018, and T019 remain open — all three need a running server against a
> seeded Postgres, which was not available during implementation. The *arithmetic* half of
> T018 was verified DB-free by driving the real `PeriodSummary` use case with a fake
> repository: INV-1 through INV-8 all hold, including the uneven-division rounding case
> (`1000 @ 25% / 3`) and the raw-JSON check that an empty range serializes `"0.00"` rather
> than `"0"`. What is still unverified is everything that depends on the database: the
> repository's range filter and `CANCELED` exclusion, prefetch behaviour and query count,
> and end-to-end HTTP status codes.

- [ ] T017 Run every scenario in [quickstart.md](./quickstart.md) (1–12) against a local server and confirm each expectation, including scenario 10's check that the pre-existing loans routes still behave identically after the T008 router reordering, and scenario 11's inclusion rules (inactive partners included, fully `PAID` loans still counted, ranges spanning several months)
- [ ] T018 Verify all eight invariants from [data-model.md](./data-model.md) hold on real seeded data, especially INV-1/INV-2/INV-5 on a loan whose `total_amount` does not divide evenly by `installments_qty` (e.g. `principal_amount: 1000`, `interest_rate: 25`, `installments_qty: 3`) — the case most likely to expose a rounding mistake. Confirm INV-8 explicitly by inspecting the **raw JSON** of an empty range: every money field must read `0.00`, not `0` (FR-014)
- [ ] T019 Verify SC-005 and SC-006 against `app/slices/partner_loan/period_summary/`: time a one-month and a twelve-month range on a representative loan book (targets: under 1s and under 2s), and confirm the query count is flat — enable Tortoise query logging and check that widening the range issues the same number of queries, proving the `prefetch_related` in T003 has not degraded into per-installment lookups
- [X] T020 Run the `update-api-contract` skill to audit `specs/api/loans.md` against the implemented routes and schemas, confirming the contract matches `app/slices/partner_loan/` exactly
- [X] T021 Confirm the change added no test files, generated no Aerich migration, touched no file under `app/shared/`, and modified no file outside the new slice other than the single added line in `app/slices/partner_loan/urls.py` and the `specs/api/loans.md` update (Constitution Principles I, IV, V)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies
- **Foundational (Phase 2)**: depends on T001 — BLOCKS all user stories
- **User Story 1 (Phase 3)**: depends on Phase 2
- **User Story 2 (Phase 4)**: depends on Phase 3 — extends the DTO, schema, and aggregation loop that US1 creates
- **User Story 3 (Phase 5)**: depends on Phase 3; independent of US2 in logic, but edits the same two files, so it is sequenced after it
- **Polish (Phase 6)**: depends on every story you intend to ship

### Within Each User Story

Domain rules → use case → schemas → route → router wiring → contract update.

### Parallel Opportunities

**This feature has very little genuine parallelism, and the task list says so rather than pretending otherwise.** It is one endpoint whose three stories are successive layers on the same two files (`application/use_case.py`, `ui/schemas.py`). The template's usual "all stories run in parallel once foundational is done" does **not** apply here.

Actually parallelizable:

- **T002 and T003** — different files (`domain/rules.py`, `infra/repository.py`), no shared imports
- **T006** — `ui/schemas.py` has no import dependency on `use_case.py`, so it can be written alongside T005

Everything else is sequential. Splitting US2 and US3 across two developers would put both in `use_case.py` and `schemas.py` at once and produce conflicts for no scheduling gain.

---

## Parallel Example: Phase 2

```bash
# Both foundational tasks touch different files and can be done together:
Task: "Create domain/rules.py with validate_date_range in app/slices/partner_loan/period_summary/domain/rules.py"
Task: "Create PeriodSummaryRepository in app/slices/partner_loan/period_summary/infra/repository.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 only)

1. Phase 1 (T001) → Phase 2 (T002–T003) → Phase 3 (T004–T009)
2. **STOP and VALIDATE**: quickstart scenarios 1, 2, 6, 7, 8
3. The dashboard's revenue and profit tiles are live; `specs/api/loans.md` already documents them

### Incremental Delivery

1. Setup + Foundational → queryable, validated range
2. + US1 → totals and capital/profit split (**MVP, deployable**)
3. + US2 → per-partner collection list
4. + US3 → received vs. outstanding at both levels
5. Phase 6 → full quickstart pass and contract audit

Each increment leaves the endpoint working and its contract accurate, so you can stop after any story.

---

## Notes

- Every task edits files inside the new slice, except T008 (`urls.py`), the three `specs/api/loans.md` updates (T009, T012, T016), and the T020 contract audit.
- The contract update is folded into each story phase rather than deferred to the end, because each story changes the response shape and the constitution requires the contract to move in the same change.
- Money stays `Decimal` end to end, and two rules govern it: **derive one side of each pair by subtraction, never round both sides independently** ([research.md](./research.md) §3), and **seed every accumulator `Decimal("0.00")`, never `Decimal("0")`** ([data-model.md](./data-model.md) §Precision).
- Do not add tests. If a task seems to need one to be verifiable, raise it rather than silently adding or silently skipping verification.
- Commit after each task or logical group.
