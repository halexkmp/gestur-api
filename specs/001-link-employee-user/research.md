# Phase 0 Research: Link Employee to User Account

All unknowns below were resolved by inspecting existing patterns in this codebase rather
than external research, since the stack, architecture, and conventions are fixed by
`CLAUDE.md` and `.specify/memory/constitution.md`. No `NEEDS CLARIFICATION` markers remain.

## Decision 1: Model relationship shape

**Decision**: Add a nullable, unique foreign key on `Employee` pointing to `User`:

```python
user = fields.ForeignKeyField("models.User", related_name="employee", null=True, unique=True)
```

**Rationale**:
- `null=True` mirrors the existing optional-FK precedent `Sale.partner` (`app/shared/db/models.py:77`), which is the codebase's established way to model "this link may or may not exist."
- `unique=True` enforces the spec's one-to-one constraint (FR-004: a user account may be linked to at most one employee) at the database level, so the invariant holds even under concurrent writes — not just inside application code.
- The FK lives on `Employee` (not as a reverse `OneToOneField` declared on `User`) to match this repo's convention that the "owning" side of a business relationship declares the `ForeignKeyField` (e.g. `SalaryAdvance.employee`, `Sale.partner`, `Sale.user`). Tortoise's `related_name="employee"` then exposes the reverse accessor from `User` without needing a second field declaration.

**Alternatives considered**:
- A dedicated `OneToOneField` on `User` — functionally equivalent, but this codebase never uses `OneToOneField` anywhere; introducing it for a single relation would violate Constitution IV (Consistency Over Cleverness) by adding a new ORM pattern where an existing one already fits.
- A many-to-many join table — rejected, since the spec is explicit about a one-to-one, optional relationship; a join table would allow multiplicities the spec forbids.

## Decision 2: Expressing "clear the user link" on update

**Problem**: The existing `update_employee` flow (and the identical pattern in
`app/slices/sales/update_sale`) treats an `Optional[T] = None` field as "not supplied,
leave unchanged" — the repository only assigns a field `if value is not None`. This means
a single `Optional[UUID]` field cannot, on its own, distinguish "the client didn't send
`user_id`" from "the client explicitly wants to clear the linked user" — both arrive as
`None`. The spec (User Story 2, Acceptance Scenario 3) explicitly requires supporting
clearing, so this ambiguity must be resolved.

**Decision**: Keep `user_id: Optional[UUID] = None` for "set/leave unchanged" exactly like
every other field, and thread one additional explicit, typed boolean parameter,
`clear_user: bool = False`, through schema → route → use case → repository. The route
derives it from the incoming request without exposing a new API field: it checks Pydantic
v2's `model_fields_set` to see whether the client's JSON body included the `user_id` key at
all, and whether the supplied value was `null`:

```python
clear_user = "user_id" in data.model_fields_set and data.user_id is None
```

So, from the API consumer's point of view, nothing changes about the contract shape:
omitting `user_id` leaves the link untouched; sending `"user_id": "<uuid>"` sets/changes it;
sending `"user_id": null` explicitly clears it. `clear_user` is purely an internal
implementation detail for disambiguating the two "empty" states — it is derived, not a new
request field, so `specs/api/employees.md` only needs to document the three JSON-visible
behaviors above.

**Rationale**: This satisfies Constitution II (explicit, typed parameters — no dict/kwargs)
without introducing a generic "unset sentinel" utility that would ripple into every other
optional field on every other update endpoint in the codebase (which would violate
Constitution IV's scoping rule: changes must be the minimum necessary for the feature at
hand). The change is confined to the one new field this feature introduces.

**Alternatives considered**:
- A shared "unset" sentinel default reused across all optional update fields — rejected as
  an unscoped refactor of stable, working code (every other field on `EmployeeUpdate` and
  every sibling `*Update` schema in the codebase) that this feature does not need to touch.
- A separate `DELETE /employees/{employee_id}/user` (or similar) endpoint dedicated to
  unlinking — rejected as unnecessary extra API surface when the existing partial-update
  `PUT` already covers every other optional field; adding a second endpoint for one field
  would be inconsistent with how every other employee attribute is cleared/changed today
  (there is no precedent for per-field unlink endpoints in this codebase).

## Decision 3: Validation and error responses for the linked user

**Decision**: Reuse the exact pattern already established in
`app/slices/partner_loan/create_loan` for validating a referenced entity:
1. Look the user up with `User.get_or_none(id=user_id)`; if absent, raise
   `ValueError("User not found")`.
2. Check no *other* employee already references that user
   (`Employee.exclude(id=employee_id).get_or_none(user=user)` on update;
   `Employee.get_or_none(user=user)` on create); if found, raise
   `ValueError("User is already linked to another employee")`.
3. In the route, catch `ValueError` and branch on message content exactly like
   `partner_loan/create_loan/ui/route.py` does: `"not found"` → `404`, everything else →
   `400`. The employee-not-found check on update keeps its current, separate `404` handling
   unchanged.

**Rationale**: This is a directly reusable, already-approved precedent in the same
codebase for "validate a referenced foreign entity exists, and validate a uniqueness/business
rule about that reference," including the HTTP status mapping. Reusing it satisfies
Constitution IV rather than inventing a new error-handling convention (e.g. `409 Conflict`,
which has no precedent anywhere in this codebase's `app/slices/`).

**Alternatives considered**:
- `409 Conflict` for the duplicate-link case — semantically arguable, but rejected because
  no endpoint in this codebase uses `409` today; `400` is the established status for
  non-404 business-rule `ValueError`s.

## Summary of Technical Context (no unknowns remain)

- **Language/Version**: Python 3.11+ (existing project runtime)
- **Primary Dependencies**: FastAPI, Tortoise-ORM, Aerich, Pydantic v2 (all already in `requirements.txt`; no new dependency needed)
- **Storage**: PostgreSQL via Tortoise-ORM, migration generated by `aerich migrate` (not hand-authored)
- **Testing**: N/A — project policy explicitly forbids adding tests for new feature work (Constitution, Development Workflow & Quality Gates)
- **Target Platform**: Linux server / Vercel Python serverless function (`api/index.py`)
- **Project Type**: Web service, single backend, Vertical Slice Architecture
- **Performance Goals**: None beyond existing endpoint responsiveness; no new performance target implied by the spec
- **Constraints**: One-to-one optional Employee↔User invariant enforced at the DB level (`unique=True`); no new third-party dependencies; schema change flows only through Aerich
- **Scale/Scope**: One new nullable+unique FK column on `Employee`; touches 4 existing slices (`create_employee`, `update_employee`, `get_employee`, `list_employees`) plus `specs/api/employees.md`; no new slice folder needed
