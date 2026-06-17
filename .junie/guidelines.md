# Vertical Slice Architecture – Implementation Guide for New Features

This guide defines **how to implement new features** in this project using the **Vertical Slice Architecture** adopted by the team.

### The goal is to ensure
- High cohesion
- Explicit contracts
- Minimal coupling
- Clear separation of responsibilities
- Pythonic and pragmatic design

This document is intended to be consumed by **coding agents and developers**.

---

## 1. Core Principles

### Before writing code, **always validate these principles**

- Each feature is **self-contained**
- A feature owns its **UI, application, infra, and (optional) domain**
- No generic `dict` objects crossing layers
- Parameters must be **explicit**
- Repositories only persist data
- Business rules live in **application or domain**
- HTTP concerns live only in **UI**
- Shared modules (`shared/`) are allowed **only for stable, cross-cutting concerns**

---

## 2. Feature Folder Structure

### Each feature must live inside its slice and follow this structure

slices/
<context>/
<feature_name>/
    application/
        use_case.py
    ui/
        route.py
        schemas.py
    infra/ # optional
        repository.py
    domain/ # optional
        rules.py


### Naming rules
- Folder names: `snake_case`
- Feature name should describe **one use case**
- File names are **fixed and mandatory**

---

## 3. Layer Responsibilities

### 3.1 UI Layer (`ui/`)

**Purpose**
- Handle HTTP
- Parse and validate input
- Call the use case
- Translate application errors into HTTP responses

**Allowed**
- FastAPI
- Pydantic schemas
- HTTPException
- Dependency injection

**Forbidden**
- ORM access
- Business rules
- Transactions

#### Files

##### `schemas.py`
Defines request and response schemas.

- Schemas are **UI contracts**
- They must not leak into application or infra

### Example
```python
### class CreateProductRequest(BaseModel)
    name: str
    price: float
    active: bool
```
File
route.py

Defines HTTP routes and adapters.

UI calls the use case

UI passes explicit parameters

UI translates errors

### Example

@router.post("")
### async def route(data: CreateProductRequest)
    return await use_case.execute(
        name=data.name,
        price=data.price,
        active=data.active,
    )

## 3.2 Application Layer (application/)

Purpose

Orchestrate the feature

Define the system’s intention

Coordinate domain rules and repositories

Allowed

Business rules

Domain rule invocation

Repository usage

Forbidden

HTTP concerns

ORM specifics

Pydantic schemas

Generic dictionaries

File
use_case.py

### Rules

Parameters must be explicit

No dict, **kwargs, or dynamic payloads

Use case defines the true contract of the feature

### Example

### class CreateProduct
###     def __init__(self, repository: CreateProductRepository)
        self.repository = repository

    async def execute(
        self,
        name: str,
        price: float,
        active: bool,
###     )
        return await self.repository.create(
            name=name,
            price=price,
            active=active,
        )

## 3.3 Domain Layer (domain/) – Optional

Purpose

Encapsulate pure business rules

Protect invariants

Avoid duplication across use cases

When to create

Rule is complex

Rule is reused

Rule has no infrastructure dependency

When NOT to create

Rule is trivial

Rule is specific to one use case

Adds unnecessary indirection

File
rules.py

### Rules

No ORM

No HTTP

No framework imports

### Example

### def calculate_total(items: list) -> float
    return sum(item.quantity * item.unit_price for item in items)

## 3.4 Infra Layer (infra/)

Purpose

Persist data

Talk to the database

Implement repositories

Allowed

ORM

Transactions

Models from shared/db/models.py

Forbidden

Business decisions

HTTP logic

Input validation

Schema knowledge

File
repository.py

### Rules

Repository receives explicit parameters

Repository does not calculate business values

Repository does not validate rules

### Example

### class CreateProductRepository
    async def create(
        self,
        name: str,
        price: float,
        active: bool,
###     )
        return await Product.create(
            name=name,
            price=price,
            active=active,
        )

# 4. Shared Module Usage (shared/)

shared/ exists for stable, cross-cutting concerns.

Allowed in shared

ORM models

Enums

Database configuration

Constants

Forbidden in shared

Use cases

Feature-specific logic

UI schemas

Business rules tied to a single feature

Rule

If it changes with business logic, it does NOT belong in shared.

# 5. Error Handling Rules

UI raises HTTPException

Application raises domain/application errors

Infra never raises HTTP errors

### Example

### class ProductNotFoundError(Exception)
    pass


### UI translates

### try
    ...
### except ProductNotFoundError
    raise HTTPException(status_code=404)

# 6. Dependency Direction (Non-Negotiable)
UI → Application → (Domain) → Infra


Reverse dependencies are forbidden.

# 7. Explicitness Over Convenience

### ❌ This is forbidden

### async def execute(self, data: dict)


### ✅ This is required

### async def execute(self, name: str, price: float)


Explicit parameters are a design rule, not a preference.

# 8. Definition of Done for a Feature

### A feature is complete only if

 Has its own folder

 Uses fixed file names

 Has no generic dictionaries crossing layers

 UI contains all HTTP logic

 Repository contains only persistence logic

 Business rules are not in infra

 Shared is used only when justified

# 9. Task Management Guidelines

### Working with `docs/tasks.md`
- Mark tasks as `[x]` when completed.
- Maintain the existing structure and phases.
- When adding new tasks, ensure they are linked to a requirement and a plan item:
  - Format: `- [ ] T{phase}.{task_id}: Description (Plan: {plan_id}, Req: {req_id})`
- Every modification to the task list must be reflected in the project progress.
- Tasks should be as granular as possible, especially for vertical slices (splitting UI, Application, and Infra).
