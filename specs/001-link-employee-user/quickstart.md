# Quickstart: Validate Employee ↔ User Linking

Prerequisites:
- Dev server running (`python app/main.py`), local Postgres reachable, migrations applied (`aerich upgrade`).
- An HR-role JWT (`Authorization: Bearer <token>`) — obtain via the existing login endpoint (`specs/api/auth.md`).
- Two existing user accounts not yet linked to any employee: `USER_A_ID`, `USER_B_ID`.

All request/response shapes referenced below are defined in
`contracts/employees.md` (delta) and `specs/api/employees.md` (full current contract).

## Scenario 1 — Create an employee with a linked user (User Story 1)

```bash
curl -X POST http://localhost:8000/employees/ \
  -H "Authorization: Bearer $HR_TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"Ana Silva","salary":3000,"start_date":"2026-07-17","user_id":"'$USER_A_ID'"}'
```
Expected: `200`, response body includes `"user_id": "<USER_A_ID>"`.

## Scenario 2 — Create an employee with no linked user

```bash
curl -X POST http://localhost:8000/employees/ \
  -H "Authorization: Bearer $HR_TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"Bruno Costa","salary":2800,"start_date":"2026-07-17"}'
```
Expected: `200`, response body includes `"user_id": null`.

## Scenario 3 — Reject linking an already-linked user

Repeat Scenario 1's request again (still referencing `USER_A_ID`, now already linked to
"Ana Silva") for a second, different employee.
Expected: `400 Bad Request`.

## Scenario 4 — Reject an unknown user id

```bash
curl -X POST http://localhost:8000/employees/ \
  -H "Authorization: Bearer $HR_TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"Carla Dias","salary":2900,"start_date":"2026-07-17","user_id":"00000000-0000-0000-0000-000000000000"}'
```
Expected: `404 Not Found`.

## Scenario 5 — Link a user to an existing employee via edit (User Story 2)

Using the employee created in Scenario 2 (`EMPLOYEE_B_ID`, no linked user):
```bash
curl -X PUT http://localhost:8000/employees/$EMPLOYEE_B_ID \
  -H "Authorization: Bearer $HR_TOKEN" -H "Content-Type: application/json" \
  -d '{"user_id":"'$USER_B_ID'"}'
```
Expected: `200`, response body includes `"user_id": "<USER_B_ID>"`.

## Scenario 6 — Clear a linked user via edit

```bash
curl -X PUT http://localhost:8000/employees/$EMPLOYEE_B_ID \
  -H "Authorization: Bearer $HR_TOKEN" -H "Content-Type: application/json" \
  -d '{"user_id": null}'
```
Expected: `200`, response body includes `"user_id": null`.

## Scenario 7 — Omitting user_id on edit leaves the link untouched

Repeat Scenario 5 to relink `USER_B_ID`, then:
```bash
curl -X PUT http://localhost:8000/employees/$EMPLOYEE_B_ID \
  -H "Authorization: Bearer $HR_TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"Bruno C. Costa"}'
```
Expected: `200`, response body still includes `"user_id": "<USER_B_ID>"` (unchanged).

## Scenario 8 — View the link (User Story 3)

```bash
curl http://localhost:8000/employees/$EMPLOYEE_B_ID -H "Authorization: Bearer $HR_TOKEN"
curl http://localhost:8000/employees/ -H "Authorization: Bearer $HR_TOKEN"
```
Expected: both responses include `user_id` for the employee (matching whatever the last
successful scenario left it as).
