# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Gestur API — a FastAPI + Tortoise-ORM backend for business operations (sales, inventory, HR, partner loans, employee journey tracking). Deployed on Vercel as a Python serverless function.

## Commands

```bash
# Run the dev server (reload enabled when ENVIRONMENT != production)
python app/main.py
# equivalently: uvicorn app.main:app --reload

# Install dependencies
pip install -r requirements.txt

# Migrations (Aerich)
aerich migrate    # generate a new migration from model changes
aerich upgrade     # apply pending migrations

# Tests
pytest
pytest path/to/test_file.py::test_name   # single test
```

There is no lint/format tooling configured in this repo (no ruff/black/flake8 config present).

## Architecture: Vertical Slice Architecture (VSA)

This is the defining structural rule of the codebase — every new feature MUST follow this shape:

```
app/slices/<context>/<feature_name>/
    application/use_case.py   # one class = one business action, explicit params, no dict/**kwargs
    ui/route.py                # FastAPI route, HTTP-only concerns
    ui/schemas.py               # Pydantic request/response contracts (HTTP-only, never reused elsewhere)
    infra/repository.py         # ORM queries only — persistence, no business rules
    domain/rules.py             # optional: pure business logic, no framework imports
```

- Each `<context>` (e.g. `auth`, `users`, `partner_loan`, `journey`, `employees`, `partners`, `products`, `sales`, `reports`, `roles`) has a top-level `urls.py` that composes an `APIRouter` from each feature's `ui/route.py` and is wired into `app/main.py`.
- Dependency direction is one-way: UI → Application → Domain (optional) → Infrastructure. Never the reverse.
- Repositories only persist/retrieve; business rules live in `application/` or `domain/`, never in `ui/` or `infra/`.
- Use case constructors wire their own collaborators (repository, hashers, token service, etc.) — see `app/slices/auth/login_user/ui/route.py` for the pattern: the module instantiates `use_case = LoginUser(Repo(), Verifier(), TokenService())` at import time and the route just calls `use_case.execute(...)`.
- `app/shared/` is only for stable cross-cutting concerns (ORM models in `shared/db/models.py`, enums in `shared/db/enums.py`, security in `shared/security/`, blob storage in `shared/infra/image_service.py`). Feature-specific logic must never live here.
- When adding a new feature, follow the existing folder/file layout exactly (file names are fixed: `use_case.py`, `route.py`, `schemas.py`, `repository.py`, `rules.py`) and reuse patterns from a similar existing slice rather than inventing new structure.

## Data layer

- Tortoise-ORM models are centralized in `app/shared/db/models.py`; enums in `app/shared/db/enums.py`.
- Primary keys are UUIDs; money fields use `DecimalField`; most models have `created_at`/`updated_at`.
- Migrations are managed by Aerich (config in `pyproject.toml` under `[tool.aerich]`, files in `migrations/`). Do not hand-author or hand-edit migration files when models change — migration generation is handled via `aerich migrate`/`aerich upgrade`, run manually/separately.

## Auth & permissions

- JWT auth via `app/shared/security/current_user.py` (`get_current_user` dependency, `OAuth2PasswordBearer`, with an in-memory per-token user cache with a 1-hour TTL).
- Role checks are explicit guard functions in `app/shared/security/permissions.py` (e.g. `ensure_admin`, `ensure_hr`), called from within use cases/routes rather than via a generic RBAC decorator.
- Roles: `ADMIN`, `MANAGER`, `HUMAN_RESOURCES`, `OPERATOR`, `EMPLOYEE` (`UserRole` enum).

## Configuration

- Settings load from `.env` via `app/config.py` (`pydantic-settings`). Key vars: `ENVIRONMENT`, `SECRET_KEY`, `DATABASE_URL`, `ALLOWED_ORIGINS`, `BLOB_STORE_ID`/`BLOB_READ_WRITE_TOKEN`/`BLOB_FOLDER` (Vercel Blob for image storage), `GENERATE_SCHEMAS`, `RUN_MIGRATIONS_ON_STARTUP`.
- In production, `DATABASE_URL` and `SECRET_KEY` are required (validated in `Settings._apply_env_defaults`); dev falls back to local Postgres defaults and a dev secret key.
- `GENERATE_SCHEMAS` is only true outside production — in production, schema changes come from Aerich migrations, not `register_tortoise` auto-generation.
- Deployment entrypoint is `api/index.py` (imports `app` from `app.main`); Vercel's `installCommand` in `vercel.json` runs `migrations/run_migrations.py` (`aerich upgrade`) before the function goes live.

## Feature documentation workflow

Features are specified using [Spec Kit](https://github.com/github/spec-kit): `/speckit-specify` → `/speckit-plan` → `/speckit-tasks`, writing to `specs/<NNN-feature-name>/` (`spec.md`, `plan.md`, `tasks.md`, plus `research.md`/`data-model.md`/`contracts/` from the plan phase). `spec.md` is the source of truth for a feature's requirements and takes priority over existing code patterns when there is a conflict. Implement via `/speckit-implement`.

## Notable constraints

- **Do not write tests.** Tests are not to be created for new features, despite `pytest`/`pytest-asyncio` being installed dependencies — this is an explicit, current project policy (see `.specify/memory/constitution.md`).
- Never use `dict` or `**kwargs` as use-case parameters — parameters must be explicit and typed.
- Don't refactor, rename, or reorganize unrelated code; keep changes scoped to the requested feature ("Don't Be Smart" section).
- Prefer reusing an existing slice's pattern over introducing a new abstraction or architectural style.
