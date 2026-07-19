# Quickstart: HR Lateness Tolerance & Salary Deduction Configuration

Validates the feature end-to-end against a running dev instance. Assumes `python app/main.py`
is up (dev server, `GENERATE_SCHEMAS=True`) and you have an HR-role bearer token
(`$HR_TOKEN`) and an employee linked to a user account (`$EMPLOYEE_ID`, `$USER_ID`).

## 1. Confirm defaults before any configuration exists

```bash
curl -s http://localhost:8000/employees/lateness-config \
  -H "Authorization: Bearer $HR_TOKEN"
```

Expected: `enabled: false`, all numeric fields `0`/`0.00` — even though no row exists yet
locally (dev DB uses `GENERATE_SCHEMAS`, not the migration seed).

## 2. Configure and enable

```bash
curl -s -X PUT http://localhost:8000/employees/lateness-config \
  -H "Authorization: Bearer $HR_TOKEN" -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "expected_entrance_time": "08:00:00",
    "tolerance_minutes": 10,
    "deduction_interval_minutes": 60,
    "deduction_value": 6.80
  }'
```

Expected: `200`, echoes back the values just set.

## 3. Produce a late check-in

Using the existing journey endpoint, register a check-in for `$USER_ID` today with a
timestamp effectively later than `08:00` local/UTC (the dev server's clock at call time
determines `JourneyRegistry.timestamp`, which is `auto_now_add`) — e.g. run this after
10:05 UTC, or adjust `expected_entrance_time` above to just before "now" so the call
counts as late:

```bash
curl -s -X POST http://localhost:8000/journey/ \
  -H "Authorization: Bearer $USER_TOKEN" \
  -F latitude=0.0 -F longitude=0.0 -F selfie=@/path/to/selfie.jpg
```

## 4. Read the salary summary and verify delay/deduction

```bash
curl -s "http://localhost:8000/employees/salary-summary/$EMPLOYEE_ID" \
  -H "Authorization: Bearer $HR_TOKEN"
```

Expected: `late_days_count: 1`, `late_delay_minutes` matches the actual delay, and
`late_deduction_total` equals `floor(delay_minutes / 60) * 6.80` (see `contracts/employees-lateness.md`
for the worked example). `net_salary` reflects the subtraction.

## 5. Disable and re-check

```bash
curl -s -X PUT http://localhost:8000/employees/lateness-config \
  -H "Authorization: Bearer $HR_TOKEN" -H "Content-Type: application/json" \
  -d '{
    "enabled": false,
    "expected_entrance_time": "08:00:00",
    "tolerance_minutes": 10,
    "deduction_interval_minutes": 60,
    "deduction_value": 6.80
  }'

curl -s "http://localhost:8000/employees/salary-summary/$EMPLOYEE_ID" \
  -H "Authorization: Bearer $HR_TOKEN"
```

Expected: `late_delay_minutes`, `late_days_count`, `late_deduction_total` all back to
zero; `net_salary` equals `gross_salary - advances_total` only, even though the same
late check-in from step 3 still exists.

## 6. Re-enable without resubmitting values (optional)

```bash
curl -s -X PUT http://localhost:8000/employees/lateness-config \
  -H "Authorization: Bearer $HR_TOKEN" -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "expected_entrance_time": "08:00:00",
    "tolerance_minutes": 10,
    "deduction_interval_minutes": 60,
    "deduction_value": 6.80
  }'
```

Expected: the deduction from step 4 reappears on the next salary-summary call, confirming
the same stored row was updated in place rather than a second row being created (spec
User Story 1, Acceptance Scenario 2).
