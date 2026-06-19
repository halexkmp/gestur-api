# Technical Tasks - Journey Registry

## Phase 1: Setup & Foundation
- [x] T1.1: Add `EMPLOYEE` value to `UserRole` enum in `app/shared/db/enums.py` (Plan: 1.1, Req: 4)
- [x] T1.2: Define `JourneyRegistry` model in `app/shared/db/models.py` (Plan: 1.1, Req: 1, 3)
- [x] T1.3: Create database migration for the new model and enum change (Plan: 1.1, Req: 1)
- [x] T1.4: Create data migration to insert `EMPLOYEE` role into the `role` table (Plan: 1.1, Req: 4)

## Phase 2: Core Journey Features
- [x] T2.1: Implement `register_journey` slice (Plan: 2.1, Req: 1, 5)
    - [x] T2.1.1: UI: `ui/schemas.py` and `ui/route.py`
    - [x] T2.1.2: Application: `application/use_case.py`
    - [x] T2.1.3: Infra: `infra/repository.py`
    - [x] T2.1.4: Implement business rule: max 4 records per day (Plan: 2.1, Req: 1)
    - [x] T2.1.5: Implement business rule: min 1-minute interval (Plan: 2.1, Req: 1)
- [x] T2.2: Implement `list_my_journeys` slice (Plan: 2.2, Req: 2, 5)
    - [x] T2.2.1: UI: `ui/schemas.py` and `ui/route.py`
    - [x] T2.2.2: Application: `application/use_case.py`
    - [x] T2.2.3: Infra: `infra/repository.py`

## Phase 3: Administrative Features
- [x] T3.1: Implement `admin_list_journeys` slice (Plan: 3.1, Req: 3, 5)
    - [x] T3.1.1: UI: `ui/schemas.py` and `ui/route.py`
    - [x] T3.1.2: Application: `application/use_case.py`
    - [x] T3.1.3: Infra: `infra/repository.py`
- [x] T3.2: Implement `update_journey` slice for Admins (Plan: 3.2, Req: 3, 5)
    - [x] T3.2.1: UI: `ui/schemas.py` and `ui/route.py`
    - [x] T3.2.2: Application: `application/use_case.py`
    - [x] T3.2.3: Infra: `infra/repository.py`
- [x] T3.3: Implement `delete_journey` slice for Admins (Plan: 3.3, Req: 3, 5)
    - [x] T3.3.1: UI: `ui/schemas.py` and `ui/route.py`
    - [x] T3.3.2: Application: `application/use_case.py`
    - [x] T3.3.3: Infra: `infra/repository.py`

## Phase 4: User Profile & RBAC
- [x] T4.1: Update user creation/update slices to support `EMPLOYEE` role (Plan: 4.1, Req: 4)
- [x] T4.2: Verify and update security decorators to handle `EMPLOYEE` permissions (Plan: 4.1, Req: 5)

## Phase 5: Testing & QA
- [x] T5.1: Write unit tests for journey use cases (Plan: 2.1, 2.2, 3.2)
- [x] T5.2: Write integration tests for journey API endpoints (Plan: 2.1, 2.2, 3.1, 3.2, 3.3)
- [x] T5.3: Verify soft delete behavior and audit logging for admin edits (Plan: 3.2, 3.3, Req: 3)
- [x] T5.4: Test business rules for journey registration (max 4/day, 1min interval) (Plan: 2.1, Req: 1)