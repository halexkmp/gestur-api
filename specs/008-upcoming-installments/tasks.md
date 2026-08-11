---

description: "Task list for Upcoming Loan Installments List"
---

# Tasks: Upcoming Loan Installments List

**Input**: Design documents from `/specs/008-upcoming-installments/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/loans-upcoming-installments.md](./contracts/loans-upcoming-installments.md), [quickstart.md](./quickstart.md)

**Tests**: NO test tasks. This project's constitution ("Development Workflow & Quality Gates") explicitly forbids adding automated tests for new feature work. Verification is the manual [quickstart.md](./quickstart.md) run, checkpointed per story and completed in Phase 6.

**Organization**: Tasks are grouped by user story. Note the honest constraint recorded in "Parallel Opportunities" below — this feature is a single endpoint, so US2 and US3 layer additional query parameters onto the *same four files* US1 creates. They must be done in priority order, not in parallel.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Exact file paths are included in every task

## Path Conventions

Vertical Slice Architecture. All new code lives in `app/slices/partner_loan/upcoming_installments/`; the only files touched outside it are `app/slices/partner_loan/urls.py` and `specs/api/loans.md`.

---

## Phase 1: Setup

**Purpose**: Create the slice skeleton

- [X] T001 Create the slice directory tree `app/slices/partner_loan/upcoming_installments/` with `ui/`, `application/`, `domain/`, and `infra/` subdirectories (no `__init__.py` files — every slice under `app/slices/` uses namespace packages; there are zero `__init__.py` files in the tree)

**Note**: No dependency install, no `aerich migrate`, no lint config. This feature adds no model, no column, and no third-party dependency ([plan.md](./plan.md) §Technical Context).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The pure rules and the data access every story needs

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 [P] Create `app/slices/partner_loan/upcoming_installments/domain/rules.py` with three pure functions, no framework imports (mirror the style of `app/slices/partner_loan/period_summary/domain/rules.py`):
  - `validate_date_range(start_date: date, end_date: date) -> None` — raise `ValueError("end_date must be on or after start_date")` when `end_date < start_date`; `start_date == end_date` is valid
  - `received_for_installment(payment_amounts: list[Decimal], installment_amount: Decimal) -> Decimal` — return `min(sum(payment_amounts, Decimal("0.00")), installment_amount)`. **Re-declare it here; do NOT import it from `period_summary/domain/rules.py`** — a cross-slice domain import violates Constitution Principle I ([research.md](./research.md) §6). Seed the sum with `Decimal("0.00")`, never `Decimal("0")` ([data-model.md](./data-model.md) §Precision)
  - `is_overdue_on(due_date: date, reference_date: date) -> bool` — return `due_date < reference_date`. Strictly earlier: an installment due on `reference_date` is NOT overdue (FR-008). Take the reference date as a parameter so the rule stays pure; the use case supplies `date.today()`. **The `_on` suffix is deliberate**: the DTO and the response schema both carry a field named `is_overdue`, and binding that name to a local in the use case would shadow the function for the entire scope and raise `UnboundLocalError` on the first row
- [X] T003 [P] Create `app/slices/partner_loan/upcoming_installments/infra/repository.py` with `UpcomingInstallmentsRepository.list_due_installments(self, start_date: date, end_date: date) -> list[LoanInstallment]` running a single query: `LoanInstallment.filter(due_date__gte=start_date, due_date__lte=end_date).exclude(loan__status=LoanStatus.CANCELED).exclude(status=LoanInstallmentStatus.PAID).prefetch_related("loan__partner", "payments").order_by("due_date", "loan_id", "installment_number")`. Persistence only — no aggregation, no business rules (Principle I). Satisfies FR-004 (canceled loans), FR-005 (settled installments) and FR-009 (ordering). Three points that are load-bearing:
  - the `PAID` exclusion selects on **status, not the payments sum** ([research.md](./research.md) §3)
  - the three-key ordering must be exactly this, because `limit` in Phase 6 depends on it being deterministic
  - **verify `order_by("loan_id")` resolves before moving on.** No existing slice orders by a foreign-key source column — `period_summary` orders by plain fields only — so this is the one unverified ORM assumption in the plan. If Tortoise rejects it, fall back to `"loan__id"`. Do not silently drop to a two-key ordering: that makes `limit` (T018) return different rows for the same request when several installments share a due date

**Checkpoint**: Installments can be selected and the derived values computed — user story implementation can begin

---

## Phase 3: User Story 1 - See which installments come due in a window (Priority: P1) 🎯 MVP

**Goal**: A working `GET /loans/upcoming-installments?start_date&end_date` returning one row per unsettled installment due in the window, across all loans and partners, with the owing partner named inline.

**Independent Test**: Seed loans for several partners with installments inside and outside a window, plus one canceled loan and one fully-paid installment. Call the endpoint and confirm only the in-window unsettled rows come back, ordered by due date, each with correct partner, amounts, and status. Per [quickstart.md](./quickstart.md) scenarios 1, 2, 3, 8, 10.

### Implementation for User Story 1

- [X] T004 [P] [US1] Create `app/slices/partner_loan/upcoming_installments/ui/schemas.py` with `class UpcomingInstallmentResponse(BaseModel)` carrying exactly the FR-006 fields: `installment_id: UUID`, `loan_id: UUID`, `partner_id: UUID`, `partner_name: str`, `installment_number: int`, `due_date: date`, `amount: Decimal`, `paid_amount: Decimal`, `remaining_amount: Decimal`, `status: LoanInstallmentStatus`, `is_overdue: bool`. Include `class Config: from_attributes = True`, matching `period_summary/ui/schemas.py`. The id field is `installment_id`, not `id` — three ids sit side by side in one row ([research.md](./research.md) §7). Do NOT expose `payment_date`: it is only ever set on fully-settled installments, all of which are filtered out, so it would be `null` on every row ([data-model.md](./data-model.md))
- [X] T005 [US1] Create `app/slices/partner_loan/upcoming_installments/application/use_case.py` with a `@dataclass UpcomingInstallmentDTO` (same eleven fields as the response schema) and `class ListUpcomingInstallments` taking `UpcomingInstallmentsRepository` in `__init__`. `execute(self, start_date: date, end_date: date) -> list[UpcomingInstallmentDTO]` — explicit typed params, no `dict`/`**kwargs` (Principle II). Call `validate_date_range`, fetch via the repository, resolve `reference_date = date.today()` **once before the loop** so every row in one response is judged against the same date, then map each installment to a DTO: `paid_amount = received_for_installment([p.amount for p in installment.payments], installment.amount)`, `remaining_amount = installment.amount - paid_amount`, `is_overdue = is_overdue_on(installment.due_date, reference_date)`, with `partner_id`/`partner_name` read from `installment.loan.partner`. Satisfies FR-001, FR-006, FR-007, FR-008. No rounding anywhere — every value is a sum or difference of 2dp operands and is exact by construction ([data-model.md](./data-model.md) §Precision). Follow the DTO style of `period_summary/application/use_case.py`
- [X] T006 [US1] Create `app/slices/partner_loan/upcoming_installments/ui/route.py` — copy the shape of `period_summary/ui/route.py` exactly: module-level `router = APIRouter()` and `use_case = ListUpcomingInstallments(UpcomingInstallmentsRepository())` wired at import time, then `@router.get("/upcoming-installments", response_model=List[UpcomingInstallmentResponse])` with `start_date: date = Query(...)`, `end_date: date = Query(...)`, `current_user=Depends(get_current_user)` — both dates required, per FR-002. Wrap the call in `try/except ValueError` → `HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))`, satisfying FR-003 and SC-005. Returning `[]` for a window with no matches (FR-013) needs no code — it falls out of the empty query result. Auth is `get_current_user` only — **no role guard**, matching `period_summary` (FR-014)
- [X] T007 [US1] Wire the router in `app/slices/partner_loan/urls.py`: import it as `upcoming_installments_router` and `loans_router.include_router(...)` it **before** `get_loan_router`, next to `period_summary_router`. Extend the existing comment above `period_summary_router` (`urls.py:17-18`) to cover both literal paths. Registering after `get_loan_router` makes `GET /{loan_id}` swallow the literal segment and return 422 ([research.md](./research.md) §2). This is the only file outside the slice touched by US1 — add the two lines, change nothing else
- [X] T008 [US1] Validate US1 by running [quickstart.md](./quickstart.md) scenarios 1 (in-window rows only), 2 (ordering and per-row arithmetic), 3 (inclusive boundary dates), 8 (empty window returns `[]`, not an error) and 10 (route reachable — a 422 about UUID parsing means T007 was placed wrong)

**Checkpoint**: `GET /loans/upcoming-installments` is fully functional for the default in-window case and independently demoable. This is the MVP.

---

## Phase 4: User Story 2 - Include what is already overdue (Priority: P2)

**Goal**: An opt-in `include_overdue` flag that additionally returns every unsettled installment due before the window start, with no lower cutoff.

**Independent Test**: With at least one unsettled installment due before the window start, call the endpoint twice — flag off, then on — and confirm the overdue row is absent the first time and present, flagged `is_overdue: true` and sorted ahead of the in-window rows, the second time. Per [quickstart.md](./quickstart.md) scenarios 4 and 5.

⚠️ Modifies files created in Phase 3. Complete US1 first.

### Implementation for User Story 2

- [X] T009 [US2] Add `resolve_lower_bound(start_date: date, include_overdue: bool) -> Optional[date]` to `app/slices/partner_loan/upcoming_installments/domain/rules.py`, returning `None` when `include_overdue` is true (no lower bound at all — the window reaches back over the entire loan history, per the user's confirmed decision on FR-010) and `start_date` otherwise. This rule is what keeps the `include_overdue` *business* concept out of the repository ([research.md](./research.md) §5)
- [X] T010 [US2] Widen `list_due_installments` in `app/slices/partner_loan/upcoming_installments/infra/repository.py` to accept `start_date: Optional[date]`. Build the queryset as `LoanInstallment.filter(due_date__lte=end_date).exclude(...).exclude(...)`, then apply `.filter(due_date__gte=start_date)` **only when `start_date is not None`**, before the `prefetch_related`/`order_by` chain. The repository must never see the `include_overdue` boolean — it receives an already-resolved bound (Principle I)
- [X] T011 [US2] Add `include_overdue: bool = False` to `ListUpcomingInstallments.execute(...)` in `app/slices/partner_loan/upcoming_installments/application/use_case.py`. Call `validate_date_range` **unchanged** — `start_date` stays required and the reversed-range check still applies even when the flag makes it a non-bound (contract: "Ignored as a bound when `include_overdue=true`, but still required"). Pass `resolve_lower_bound(start_date, include_overdue)` to the repository in place of `start_date`. Leave `is_overdue` computation alone: it is judged against today independently of the flag, so in-window rows can legitimately come back `is_overdue: true` with the flag off (FR-008, [research.md](./research.md) §4)
- [X] T012 [US2] Add `include_overdue: bool = Query(False)` to the route in `app/slices/partner_loan/upcoming_installments/ui/route.py` and forward it to `use_case.execute(...)`. Default is `False` — the endpoint must behave exactly as it did after US1 when the parameter is omitted
- [X] T013 [US2] Validate US2 by running [quickstart.md](./quickstart.md) scenarios 4 (flag off vs on; the second result must be a strict superset, extra rows all `is_overdue: true` and sorted first, no settled past installment in either) and 5 (`is_overdue` judged against today, not the window)

**Checkpoint**: Both the in-window list and the opt-in overdue look-back work; US1 behavior is unchanged when the flag is omitted.

---

## Phase 5: User Story 3 - Narrow the list to one partner (Priority: P3)

**Goal**: An optional `partner_id` filter restricting the same window view to a single partner.

**Independent Test**: Call the same window with and without the filter and confirm the filtered result is exactly the subset belonging to that partner; confirm a partner with nothing due, and an unknown partner id, both return `200` with `[]`. Per [quickstart.md](./quickstart.md) scenario 6.

⚠️ Modifies files touched in Phases 3-4. Complete US1 and US2 first.

### Implementation for User Story 3

- [X] T014 [US3] Add `partner_id: Optional[UUID]` to `list_due_installments` in `app/slices/partner_loan/upcoming_installments/infra/repository.py`, applying `.filter(loan__partner_id=partner_id)` only when it is not `None`, alongside the conditional lower bound from T010 (FR-011). Confirm the relation traversal resolves — `period_summary` traverses `loan__status`, but not through to a related model's id — and fall back to `loan__partner__id` if it does not. Do **not** add an existence check — `list_loans` filters by partner without one, and an unknown partner is answered with an empty list, not a 404 ([research.md](./research.md) §8)
- [X] T015 [US3] Add `partner_id: Optional[UUID] = None` to `ListUpcomingInstallments.execute(...)` in `app/slices/partner_loan/upcoming_installments/application/use_case.py` and pass it straight through to the repository. No validation and no extra query — the filter is a pure narrowing of the result set
- [X] T016 [US3] Add `partner_id: Optional[UUID] = Query(None)` to the route in `app/slices/partner_loan/upcoming_installments/ui/route.py` and forward it. FastAPI returns `422` on a malformed UUID; a well-formed but unknown id must return `200` with `[]`
- [X] T017 [US3] Validate US3 by running [quickstart.md](./quickstart.md) scenario 6 — filtered subset, empty array for a partner with nothing due, and empty array (**not** `404`) for an unknown partner id

**Checkpoint**: All three user stories are independently functional.

---

## Phase 6: Cross-Cutting Requirements, Contract Sync & Validation

**Purpose**: The one functional requirement that belongs to no single story, plus the mandatory contract sync and full validation

**⚠️ NOT optional polish.** This phase carries two hard MUSTs from the spec: **FR-012** (the `limit` parameter, T018-T019) and **FR-015** (the `specs/api/loans.md` sync, T020). `limit` has no owning user story only because it is a convenience applied to all three, not because it is discretionary. Stopping after US3 leaves the feature incomplete against the spec.

- [X] T018 Add `limit: Optional[int]` to `list_due_installments` in `app/slices/partner_loan/upcoming_installments/infra/repository.py`, applying `.limit(limit)` **after** `order_by` and only when it is not `None` (FR-012). Truncating in SQL rather than slicing in Python is the point: `include_overdue=true` has no lower bound, so Python-side slicing would load the entire loan history to render a handful of rows ([research.md](./research.md) §5)
- [X] T019 Add `limit: Optional[int] = None` to `ListUpcomingInstallments.execute(...)` in `app/slices/partner_loan/upcoming_installments/application/use_case.py` and `limit: Optional[int] = Query(None, ge=1)` to the route in `app/slices/partner_loan/upcoming_installments/ui/route.py`, forwarding it through. Use FastAPI's `ge=1` rather than a domain rule — `limit` is an input-shape constraint with no business meaning, so `422` is the honest status for `limit=0` ([research.md](./research.md) §8)
- [X] T020 Update `specs/api/loans.md` — **mandatory, not optional** (FR-015, Constitution Principle III; a slice change is not complete until its contract file reflects it). Add `GET /loans/upcoming-installments` to the endpoint list at the top of the file, then a new section after "Loan Period Summary" documenting: the four query parameters with their defaults, the flat-array row shape, the selection rule (not `CANCELED`, not `PAID`, `due_date <= end_date`, lower bound unless `include_overdue`), the three-key ordering, the per-row guarantees, and the `400`/`401`/`422` cases. Carry over the reconciliation note from [contracts/loans-upcoming-installments.md](./contracts/loans-upcoming-installments.md) verbatim — including the `PATCH /pay` exception. No enum changed, so `specs/api/shared.md` is **not** touched
- [X] T021 Run the full [quickstart.md](./quickstart.md) suite end to end, including the scenarios not covered by a per-story checkpoint: 7 (`limit` returns the earliest-due N and is stable across repeated identical requests), 9 (all four error cases: `400` reversed range, `422` missing `end_date`, `422` `limit=0`, `401` no token) 11 (reconciliation against `GET /loans/period-summary`, with the documented `PATCH /pay` exception) and 12 (query count stays constant as the row count grows — the only check that verifies SC-004, since "no perceptible wait" is really "no N+1")
- [X] T022 Final constitution compliance check against [plan.md](./plan.md) §Constitution Check: no `__init__.py` added; no file created under `app/shared/`; no import from another slice; no `dict`/`**kwargs` crossing a layer boundary; no Pydantic schema referenced outside `ui/`; no business rule in `infra/`; no test file added; no migration generated; `app/slices/partner_loan/urls.py` and `specs/api/loans.md` are the only files changed outside the new slice directory

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies — T001 first
- **Foundational (Phase 2)**: depends on T001 — **blocks all user stories**
- **User Story 1 (Phase 3)**: depends on Phase 2. Delivers the MVP
- **User Story 2 (Phase 4)**: depends on US1 — it modifies the four files US1 creates
- **User Story 3 (Phase 5)**: depends on US2 — T014 edits the same repository signature T010 widened
- **Polish (Phase 6)**: T018/T019 depend on US3; T020 depends on every parameter being final; T021 depends on all of the above

### Within Each User Story

- Rules → repository → use case → route → router wiring → validate
- The route is wired last within US1 so the endpoint is never reachable in a half-built state

### Task-Level Dependencies

```text
T001 ─┬─> T002 (rules) ──────┐
      └─> T003 (repository) ─┤
                             ├─> T005 (use case) ─> T006 (route) ─> T007 (urls) ─> T008 ✅ MVP
              T004 (schemas) ┘
T008 ─> T009 ─> T010 ─> T011 ─> T012 ─> T013 ✅ US2
T013 ─> T014 ─> T015 ─> T016 ─> T017 ✅ US3
T017 ─> T018 ─> T019 ─> T020 ─> T021 ─> T022 ✅ done
```

### Parallel Opportunities

Honest assessment: **this feature is close to fully sequential.** It is one endpoint in one slice, and the three user stories are three query parameters on the same four files, so they cannot be split across developers without constant conflicts.

The only genuine parallelism:

- **T002 and T003** — different files (`domain/rules.py`, `infra/repository.py`), neither depends on the other
- **T004** — `ui/schemas.py` is independent of everything in Phase 2 and can be written at any point before T006

Everything else touches a file that an earlier task in the chain has to have finished. Do not manufacture further `[P]` markers here; the cost of two people editing `use_case.py` and `route.py` in alternating passes exceeds the benefit.

---

## Parallel Example: Phase 2 + T004

```bash
# The three genuinely independent file creations:
Task: "Create domain/rules.py with validate_date_range, received_for_installment, is_overdue"   # T002
Task: "Create infra/repository.py with UpcomingInstallmentsRepository.list_due_installments"    # T003
Task: "Create ui/schemas.py with UpcomingInstallmentResponse"                                    # T004
```

---

## Implementation Strategy

### MVP First (User Story 1 only)

1. Phase 1: Setup (T001)
2. Phase 2: Foundational (T002-T003) — blocks everything
3. Phase 3: User Story 1 (T004-T008)
4. **STOP and VALIDATE**: quickstart scenarios 1, 2, 3, 8, 10
5. Deploy/demo — the dashboard can already answer "what is coming due in this window?", which is the question that motivated the feature

### Incremental Delivery

1. Setup + Foundational → slice skeleton with rules and query in place
2. US1 → validate → deploy (**MVP**)
3. US2 → validate → deploy (overdue look-back, default behavior unchanged)
4. US3 → validate → deploy (partner filter)
5. Polish → `limit`, contract sync, full quickstart run

Each increment is additive: US2 and US3 introduce parameters that default to the previous behavior, so no earlier scenario changes result.

### Parallel Team Strategy

Not applicable. One developer, sequentially — see "Parallel Opportunities". If a second person is available, the highest-value split is having them run the [quickstart.md](./quickstart.md) checkpoint for story N while story N+1 is being written.

---

## Verification note (how T008 / T013 / T017 / T021 were actually run)

No live Postgres or auth token was available in the implementation session, so the quickstart
was **not** executed as written (curl against a running server). Instead the same scenarios
were driven against a sqlite in-memory database with seeded loans, partners, installments and
payments, calling the use case directly, plus a FastAPI `TestClient` pass for the HTTP-layer
checks that need no database. Verification scripts live in the session scratchpad, not in the
repo — the constitution forbids adding test files.

Covered and passing: selection (in-window only, canceled loans and `PAID` installments
excluded), ordering, per-row arithmetic including the overpayment cap, `is_overdue` with the
due-today boundary, `include_overdue` superset behavior, partner filter including the unknown-id
empty result, `limit` determinism, empty window, reversed-range `ValueError`, route registered
ahead of `GET /{loan_id}`, `401` without a token, the full OpenAPI parameter and row shape, and
constant SQL statement count as row count grows (12 rows → 4 statements, 60 rows → 4).

**Still worth running against real data**: the end-to-end curl flow with a genuine token
(quickstart scenarios 1-12), which is the only way to exercise Postgres-specific behavior,
`422` responses behind a valid token, and real loan data created through `POST /loans/`.

## Notes

- `[P]` tasks = different files, no dependencies
- `[Story]` label maps a task to a user story for traceability
- Commit after each task or logical group; mark tasks `[X]` in this file immediately as they complete (Constitution Principle III)
- **No test files.** If a task seems to need one to be verifiable, surface the tension rather than silently adding a test or silently skipping verification (Constitution, "Development Workflow & Quality Gates")
- **Known, deliberate divergence**: `PATCH /loan-installments/{id}/pay` marks an installment `PAID` without writing a payment row, while `period_summary` derives `received_amount` from payment rows only. This endpoint trusts status, so the two disagree about such installments and SC-002's reconciliation does not hold for them. Documented in [research.md](./research.md) §3 and carried into the contract by T020. **Do not "fix" either write path inside this feature** (Principle IV) — it is worth a separate follow-up
