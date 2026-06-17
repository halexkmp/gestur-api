# Implementation Plan - Journey Registry

## 1. Foundation & Shared Concerns
- **P1: Database Schema Update** (Requirement: 1, 3, 4)
  - Add `EMPLOYEE` to `UserRole` enum.
  - Create `JourneyRegistry` model in `app/shared/db/models.py`.
  - Fields: `id`, `user_id` (FK), `timestamp`, `latitude`, `longitude`, `is_deleted`, `edit_reason`, `original_data` (JSON/Text).
  - Data migration to insert `EMPLOYEE` role into the `role` table.
- **P2: Shared Utilities** (Requirement: 1)
  - Ensure datetime and location validation helpers are available in `shared/`.

## 2. Core Journey Features (Employee)
- **P1: Create Journey Registry Slice** (Requirement: 1, 5)
  - Path: `slices/journey/register_journey/`
  - Implement UI (POST), Application, and Infra.
- **P3: List Personal Journey History Slice** (Requirement: 2, 5)
  - Path: `slices/journey/list_my_journeys/`
  - Implement UI (GET), Application, and Infra.

## 3. Administrative Features (Admin)
- **P2: List All Journey Registries Slice** (Requirement: 3, 5)
  - Path: `slices/journey/admin_list_journeys/`
  - Filters: `user_id`, `start_date`, `end_date`.
- **P2: Update Journey Registry Slice** (Requirement: 3, 5)
  - Path: `slices/journey/update_journey/`
  - Only accessible by Admin.
  - Requires `edit_reason`.
- **P3: Delete Journey Registry Slice** (Requirement: 3, 5)
  - Path: `slices/journey/delete_journey/`
  - Soft delete implementation.

## 4. User Profile Integration
- **P2: Role-Based Access Control Update** (Requirement: 4, 5)
  - Update user creation/update logic to support `EMPLOYEE` role.
  - Ensure security decorators/middlewares account for the new role and permissions.
