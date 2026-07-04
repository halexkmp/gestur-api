# Vertical Slice Architecture – Implementation Guide for New Features

This guide defines how AI coding agents and developers must implement new features in this project using the adopted Vertical Slice Architecture.

The objective is to maximize consistency, predictability, maintainability, and code quality while minimizing architectural drift.

---

# Priority Order (Highest to Lowest)

When implementing a feature, always follow this priority order:

1. `requirements.md`
2. `guidelines.md`
3. Existing project patterns

If any conflict exists, always follow the document with the highest priority.

---

# Mandatory Workflow

For every new feature, ALWAYS follow this workflow.

1. Read and fully understand `requirements.md`.
2. Inspect the existing project to identify similar implementations.
3. Reuse existing architectural patterns whenever possible.
4. Create `plan.md`.
5. Create `tasks.md`.
6. Implement the feature following `tasks.md`.
7. Mark tasks as completed (`[x]`) immediately after implementation.
8. Do not implement requirements that are not described in `requirements.md`.

Never skip any step.

---

# 1. Core Principles

Before writing code, validate all of the following.

- Each feature is self-contained.
- A feature owns its own UI, Application, Infra and (optionally) Domain.
- No generic dictionaries (`dict`) cross architectural layers.
- Parameters must always be explicit.
- Repositories only persist and retrieve data.
- Business rules belong to the Application or Domain layer.
- HTTP concerns belong exclusively to the UI layer.
- Shared modules exist only for stable cross-cutting concerns.
- Prefer consistency over introducing new abstractions.
- Minimize the number of modified files.
- Reuse existing implementations whenever possible.

---

# 2. Feature Folder Structure

Each feature must follow this structure.

```text
slices/
    <context>/
        <feature_name>/
            application/
                use_case.py
            ui/
                route.py
                schemas.py
            infra/
                repository.py
            domain/
                rules.py
```

## Naming Rules

- Folder names use `snake_case`.
- Feature names describe a single business use case.
- File names are fixed and must not be changed.
- Keep naming consistent with the rest of the project.

---

# 3. Layer Responsibilities

## 3.1 UI Layer (`ui/`)

### Responsibilities

- Handle HTTP requests.
- Validate request payloads.
- Convert HTTP requests into explicit use case parameters.
- Translate application exceptions into HTTP responses.

### Allowed

- FastAPI
- Dependency Injection
- Pydantic
- HTTPException

### Forbidden

- ORM
- Transactions
- Business rules
- SQL

### Schemas

Schemas are HTTP contracts only.

They must never leak into Application, Domain or Infra.

---

## 3.2 Application Layer (`application/`)

### Responsibilities

- Represent one business action.
- Coordinate repositories.
- Execute business rules.
- Control transactions when necessary.

### Allowed

- Domain rules
- Repository usage
- Application exceptions

### Forbidden

- HTTP
- ORM implementation details
- SQL
- Pydantic schemas
- Generic dictionaries

### Rules

- One Use Case = One business action.
- Parameters must always be explicit.
- Never use `dict`.
- Never use `**kwargs`.
- Never expose infrastructure details.

---

## 3.3 Domain Layer (`domain/`)

Create this layer only when business logic is reusable or sufficiently complex.

### Responsibilities

- Pure business rules.
- Business invariants.
- Domain calculations.

### Forbidden

- ORM
- FastAPI
- HTTP
- Database access
- Framework imports

---

## 3.4 Infrastructure Layer (`infra/`)

### Responsibilities

- Execute database operations.
- Persist entities.
- Retrieve entities.

### Allowed

- ORM
- Queries
- Transactions
- Shared database models

### Forbidden

- Business rules
- HTTP logic
- Validation
- Request schemas

Repositories must only persist and retrieve data.

---

# 4. Database Guidelines

When introducing new persistence models:

- Use UUID as the primary key.
- Include `created_at`.
- Include `updated_at`.
- Prefer database constraints over application-only validation.
- Create indexes for frequently queried columns.
- Use `Decimal` for monetary values.
- Avoid nullable fields unless required.

---

# 5. Shared Module Usage

`shared/` exists only for stable cross-cutting concerns.

Allowed:

- ORM models
- Enums
- Constants
- Database configuration
- Utility functions shared by multiple features

Forbidden:

- Feature-specific use cases
- Feature-specific business logic
- UI schemas
- Application services

Rule:

If it changes because business requirements change, it probably does not belong in `shared/`.

---

# 6. Error Handling

UI

- Converts exceptions into HTTP responses.

Application

- Raises business exceptions.

Infrastructure

- Never raises HTTP exceptions.

Business exceptions should be meaningful and specific.

---

# 7. Dependency Direction (Non-Negotiable)

Dependencies always flow in one direction.

```text
UI
    ↓
Application
    ↓
Domain (optional)
    ↓
Infrastructure
```

Reverse dependencies are forbidden.

---

# 8. Explicitness Over Convenience

Forbidden

```python
async def execute(data: dict)
```

Required

```python
async def execute(
    partner_id: UUID,
    amount: Decimal,
    installments: int
)
```

Explicit parameters are a design rule.

---

# 9. Design Principles

Prefer:

- Composition over inheritance.
- Small classes.
- Small functions.
- Early returns.
- Dependency injection.
- Immutable data whenever practical.
- Clear responsibilities.

Avoid unnecessary abstraction.

---

# 10. Consistency First

When implementing a feature:

- Follow existing project patterns.
- Do not introduce new architectural styles.
- Do not create abstractions unless necessary.
- Preserve naming conventions.
- Keep modifications focused on the requested feature.

Consistency is preferred over cleverness.

---

# 11. Missing Requirements

If `requirements.md` does not define some behavior:

1. Search for similar implementations.
2. Reuse existing behavior when appropriate.
3. If no precedent exists, document the assumption in `plan.md`.
4. Do not invent complex business rules.

---

# 12. Performance Guidelines

Avoid:

- N+1 queries.
- Repeated database access.
- Loading unnecessary relationships.
- Duplicate calculations.

Prefer:

- Bulk operations.
- Database filtering.
- Efficient queries.

---

# 13. Testing

- NOT CREATE ANY TEST
---

# 14. Migration Rules

Whenever the database changes:

- Do nothing. The migration will be handled by the migration tool manually

---

# 15. Documentation

Each feature must have its own documentation folder.

```text
docs/
    feature_name/
        requirements.md
        plan.md
        tasks.md
```

---

## requirements.md

Written by the developer or another AI agent.

Contains:

- Business requirements.
- Acceptance criteria.
- Functional rules.
- Non-functional requirements.

Junie must treat this document as the source of truth.

---

## plan.md

Must be created by Junie before implementation.

It should describe:

- Technical approach.
- Architectural decisions.
- Database changes.
- API changes.
- Validation strategy.
- Implementation phases.
- Risks or assumptions.

The plan should be concise but sufficient to explain how the feature will be implemented.

---

## tasks.md

Must also be created by Junie.

Requirements:

- Organize tasks by implementation phase.
- Tasks must be as granular as practical.
- Each task should represent one logical implementation step.
- Use checkboxes.

Example:

```text
## Phase 1 - Database

- [ ] Create Loan model
- [ ] Create LoanInstallment model
- [ ] Create migration

## Phase 2 - Infrastructure

- [ ] Implement repository

## Phase 3 - Application

- [ ] Implement CreateLoanUseCase

## Phase 4 - UI

- [ ] Create endpoint
- [ ] Create request schema
```

During implementation, completed tasks must immediately become:

```text
- [x]
```

---

# 16. Definition of Done

A feature is complete only when:

- Feature folder exists.
- Vertical Slice Architecture is respected.
- Explicit parameters are used.
- Business rules are outside repositories.
- Repository only performs persistence.
- HTTP logic exists only in UI.
- Tests were implemented.
- Documentation was updated.
- `plan.md` was created.
- `tasks.md` was created.
- All tasks are marked as completed.
- Database migrations were created (when necessary).
- No unrelated code was modified.

---

# 17. Don't Be Smart

Unless explicitly requested:

- Do not refactor unrelated code.
- Do not rename files.
- Do not rename classes.
- Do not reorganize folders.
- Do not optimize unrelated code.
- Do not introduce new libraries.
- Do not change coding style.
- Do not change project architecture.

Implement exactly what is requested in `requirements.md`.