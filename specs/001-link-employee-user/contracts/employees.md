# Contract Changes: Employees API

Scope: this documents the delta to the existing `POST /employees/`, `PUT
/employees/{employee_id}`, `GET /employees/{employee_id}`, and `GET /employees/` endpoints.
Everything not listed here (auth requirement, other fields, other endpoints) is unchanged
from the current `specs/api/employees.md`. This file is a design artifact for this
feature's implementation; `specs/api/employees.md` itself MUST be updated to match during
`/speckit-implement`, per `CLAUDE.md`'s API contract policy.

Requires: `HUMAN_RESOURCES` — unchanged, same as every other endpoint in this file.

## Employee shape (response) — field added

```text
id
name
salary
pix_key      # nullable
active
start_date
user_id      # nullable — NEW: id of the linked User account, or null if none
```

Returned by: `POST /employees/`, `GET /employees/{employee_id}`, `PUT
/employees/{employee_id}`, and each item in `GET /employees/`.

## POST /employees/ — request field added

```text
name
pix_key        # optional
salary         # >= 0
active         # default true
start_date
user_id        # NEW, optional — links this employee to an existing user account at creation
```

- Omit `user_id` (or send `null`) → employee is created with no linked user.
- Supply an existing, unlinked user's id → employee is created with that user linked.
- Supply a `user_id` that doesn't exist → `404 Not Found`.
- Supply a `user_id` already linked to a different employee → `400 Bad Request`.

## PUT /employees/{employee_id} — request field added (all fields remain optional/partial)

```text
name           # optional
pix_key        # optional
salary         # optional
active         # optional
start_date     # optional
user_id        # NEW, optional
```

`user_id` on update has three distinct behaviors based on JSON presence/value:

| Request body | Effect |
|---|---|
| `user_id` key omitted entirely | No change to the employee's current user link |
| `"user_id": "<uuid>"` | Sets/changes the linked user to that account |
| `"user_id": null` | Explicitly clears the employee's linked user |

- Supplying a `user_id` that doesn't exist → `404 Not Found`.
- Supplying a `user_id` already linked to a different employee → `400 Bad Request`.
- Supplying the employee's own current `user_id` again → no-op, succeeds.
- Employee not found (existing behavior, unchanged) → `404 Not Found`.
