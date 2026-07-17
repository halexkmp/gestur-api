---

description: "Task list template for feature implementation"
---

# Tasks: Link Employee to User Account

**Input**: Design documents from `/specs/001-link-employee-user/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/employees.md, quickstart.md — all present

**Tests**: Not included. Project policy explicitly forbids adding tests for new feature work (`.specify/memory/constitution.md`, Development Workflow & Quality Gates); this is confirmed, not an oversight.

**Organization**: Tasks are grouped by user story (from spec.md, priority order P1 → P2 → P3) to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on an incomplete task)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Every task includes its exact file path

## Path Conventions

Existing single-project FastAPI backend, Vertical Slice Architecture. No new project
structure is introduced — every task below edits a file inside an already-existing slice
folder (`app/slices/employees/<feature>/...`) or the shared model file
(`app/shared/db/models.py`), per plan.md's Project Structure section.

---

## Phase 1: Setup

No setup tasks are required. This feature extends existing slices using dependencies
already present in `requirements.txt` (FastAPI, Tortoise-ORM, Aerich, Pydantic v2) — see
plan.md's Technical Context and research.md. Proceed directly to Foundational.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The shared `Employee.user` relationship that every user story depends on to
create, edit, or view the association.

**⚠️ CRITICAL**: No user story task can begin until this phase is complete.

- [ ] T001 Add a nullable, unique `user` foreign key field to the `Employee` model in `app/shared/db/models.py`: `user = fields.ForeignKeyField("models.User", related_name="employee", null=True, unique=True)` (per data-model.md and research.md Decision 1)
- [ ] T002 Generate and apply the Aerich migration for the new field (`aerich migrate`, then `aerich upgrade`) — do not hand-author the migration file (depends on T001)

**Checkpoint**: `Employee` rows can now store an optional, unique link to a `User`. User story implementation can begin.

---

## Phase 3: User Story 1 - Link a user account while creating an employee (Priority: P1) 🎯 MVP

**Goal**: HR can supply an existing user's id when creating a new employee, and the
created employee record reflects that link (or reflects no link, if omitted).

**Independent Test**: `POST /employees/` with an existing, unlinked `user_id` returns an
employee whose response includes that `user_id`; omitting it returns `user_id: null`;
reusing an already-linked or unknown `user_id` is rejected. Fully verifiable from the
create response alone (see quickstart.md Scenarios 1-4).

### Implementation for User Story 1

- [ ] T003 [P] [US1] Add `user_id: Optional[UUID] = None` to `CreateEmployeeRequest` and `user_id: Optional[UUID]` to `EmployeeResponse` in `app/slices/employees/create_employee/ui/schemas.py`
- [ ] T004 [P] [US1] Add a `user_id: UUID | None = None` parameter to `CreateEmployee.execute` in `app/slices/employees/create_employee/application/use_case.py`: when provided, look up the `User` (`User.get_or_none(id=user_id)`) and raise `ValueError("User not found")` if absent, then check no other `Employee` already references it (`Employee.get_or_none(user_id=user_id)`) and raise `ValueError("User is already linked to another employee")` if found, before delegating to the repository (per research.md Decision 3)
- [ ] T005 [P] [US1] Add a `user_id: UUID | None = None` parameter to `CreateEmployeeRepository.create` in `app/slices/employees/create_employee/infra/repository.py`, passing it through to `Employee.create(...)`
- [ ] T006 [US1] Update `app/slices/employees/create_employee/ui/route.py` to pass `user_id=data.user_id` into the use case call, and catch `ValueError` mapping "not found" messages to `404` and any other message to `400` (mirror `app/slices/partner_loan/create_loan/ui/route.py`'s existing pattern); depends on T003, T004, T005
- [ ] T007 [P] [US1] Update the `POST /employees/` section of `specs/api/employees.md` to document the new optional `user_id` request field, the `user_id` response field, and the `404`/`400` error cases (per contracts/employees.md)

**Checkpoint**: User Story 1 is fully functional and independently testable/deployable as an MVP.

---

## Phase 4: User Story 2 - Link, change, or remove a user account on an existing employee (Priority: P2)

**Goal**: HR can add, change, or clear an employee's linked user account via the existing
edit endpoint, without disturbing any other field's current partial-update behavior.

**Independent Test**: `PUT /employees/{id}` with a new `user_id` sets/changes the link;
with `"user_id": null` clears it; omitting the key entirely leaves it untouched; invalid or
already-linked ids are rejected. Verifiable using employees created either before or after
US1 ships, since the underlying field already exists after Phase 2 (see quickstart.md
Scenarios 5-7).

### Implementation for User Story 2

- [ ] T008 [P] [US2] Add `user_id: Optional[UUID] = None` to `EmployeeUpdate` and `user_id: Optional[UUID]` to `EmployeeResponse` in `app/slices/employees/update_employee/ui/schemas.py`
- [ ] T009 [P] [US2] Add `user_id: Optional[UUID] = None` and `clear_user: bool = False` parameters to `UpdateEmployee.execute` in `app/slices/employees/update_employee/application/use_case.py`: if `clear_user` is true, clear the association; else if `user_id` is provided, validate it the same way as T004 (excluding the employee being edited from the uniqueness check, e.g. `Employee.exclude(id=employee_id).get_or_none(user_id=user_id)`) before delegating to the repository (per research.md Decisions 2 and 3)
- [ ] T010 [P] [US2] Add `user_id: Optional[UUID] = None` and `clear_user: bool = False` parameters to `UpdateEmployeeRepository.update` in `app/slices/employees/update_employee/infra/repository.py`: set `employee.user_id = None` when `clear_user` is true, else set `employee.user = user` (the validated instance) when `user_id is not None`, leaving the field untouched otherwise
- [ ] T011 [US2] Update `app/slices/employees/update_employee/ui/route.py` to derive `clear_user = "user_id" in data.model_fields_set and data.user_id is None`, pass `user_id=data.user_id, clear_user=clear_user` into the use case call, and extend the existing `except ValueError` block so only the employee-not-found case maps to `404` with its current message while new "User not found" messages map to `404` and any other message (e.g. the duplicate-link case) maps to `400` (mirror `partner_loan/create_loan`'s branching pattern); depends on T008, T009, T010
- [ ] T012 [P] [US2] Update the `PUT /employees/{employee_id}` section of `specs/api/employees.md` to document the new `user_id` field and its three-state (omitted / set / explicit `null`) semantics, plus the new `404`/`400` error cases (per contracts/employees.md)

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - View which user account is linked to an employee (Priority: P3)

**Goal**: Any authorized caller retrieving employee details (single or list) can see the
linked `user_id`, or that none is linked.

**Independent Test**: `GET /employees/{id}` and `GET /employees/` both include `user_id`
for every employee in their response (see quickstart.md Scenario 8).

### Implementation for User Story 3

- [ ] T013 [P] [US3] Add `user_id: Optional[UUID]` to `EmployeeResponse` in `app/slices/employees/get_employee/ui/schemas.py`
- [ ] T014 [P] [US3] Add `user_id: Optional[UUID]` to `EmployeeResponse` in `app/slices/employees/list_employees/ui/schemas.py`
- [ ] T015 [P] [US3] Update the `Employee` shape block of `specs/api/employees.md` (used by `GET /employees/{employee_id}` and `GET /employees/`) to list the new `user_id` field

**Checkpoint**: All three user stories are independently functional; the full feature is complete.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T016 Run all 8 quickstart.md scenarios end-to-end against a local dev server to validate the complete feature
- [ ] T017 Invoke the `update-api-contract` skill (or manually diff) to confirm `specs/api/employees.md` matches the final implemented routes/schemas exactly, per `CLAUDE.md`'s mandatory API-contract-sync rule

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: None — no tasks
- **Foundational (Phase 2)**: No dependencies beyond Setup; BLOCKS all user stories (T003-T015 all require the `Employee.user` field to exist)
- **User Stories (Phase 3-5)**: All depend only on Foundational; they do not depend on each other and may proceed in any order or in parallel
- **Polish (Phase 6)**: Depends on whichever user stories were completed (T016 exercises all 3; run a subset of quickstart scenarios if shipping fewer stories)

### User Story Dependencies

- **User Story 1 (P1)**: Depends only on Phase 2
- **User Story 2 (P2)**: Depends only on Phase 2 — independently testable even if US1 hasn't shipped, since the model field already exists after Phase 2
- **User Story 3 (P3)**: Depends only on Phase 2 — independently testable by pointing at employees whose link was set directly or via US1/US2

### Within Each User Story

- Schema, use case, and repository edits (all different files) can proceed in parallel
- The route edit always comes last, since it wires together the schema and use case changes
- The `specs/api/employees.md` doc update for a story can proceed in parallel with that story's code tasks, but should land in the same change

### Parallel Opportunities

- T003, T004, T005 (US1) in parallel; then T006; T007 anytime
- T008, T009, T010 (US2) in parallel; then T011; T012 anytime
- T013, T014, T015 (US3) fully parallel (three independent files)
- Once Phase 2 is done, all of US1, US2, US3 can be staffed and worked simultaneously by different people

---

## Parallel Example: User Story 1

```bash
# Launch schema, use case, and repository edits for User Story 1 together:
Task: "Add user_id to CreateEmployeeRequest/EmployeeResponse in app/slices/employees/create_employee/ui/schemas.py"
Task: "Add user_id param + validation to CreateEmployee.execute in app/slices/employees/create_employee/application/use_case.py"
Task: "Add user_id param to CreateEmployeeRepository.create in app/slices/employees/create_employee/infra/repository.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 2: Foundational (model field + migration)
2. Complete Phase 3: User Story 1
3. **STOP and VALIDATE**: Run quickstart.md Scenarios 1-4 against a local dev server
4. Deploy/demo if ready — HR can already link a user at employee creation time

### Incremental Delivery

1. Foundational → foundation ready
2. Add User Story 1 → validate (Scenarios 1-4) → deploy/demo (MVP!)
3. Add User Story 2 → validate (Scenarios 5-7) → deploy/demo
4. Add User Story 3 → validate (Scenario 8) → deploy/demo
5. Run T017 (`update-api-contract` audit) before considering the feature complete, regardless of how it's staged

---

## Notes

- [P] tasks touch different files and have no unfinished dependency
- Every user story remains independently testable per its Independent Test above
- Commit after each task or logical group
- `specs/api/employees.md` must reflect whichever stories have actually shipped — do not defer that update past the change that ships the corresponding story (Constitution III)
