<!--
Sync Impact Report
==================
Version change: 1.1.0 → 1.2.0 (minor: new material requirement added to Principle III and
  Development Workflow & Quality Gates — the standing API contract in `specs/api/`)
Modified principles:
  - III. Documentation-First Feature Development — added the `specs/api/` standing API
    contract requirement: any change to a route, request/response schema, permission guard,
    or shared enum under `app/slices/`/`app/shared/db/enums.py` MUST update the matching
    `specs/api/<context>.md` (and `shared.md` for enums) in the same change. This is
    separate from the per-feature `specs/<NNN-feature-name>/` Spec Kit workflow: `specs/api/`
    is a living mirror of the current API surface, not a point-in-time feature spec.
Changed: Development Workflow & Quality Gates now includes `specs/api/` sync as a
  completion gate alongside the per-feature spec/plan/tasks gate.
Added sections: none
Removed sections: none
Templates requiring updates:
  - CLAUDE.md ✅ updated — new "API contract (specs/api/)" section plus a "Notable
    constraints" bullet
  - README.md ✅ updated — Project Structure now lists `specs/api/`
  - .claude/skills/update-api-contract/SKILL.md ✅ added — audits/syncs `specs/api/`
    against `app/slices/`
Follow-up TODOs: none
-->

<!--
Sync Impact Report (v1.1.0, superseded by the entry above)
==================
Version change: 1.0.1 → 1.1.0 (minor: documentation workflow redefined, materially changes
  Principle III and part of Development Workflow & Quality Gates)
Modified principles:
  - III. Documentation-First Feature Development — replaced the legacy `docs/<feature_name>/`
    convention (requirements.md/plan.md/tasks.md) with the Spec Kit workflow
    (`/speckit-specify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-implement`, writing to
    `specs/<NNN-feature-name>/spec.md|plan.md|tasks.md`). The `docs/` folder was deleted from the
    repository as legacy, per explicit user instruction — Spec Kit is now the single
    documentation workflow.
Changed: Development Workflow & Quality Gates now references `specs/<NNN-feature-name>/spec.md`
  instead of `docs/<feature_name>/requirements.md` as the completion gate.
Added sections: none
Removed sections: none
Templates requiring updates:
  - README.md ✅ updated — Project Structure now lists `specs/` (Spec Kit) instead of `docs/`
  - CLAUDE.md ✅ updated — Feature documentation workflow section now describes the Spec Kit
    command sequence and `specs/` output location
Follow-up TODOs: none
-->

<!--
Sync Impact Report (v1.0.1, superseded by the entry above)
==================
Version change: 1.0.0 → 1.0.1 (patch: reference correction, no principle change)
Changed: Governance section named `CLAUDE.md` (not `AGENTS.md`) as the day-to-day
  implementation guide, after AGENTS.md was deleted from the repository as outdated.
-->

<!--
Sync Impact Report (v1.0.0, superseded by the entries above)
==================
Version change: [TEMPLATE, unratified] → 1.0.0 (initial ratification)
Modified principles: n/a (first concrete version; all 5 slots filled from placeholders)
Added sections:
  - Core Principles I-V (Vertical Slice Architecture, Explicit Parameters, Documentation-First
    Feature Development, Consistency Over Cleverness, Data & Persistence Discipline)
  - Technology & Deployment Constraints
  - Development Workflow & Quality Gates
  - Governance (versioning policy, amendment procedure, AGENTS.md relationship)
Removed sections: none (template placeholders only)
-->

# Gestur API Constitution

## Core Principles

### I. Vertical Slice Architecture

Every feature MUST be implemented as a self-contained vertical slice under
`app/slices/<context>/<feature_name>/`, owning its own UI, Application, Infrastructure,
and (optionally) Domain layers. Dependencies MUST flow in one direction only:
UI → Application → Domain (optional) → Infrastructure; reverse dependencies are forbidden.
HTTP concerns (FastAPI routes, Pydantic schemas, exception-to-HTTP translation) MUST stay
exclusively in the `ui/` layer; business rules MUST live in `application/` or `domain/`;
repositories in `infra/` MUST only persist and retrieve data, never enforce business rules
or HTTP logic. `app/shared/` is reserved for stable, cross-cutting concerns only (ORM
models, enums, security, generic infra clients) — anything that changes because business
requirements change does not belong there.

Rationale: This is the organizing architecture of the entire codebase. Dozens of existing
feature folders follow this shape; consistent slice boundaries keep each one predictable
and let new features be added without touching unrelated code.

### II. Explicit Parameters, No Generic Containers

Application-layer entry points (use case `execute` methods) MUST declare explicit, typed
parameters. Generic `dict` payloads and `**kwargs` MUST NOT be used to cross architectural
layer boundaries. Pydantic schemas are HTTP contracts only and MUST NOT leak into
Application, Domain, or Infrastructure layers.

Rationale: Explicitness prevents architectural drift and keeps each use case
self-documenting, so its full behavior is visible from its signature alone.

### III. Documentation-First Feature Development

Every new feature MUST go through the Spec Kit workflow before implementation:
`/speckit-specify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-implement`, producing
`specs/<NNN-feature-name>/spec.md` (source of truth, authored first), `plan.md` (technical
approach, written before implementation begins), and `tasks.md` (a granular, checkbox task
list, updated to `[x]` immediately as each task completes). When documents conflict,
priority is: `spec.md` > `plan.md` > existing project patterns. Behavior not described in
`spec.md` MUST NOT be implemented without first surfacing the gap and getting explicit
confirmation.

Independently of the per-feature Spec Kit workflow, `specs/api/` is a standing API
contract — one file per context, mirroring the API surface consumed by the separate
frontend project. It is not a point-in-time feature spec; it MUST always match
`app/slices/` exactly. Any change to a route path/method, request/response schema field,
query/path parameter, role/permission guard, non-default status code, or shared enum
(`app/shared/db/enums.py`) MUST update the matching `specs/api/<context>.md` (and
`specs/api/shared.md` for enums) in the same change, regardless of whether the change came
from `/speckit-implement` or an ad hoc edit. A new `<context>` slice requires a new
`specs/api/<context>.md`.

Rationale: Keeps intent traceable as the number of slices grows, and prevents scope creep
disguised as reasonable inference. This project previously used an ad hoc `docs/<feature>/`
convention (`requirements.md`/`plan.md`/`tasks.md`); that legacy folder was removed once
Spec Kit was adopted as the single documentation workflow. `specs/api/` was added
separately because the frontend project needs an always-current contract, not a per-feature
snapshot scattered across many `specs/<NNN-feature-name>/` folders.

### IV. Consistency Over Cleverness

Implementers MUST prefer existing patterns from comparable slices over introducing new
abstractions, libraries, or architectural styles. Unless explicitly requested, do not
refactor unrelated code, rename files or classes, reorganize folders, or change coding
style while delivering a feature. Changes MUST be scoped to the minimum number of files
necessary to satisfy the requirement at hand.

Rationale: A codebase built from many near-identical feature slices only stays
maintainable if every slice keeps looking like its neighbors; unscoped cleanup multiplies
review cost and regression risk.

### V. Data & Persistence Discipline

New persistence models MUST use a UUID primary key, MUST include `created_at` (and
`updated_at` when the entity is mutable), and MUST use `Decimal` fields for monetary
values. Models SHOULD favor database constraints over application-only validation and
SHOULD add indexes for frequently queried columns. Schema changes are driven by model
edits, but migration files themselves are generated and applied outside of agent-driven
edits (`aerich migrate` / `aerich upgrade`) — agents MUST NOT hand-author or hand-edit
migration files.

Rationale: Matches the existing `app/shared/db/models.py` conventions and keeps the
Aerich migration history authoritative and reproducible.

## Technology & Deployment Constraints

The stack is fixed unless the user explicitly approves a change: FastAPI, Tortoise-ORM,
Aerich migrations, PostgreSQL, JWT auth (python-jose), and pydantic-settings for
configuration, deployed to Vercel as a Python serverless function (`api/index.py`
entrypoint, `vercel.json`). New third-party dependencies MUST NOT be introduced without an
explicit request. Environment configuration flows exclusively through `app/config.py`'s
`Settings`; in production, `DATABASE_URL` and `SECRET_KEY` are required and the
application MUST fail to start if either is missing. Schema auto-generation
(`GENERATE_SCHEMAS`) MUST remain disabled in production, where Aerich migrations are the
only source of schema change.

## Development Workflow & Quality Gates

A feature is complete only when: the vertical-slice folder structure is respected,
explicit typed parameters are used throughout the application layer, business rules live
outside repositories, HTTP logic exists only in `ui/`, the feature's
`specs/<NNN-feature-name>/spec.md`, `plan.md`, and `tasks.md` all exist with every task
checked off, the matching `specs/api/<context>.md` (and `shared.md` if enums changed)
reflects every route/schema/permission change made, database migrations were generated
when models changed, and no unrelated code was modified. Automated tests MUST NOT be added for new feature work — this is this
project's explicit, current policy and it overrides any generic "tests are OPTIONAL, only
if requested" default from tooling templates. If a task appears to require tests to be
verifiable, surface that tension to the user rather than silently adding or silently
skipping verification.

## Governance

This constitution is the highest-authority guidance for this repository. `CLAUDE.md`
is the day-to-day implementation guide for Vertical Slice Architecture and MUST stay
consistent with the principles defined here; where the two conflict, this constitution
wins and `CLAUDE.md` should be updated to match. Amendments to this
constitution MUST be recorded in this file with an updated version number and a Sync
Impact Report (prepended as an HTML comment) describing what changed and which dependent
templates or docs were checked for consistency. Versioning follows semantic rules: MAJOR
for backward-incompatible principle removals or redefinitions, MINOR for new or materially
expanded principles or sections, PATCH for clarifications and wording fixes that do not
change meaning. Every feature's `plan.md` and any code review SHOULD verify compliance
with these principles; unjustified complexity or deviation must be called out explicitly
in `plan.md`'s Complexity Tracking section rather than introduced silently.

**Version**: 1.2.0 | **Ratified**: 2026-07-17 | **Last Amended**: 2026-07-17
