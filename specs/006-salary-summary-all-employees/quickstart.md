# Quickstart: Validate Salary Summary for All Employees

Prerequisites: local dev server running (`python app/main.py`, or `uv run python app/main.py`),
local Postgres reachable per `.env`'s `DATABASE_URL`, and an HR-role user to authenticate as.
The repo's `scripts/seed_load_test_data.py` (see prior session) is a convenient way to get 100
employees with realistic salary advances and lateness data if the local DB is empty.

## 1. Get an HR token

```bash
curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "<hr-username>", "password": "<hr-password>"}' | jq -r .access_token
```

Save the token as `$TOKEN`.

## 2. Call the report for the current month

```bash
curl -s http://localhost:8000/employees/salary-summary \
  -H "Authorization: Bearer $TOKEN" | jq
```

Expected: `{"items": [...]}` with one entry per employee in the system (see
[contracts/salary-summary.md](./contracts/salary-summary.md) for the exact shape). Compare the
entry count to `GET /employees/` — they should match (spec SC-004).

## 3. Call the report for a specific month/year

```bash
curl -s "http://localhost:8000/employees/salary-summary?month=7&year=2026" \
  -H "Authorization: Bearer $TOKEN" | jq
```

Expected: same shape, `month`/`year` in every item echo `7`/`2026`.

## 4. Verify itemized advances match the total (spec FR-006)

```bash
curl -s "http://localhost:8000/employees/salary-summary?month=7&year=2026" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.items[] | select((.advances | map(.amount | tonumber) | add // 0) != (.advances_total | tonumber))'
```

Expected: no output — every employee's `advances_total` equals the sum of their `advances`.

## 5. Verify advances outside the period are excluded (spec Acceptance Scenario 2.2)

Pick one employee, create a salary advance dated in a different month (e.g. via
`POST /employees/salary-advances`), then re-run step 3 for the *original* month/year and
confirm that employee's `advances` list does not include the newly created one.

## 6. Verify permission enforcement (spec Acceptance Scenario 1.3)

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/employees/salary-summary \
  -H "Authorization: Bearer <non-hr-token>"
```

Expected: `403`.

## 7. Verify the old path is gone

```bash
curl -s -o /dev/null -w "%{http_code}\n" \
  "http://localhost:8000/employees/salary-summary/<any-employee-uuid>" \
  -H "Authorization: Bearer $TOKEN"
```

Expected: `404` (no route matches — `{employee_id}` is no longer part of this path).

## 8. Confirm the API contract doc was updated

```bash
grep -n "salary-summary" specs/api/employees.md
```

Expected: reflects the new `GET /employees/salary-summary?month&year` shape (no
`{employee_id}` path segment), and documents the nested `advances` field.
