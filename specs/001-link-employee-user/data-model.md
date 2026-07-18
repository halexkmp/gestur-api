# Phase 1 Data Model: Link Employee to User Account

## Entities

### Employee (modified)

Existing entity (`app/shared/db/models.py`, table `employee`). Adds one new field; all
existing fields are unchanged.

| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | unchanged |
| name | string | unchanged |
| pix_key | string, nullable | unchanged |
| salary | Decimal(10,2) | unchanged |
| start_date | date | unchanged |
| active | bool | unchanged |
| created_at | datetime | unchanged |
| **user** | **FK → User, nullable, unique** | **new** — the employee's linked login account, if any |

```python
user = fields.ForeignKeyField("models.User", related_name="employee", null=True, unique=True)
```

**Validation rules** (enforced in the `application/` layer, not in `infra/`):
- On create or update, if a `user_id` is supplied, the referenced `User` MUST exist (else
  reject — "User not found").
- On create or update, if a `user_id` is supplied, no *other* `Employee` row may already
  reference that same `User` (else reject — "User is already linked to another employee").
  The database `unique=True` constraint is the final backstop for this rule.
- Supplying the employee's own current `user_id` again on update is a no-op, not a conflict
  (the uniqueness check excludes the employee being edited).

**State transitions**: `user` moves between three states over an employee's lifetime —
*unset* (no account) → *linked* (a specific `User`) → *unset* or *relinked* (a different
`User`). All transitions are explicit HR actions via create/update; nothing else in the
system mutates this field (see research.md Decision 3 — no cascading clear when a `User`
is deactivated/deleted elsewhere).

### User (unchanged)

Existing entity (table `user`). No field changes. Gains a reverse accessor
(`employee`, from `related_name="employee"`) to the `Employee` row that references it, if
any — this is a Tortoise-ORM-level relation, not a new column.

## Relationships

```
User (1) ────optional, unique──── (0..1) Employee
```

- One `User` ↔ zero or one `Employee` (enforced by `unique=True` on `Employee.user_id`).
- One `Employee` ↔ zero or one `User` (enforced by `null=True`, and by application-layer
  validation rejecting unknown user ids).

## Migration

Per Constitution V and `CLAUDE.md`, this field addition is implemented by editing the
model only; the actual migration file is generated and applied separately via
`aerich migrate` / `aerich upgrade` — it is not hand-authored as part of this plan's design
artifacts.
