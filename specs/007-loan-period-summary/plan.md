# Implementation Plan: Loan Period Summary

**Branch**: `007-loan-period-summary` | **Date**: 2026-08-08 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/007-loan-period-summary/spec.md`

## Summary

Add a read-only, aggregate endpoint that answers "what will the loan book bring in between date A and date B?" for the dashboard: expected revenue, its capital/profit split, how much of it is already received versus still outstanding, and the list of partners scheduled to pay with per-partner amounts.

Technical approach: one new vertical slice, `app/slices/partner_loan/period_summary/`, following the shape of the existing `get_loan_summary` slice. A single repository query selects `LoanInstallment` rows by `due_date` within the inclusive range, excludes installments whose loan is `CANCELED`, and prefetches `loan__partner` and `payments`. The use case aggregates in Python (same style as `get_loan_summary`), deriving each installment's profit share from its own loan's interest-to-total ratio and grouping by partner. No new model, no migration.

## Technical Context

**Language/Version**: Python 3.12+ (local interpreter 3.14; existing bytecode artifacts are cpython-313)

**Primary Dependencies**: FastAPI, Tortoise-ORM, Pydantic v2 / pydantic-settings, python-jose (JWT) — no new dependency introduced

**Storage**: PostgreSQL via Tortoise-ORM. Reads only from existing tables `loan`, `loan_installment`, `loan_installment_payment`, `partner`. **No schema change, no Aerich migration.**

**Testing**: None. Project policy (constitution, "Development Workflow & Quality Gates") forbids adding automated tests for new feature work. Verification is manual, per `quickstart.md`.

**Target Platform**: Linux serverless function on Vercel (`api/index.py` → `app.main:app`)

**Project Type**: Web service (single backend, Vertical Slice Architecture)

**Performance Goals**: One database round trip for the range; response renders without visible dashboard delay (SC-005). Aggregation is O(installments in range × payments per installment) in Python.

**Constraints**: All money uses `Decimal` at 2 decimal places, **including zeros** — accumulators are seeded `Decimal("0.00")`, since `Decimal("0")` serializes as a bare `0` and would violate FR-014 on an empty range (see [data-model.md](./data-model.md) §Precision). The reported invariants must hold exactly — `capital + profit == expected_revenue`, `received + outstanding == expected_revenue`, `Σ partner.scheduled == expected_revenue` — which drives the rounding strategy in [research.md](./research.md) (§3).

**Scale/Scope**: Small loan book (tens of partners, hundreds of installments per range). No pagination, consistent with existing list endpoints.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate | Status |
|-----------|------|--------|
| I. Vertical Slice Architecture | Feature lives in one slice under `app/slices/partner_loan/period_summary/` with `ui/` + `application/` + `domain/` + `infra/`; dependencies flow UI → Application → Domain → Infra; no business rules in the repository; nothing added to `app/shared/` | ✅ PASS |
| II. Explicit Parameters | `PeriodSummary.execute(start_date: date, end_date: date)` — explicit typed params, no `dict`/`**kwargs`; Pydantic schemas confined to `ui/`, dataclass DTOs cross into `application/` | ✅ PASS |
| III. Documentation-First | `spec.md` authored first; this `plan.md` precedes implementation; `tasks.md` follows via `/speckit-tasks`; `specs/api/loans.md` update is an explicit, non-optional task | ✅ PASS |
| IV. Consistency Over Cleverness | Mirrors the existing `get_loan_summary` slice (repository → prefetch → dataclass DTO → Pydantic response) and the `filter_sales` date-range query pattern; introduces no new abstraction or library | ✅ PASS |
| V. Data & Persistence Discipline | No new model, no new column, no migration; money stays `Decimal` throughout | ✅ PASS |
| Workflow: no new tests | No test files will be added | ✅ PASS |
| Workflow: `specs/api/` sync | New route + new response schema ⇒ `specs/api/loans.md` MUST be updated in the same change | ⚠️ REQUIRED — tracked as a task, not a violation |

**Post-Phase-1 re-check**: Design artifacts introduce no new model, no new shared code, no new dependency, and no cross-slice import. All gates still PASS. Complexity Tracking is empty.

One deliberate touch outside the new slice folder is required: `app/slices/partner_loan/urls.py` must include the new router **before** `get_loan_router`, because `GET /loans/{loan_id}` would otherwise shadow the literal path `GET /loans/period-summary` and fail UUID parsing with a 422. See [research.md](./research.md) §2. This is a single added line placed in a specific position — the minimum change required for the route to be reachable, not a reorganization.

## Project Structure

### Documentation (this feature)

```text
specs/007-loan-period-summary/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── loans-period-summary.md   # Phase 1 output
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created here)
```

### Source Code (repository root)

```text
app/
├── slices/
│   └── partner_loan/
│       ├── urls.py                     # MODIFIED: include new router before get_loan_router
│       └── period_summary/             # NEW SLICE
│           ├── ui/
│           │   ├── route.py            # GET /loans/period-summary, query params, ValueError → 400
│           │   └── schemas.py          # LoanPeriodSummaryResponse, PartnerPeriodEntryResponse
│           ├── application/
│           │   └── use_case.py         # PeriodSummary.execute(start_date, end_date) + DTOs
│           ├── domain/
│           │   └── rules.py            # validate_date_range, installment_profit_share, received_for_installment
│           └── infra/
│               └── repository.py       # PeriodSummaryRepository.list_installments_in_range(...)
└── shared/                             # UNCHANGED

specs/
└── api/
    └── loans.md                        # MODIFIED: document the new endpoint + response shape
```

**Structure Decision**: Standard VSA slice inside the existing `partner_loan` context, named `period_summary` to sit alongside `get_loan_summary` without ambiguity. The `domain/rules.py` layer is included (unlike `get_loan_summary`, which has none) because this feature has three genuinely pure, framework-free rules worth isolating — range validation, the interest-share derivation, and the payment-allocation cap — matching the precedent set by `create_loan/domain/rules.py`.

## Complexity Tracking

> No constitution violations. Section intentionally empty.
