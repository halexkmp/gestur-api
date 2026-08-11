# Implementation Plan: Upcoming Loan Installments List

**Branch**: `008-upcoming-installments` | **Date**: 2026-08-10 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/008-upcoming-installments/spec.md`

## Summary

Add a read-only endpoint that answers "which installments still have to be collected between date A and date B?" — one row per installment, across every loan and partner, with the owing partner named inline. It is the row-level counterpart to the aggregate `GET /loans/period-summary` shipped in 007: same window, but individual obligations instead of totals. An opt-in `include_overdue` flag additionally pulls in every unsettled installment due before the window start, with no lower cutoff.

Technical approach: one new vertical slice, `app/slices/partner_loan/upcoming_installments/`, shaped exactly like the sibling `period_summary` slice. A single repository query selects `LoanInstallment` rows with `due_date <= end_date`, excludes `CANCELED` loans and `PAID` installments, applies an optional lower bound / partner filter / limit in SQL, and prefetches `loan__partner` and `payments`. The use case maps each row to a DTO, deriving `paid_amount` (capped at the installment amount), `remaining_amount`, and `is_overdue`. No new model, no migration, no new dependency.

## Technical Context

**Language/Version**: Python 3.12+ (local interpreter 3.14; existing bytecode artifacts are cpython-313)

**Primary Dependencies**: FastAPI, Tortoise-ORM, Pydantic v2 / pydantic-settings, python-jose (JWT) — no new dependency introduced

**Storage**: PostgreSQL via Tortoise-ORM. Reads only from existing tables `loan`, `loan_installment`, `loan_installment_payment`, `partner`. **No schema change, no Aerich migration.**

**Testing**: None. Project policy (constitution, "Development Workflow & Quality Gates") forbids adding automated tests for new feature work. Verification is manual, per [quickstart.md](./quickstart.md).

**Target Platform**: Linux serverless function on Vercel (`api/index.py` → `app.main:app`)

**Project Type**: Web service (single backend, Vertical Slice Architecture)

**Performance Goals**: One database round trip per request, with `loan__partner` and `payments` prefetched so row count does not drive query count. `limit` is applied in SQL, which is what keeps `include_overdue=true` — an unbounded look-back — from loading the entire loan history to render five rows.

**Constraints**: All money uses `Decimal` at 2 decimal places **including zeros**; the `paid_amount` accumulator is seeded `Decimal("0.00")`, since `Decimal("0")` serializes as a bare `0` and unpaid installments are the common case here (see [data-model.md](./data-model.md) §Precision). No rounding step exists anywhere in this feature — every value is a sum or difference of 2dp operands, so precision is exact by construction. Ordering must be fully deterministic (`due_date`, `loan_id`, `installment_number`) or `limit` returns unstable results.

**Scale/Scope**: Small loan book (tens of partners, hundreds of installments per window). No pagination, consistent with every other listing in this project; `limit` covers the "next few" case.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate | Status |
|-----------|------|--------|
| I. Vertical Slice Architecture | Feature lives in one slice under `app/slices/partner_loan/upcoming_installments/` with `ui/` + `application/` + `domain/` + `infra/`; dependencies flow UI → Application → Domain → Infra; the `include_overdue` business rule is resolved in the use case so the repository sees only a persistence-level bound; nothing added to `app/shared/`; no cross-slice import | ✅ PASS |
| II. Explicit Parameters | `ListUpcomingInstallments.execute(start_date: date, end_date: date, include_overdue: bool, partner_id: Optional[UUID], limit: Optional[int])` — explicit typed params, no `dict`/`**kwargs`; Pydantic schemas confined to `ui/`, dataclass DTOs cross into `application/`. **This is the final, post-Phase-6 signature**; [tasks.md](./tasks.md) builds it incrementally, starting at two parameters in US1 and widening once per story, so a mid-implementation signature legitimately has fewer | ✅ PASS |
| III. Documentation-First | `spec.md` authored first; this `plan.md` precedes implementation; `tasks.md` follows via `/speckit-tasks`; the `specs/api/loans.md` update is FR-015, an explicit non-optional task | ✅ PASS |
| IV. Consistency Over Cleverness | Mirrors the `period_summary` slice file-for-file (repository → prefetch → dataclass DTO → Pydantic response, `ValueError` → `400` in the route); flat-array response matches every existing list endpoint; introduces no new abstraction or library | ✅ PASS |
| V. Data & Persistence Discipline | No new model, no new column, no migration; money stays `Decimal` throughout; `is_overdue` and `remaining_amount` are computed per request, deliberately not persisted | ✅ PASS |
| Workflow: no new tests | No test files will be added; acceptance scenarios are manual steps in `quickstart.md` | ✅ PASS |
| Workflow: `specs/api/` sync | New route + new response schema ⇒ `specs/api/loans.md` MUST be updated in the same change. No enum change, so `shared.md` is untouched | ⚠️ REQUIRED — tracked as a task, not a violation |

**Post-Phase-1 re-check**: Design artifacts introduce no new model, no new shared code, no new dependency, and no cross-slice import. All gates still PASS. Complexity Tracking is empty.

Two deliberate notes on scope:

1. **One touch outside the new slice folder.** `app/slices/partner_loan/urls.py` must include the new router **before** `get_loan_router`, because `GET /loans/{loan_id}` would otherwise shadow the literal path `GET /loans/upcoming-installments` and fail UUID parsing with a 422. The file already carries a comment about this exact trap from 007. One added line in one specific position — the minimum change for the route to be reachable, not a reorganization.

2. **A pre-existing inconsistency is flagged, not fixed.** `PATCH /loan-installments/{id}/pay` marks an installment `PAID` without writing a payment row, while `period_summary` derives `received_amount` from payment rows only. The two therefore disagree about such an installment. This feature selects on `status != PAID` (the operator's explicit signal — see [research.md](./research.md) §3), which means SC-002's reconciliation with the period summary holds for everything settled through `POST .../payments` but not for installments closed through `PATCH /pay`. Correcting either write path is outside this feature's scope under Principle IV; the divergence is documented in the contract and in `quickstart.md` §11 so the dashboard does not read it as a bug. **Worth raising as a separate follow-up.**

## Project Structure

### Documentation (this feature)

```text
specs/008-upcoming-installments/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── loans-upcoming-installments.md   # Phase 1 output
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created here)
```

### Source Code (repository root)

```text
app/
├── slices/
│   └── partner_loan/
│       ├── urls.py                          # MODIFIED: include new router before get_loan_router
│       └── upcoming_installments/           # NEW SLICE
│           ├── ui/
│           │   ├── route.py                 # GET /loans/upcoming-installments, query params, ValueError → 400
│           │   └── schemas.py               # UpcomingInstallmentResponse
│           ├── application/
│           │   └── use_case.py              # ListUpcomingInstallments.execute(...) + UpcomingInstallmentDTO
│           ├── domain/
│           │   └── rules.py                 # validate_date_range, resolve_lower_bound,
│           │                                # received_for_installment, is_overdue
│           └── infra/
│               └── repository.py            # UpcomingInstallmentsRepository.list_due_installments(...)
└── shared/                                  # UNCHANGED

specs/
└── api/
    └── loans.md                             # MODIFIED: document the new endpoint + row shape
```

**Structure Decision**: Standard VSA slice inside the existing `partner_loan` context, named `upcoming_installments` so it reads as distinct from both `list_loan_installments` (per-loan) and `period_summary` (aggregate). The `domain/rules.py` layer is included, matching `period_summary`, because this feature has four genuinely pure, framework-free rules worth isolating: range validation, resolving `include_overdue` into a lower bound, the payment-allocation cap, and the overdue date test.

`received_for_installment` is re-declared here rather than imported from `period_summary/domain/rules.py`. A cross-slice import into another feature's domain layer is exactly the coupling Principle I exists to prevent, and `app/shared/` is reserved by the constitution for stable cross-cutting concerns — not feature logic that moves when business rules move. Reasoning in [research.md](./research.md) §6.

## Complexity Tracking

> No constitution violations. Section intentionally empty.
