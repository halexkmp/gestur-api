# Quickstart: Employee Self-Service Salary Access

Validates the feature end-to-end against a running dev instance. Assumes `python app/main.py`
is up (dev server, `GENERATE_SCHEMAS=True`), and you have:

- `$EMPLOYEE_TOKEN` — bearer token for a `User` that has the `EMPLOYEE` role **and** a
  linked `Employee` record (via `Employee.user`).
- `$NO_LINK_TOKEN` — bearer token for a `User` that has the `EMPLOYEE` role but **no**
  linked `Employee` record (for the rejection scenario).
- `$HR_TOKEN` — an HR bearer token, used only to cross-check figures against the existing
  HR-facing endpoints.
- `$EMPLOYEE_ID` — the `Employee.id` linked to `$EMPLOYEE_TOKEN`'s user, used only to query
  the HR-facing endpoints for comparison, never sent by the self-service calls themselves.

## 1. Self-service salary summary (current month, no filters)

```bash
curl -s http://localhost:8000/employees/me/salary-summary \
  -H "Authorization: Bearer $EMPLOYEE_TOKEN"
```

Expected: `200`, `employee_id` equals the caller's own linked employee id, `month`/`year`
default to the current calendar month, and `gross_salary`/`advances_total`/`net_salary`
are populated (see `contracts/employees-self-service.md`).

## 2. Cross-check against the HR-facing view

```bash
curl -s "http://localhost:8000/employees/salary-summary/$EMPLOYEE_ID" \
  -H "Authorization: Bearer $HR_TOKEN"
```

Expected: every field (`gross_salary`, `advances_total`, `late_delay_minutes`,
`late_days_count`, `late_deduction_total`, `net_salary`) matches step 1 exactly —
validates spec FR-006/FR-008 and SC-004 (self-service figures match HR's view to the
cent and minute).

## 3. Self-service salary summary with explicit month/year

```bash
curl -s "http://localhost:8000/employees/me/salary-summary?month=6&year=2026" \
  -H "Authorization: Bearer $EMPLOYEE_TOKEN"
```

Expected: `200`, `month: 6`, `year: 2026`, figures reflect that month instead of the
current one.

## 4. Self-service salary advance history

```bash
curl -s http://localhost:8000/employees/me/salary-advances \
  -H "Authorization: Bearer $EMPLOYEE_TOKEN"
```

Expected: `200`, a list containing only advances belonging to the caller's own employee
record (compare against `GET /employees/salary-advances?employee_id=$EMPLOYEE_ID` with
`$HR_TOKEN` — same items). Empty list (`[]`), not an error, if none exist.

## 5. Salary advance history filtered by month/year

```bash
curl -s "http://localhost:8000/employees/me/salary-advances?month=6&year=2026" \
  -H "Authorization: Bearer $EMPLOYEE_TOKEN"
```

Expected: only advances dated in June 2026 are returned.

## 6. Rejection: Employee role without a linked Employee record

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/employees/me/salary-summary \
  -H "Authorization: Bearer $NO_LINK_TOKEN"

curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/employees/me/salary-advances \
  -H "Authorization: Bearer $NO_LINK_TOKEN"
```

Expected: `403` for both — confirms FR-005 (reject rather than return empty/null data).

## 7. Rejection: non-Employee role (e.g. HR token)

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/employees/me/salary-summary \
  -H "Authorization: Bearer $HR_TOKEN"
```

Expected: `403` — confirms these endpoints are gated on the `EMPLOYEE` role, not merely
on data existing (edge case: an HR user who also happens to have a linked `Employee` row
must still be rejected here).

## 8. Routing sanity check: `/me` is never captured by `/{employee_id}`

```bash
curl -s http://localhost:8000/employees/me/salary-summary \
  -H "Authorization: Bearer $EMPLOYEE_TOKEN" | head -c 40; echo
```

Expected: a JSON salary-summary payload, **not** a 404/422 from `GET /employees/{employee_id}`
attempting (and failing) to parse `"me"` as a UUID — confirms the new routers were
registered before the dynamic `get_employee_router` in `app/slices/employees/urls.py`
(see `research.md` Decision 3).
