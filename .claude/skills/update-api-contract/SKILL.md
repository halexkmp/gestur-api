---
name: "update-api-contract"
description: "Audit and sync specs/api/*.md against the real FastAPI routes/schemas in app/slices/. Use any time a route, request/response schema, permission guard, or shared enum changes, when adding a new slice/context, or when asked to check/update/verify the API contract."
argument-hint: "Optional context name to scope the audit (e.g. sales, loans); omit to check everything"
user-invocable: true
disable-model-invocation: false
---

## Purpose

`specs/api/` is the standing API contract consumed by the separate frontend project — one
file per context (`auth.md`, `users.md`, `employees.md`, `journey.md`, `loans.md`,
`partners.md`, `products.md`, `reports.md`, `sales.md`, `roles.md`), plus `shared.md` for
auth/error conventions, common enums, and common types. Per `CLAUDE.md` and the project
constitution, this file MUST always match `app/slices/` exactly — it is not optional
documentation and not a per-feature spec.

This skill closes that loop: it diffs the real code against the contract docs and updates
the docs to match.

## User Input

```text
$ARGUMENTS
```

If a context name (or list of context names) is given, scope the audit to those contexts
under `app/slices/<context>/`. If empty, audit every context.

## Steps

1. **Identify scope**. If invoked after a code change (not a fresh manual run), prefer
   `git status`/`git diff` to see which `app/slices/<context>/**/ui/route.py`,
   `ui/schemas.py`, or `urls.py` files changed, plus whether
   `app/shared/db/enums.py` or `app/shared/security/permissions.py` changed. Otherwise use
   the context(s) named in `$ARGUMENTS`, or all contexts if none given.

2. **Read the real API surface** for each in-scope context:
   - `app/slices/<context>/urls.py` — router prefix(es) and how feature routers are mounted
     (note any sub-prefixes, e.g. a feature router mounted with its own extra `prefix=`).
   - Every `app/slices/<context>/*/ui/route.py` — HTTP method, full path, query/path
     params (and whether they're required/optional/defaulted), non-default status codes
     (`201`, `204`, etc.), request body shape (JSON vs form vs multipart/file upload),
     and any `ensure_admin`/`ensure_hr`/other guard from
     `app/shared/security/permissions.py`.
   - Every `app/slices/<context>/*/ui/schemas.py` — exact field names, types, and
     Optional/nullable-ness for every request and response model actually referenced by a
     route's `response_model=` or parameter type. Watch for endpoints that reuse a
     differently-shaped schema than sibling endpoints for "the same" resource (this
     codebase has real examples of this — treat it as a fact to document, not a bug to
     silently fix).
   - Check whether any enum used in these schemas is missing from `specs/api/shared.md`'s
     "Common Enums" section.

3. **Read the current contract doc(s)** at `specs/api/<context>.md` (and `shared.md` if
   enums are in scope). If a context has no matching file yet (e.g. a brand-new slice),
   that itself is a gap — create the file.

4. **Diff and update**. For each context, update `specs/api/<context>.md` so it reflects
   the code exactly:
   - Add missing endpoints, remove endpoints that no longer exist.
   - Add missing query/path parameters, request fields, and response fields (including
     response-only fields like `id`/`created_at` that aren't in the request).
   - Note role/permission requirements per endpoint (this repo's contract docs don't
     currently have a dedicated section for this — add a short guard note next to the
     endpoint, e.g. `Requires: ADMIN` or `Requires: HUMAN_RESOURCES`, only where a guard
     exists; omit it where any authenticated user is allowed).
   - Note when a request body is form-encoded, multipart, or a bare JSON array/list rather
     than a JSON object.
   - Note real behavioral quirks that change the response a client sees (e.g. role-based
     result filtering, fields silently accepted but not persisted, an update endpoint
     returning a much smaller shape than the create/list endpoints for the same resource)
     as a one-line callout directly under the relevant endpoint or field block.
   - Update `specs/api/shared.md`'s "Common Enums" section for any new/changed enum.
   - Keep the existing terse, flat style of these docs (endpoint list, then plain field
     lists in fenced `text` blocks) — do not turn this into full OpenAPI/JSON-schema
     verbosity, and do not add a new file structure/section convention beyond what's
     already used across the other `specs/api/*.md` files.

5. **Do not invent.** Only document what the code actually does. If something is
   ambiguous (e.g. unclear whether a mismatch is an intentional API design choice or a
   bug), document the code's actual current behavior and flag the ambiguity to the user in
   your final summary rather than guessing or "fixing" the code.

6. **Report**. Summarize, per context touched: which files were created/changed, what was
   added/removed/corrected. Keep it a short changelog, not a restatement of the whole file.

## Out of scope

- Do not modify `app/slices/` code — this skill only edits `specs/api/*.md`. If auditing
  surfaces an actual code inconsistency (not just a doc gap), report it instead of fixing
  it silently.
- Do not touch `specs/<NNN-feature-name>/` — that's the separate per-feature Spec Kit
  workflow.
- Do not add tests (project policy — see `CLAUDE.md`).
