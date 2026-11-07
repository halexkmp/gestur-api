# Tirolesa Daily Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Receive finished tirolesa trips from a device and give ADMIN/MANAGER a daily audit of descents detected against descents sold, with justifications.

**Architecture:** A new `app/slices/tirolesa/` context of vertical slices, plus four new models. Devices authenticate with a hashed `X-Device-Key`. The audit is calculated on each read by pure functions in `get_daily_audit/domain/rules.py`, with nothing stored.

**Tech Stack:** FastAPI, Tortoise-ORM, PostgreSQL, Aerich.

**Spec:** `specs/009-tirolesa-audit/design.md`

## Global Constraints

- Vertical Slice layout with fixed file names: `application/use_case.py`, `ui/route.py`, `ui/schemas.py`, `infra/repository.py`, `domain/rules.py`.
- Use-case parameters are explicit and typed: no `dict` or `**kwargs`.
- **No test files.** This overrides the TDD steps of the executing skills. Each task's checks are run by hand and nothing from them is committed.
- **No migration files.** The owner runs `aerich migrate` and `aerich upgrade` separately.
- `specs/api/tirolesa.md` and `specs/api/shared.md` change in the same commit as the code they describe.
- Do not touch the `sales` or `products` slices.
- Commit messages are short and lower-case, and end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- All work stays on branch `feature/009-tirolesa-audit`.

Manual checks need the local server (`uvicorn app.main:app --port 8000`, where `GENERATE_SCHEMAS` creates the new tables), and `$TOKEN` from `POST /auth/login` for an ADMIN user.

## Review Focus

1. Two requests with the same trip id at the same moment: one 201 and one 200, never a 500. Task 3.
2. A device sends a datetime with no timezone: 422, not a guess at the wrong day. Task 3.
3. Activity around local midnight: a 23:30 local sale and trip stay on that date even though it is already the next day in UTC. Task 6.
4. A day with no sales, or no linked products at all: no division by zero, and a zero or fallback value. Task 6.
5. A deactivated device resending stored trips: 401, and nothing stored. Task 3.

---

### Task 1: Foundations

**Files:**
- Modify: `app/shared/db/enums.py`, `app/shared/db/models.py`, `app/shared/security/permissions.py`, `app/main.py`, `CLAUDE.md`, `specs/api/shared.md`
- Create: `app/shared/security/device_auth.py`, `app/slices/tirolesa/urls.py`, `specs/api/tirolesa.md`

**Interfaces:**
- Produces: enums `TirolesaJustificationType`, `TirolesaAuditStatus`; models `TirolesaDevice`, `TirolesaTrip`, `TirolesaDeviceHour`, `TirolesaProduct`, `TirolesaJustification`
- Produces: `ensure_admin_or_manager(current_user) -> None`
- Produces: `generate_device_key() -> tuple[str, str]` returning `(plain_key, key_hash)`, and `async get_current_device(x_device_key: Optional[str] = Header(default=None)) -> TirolesaDevice`
- Produces: `router` with prefix `/tirolesa`, tag `tirolesa`

- [ ] **Step 1: Add the enums and models**

Use the fields and table names in the design's Data model section. `TirolesaTrip.id` is `UUIDField(pk=True)`, always set from the device's request. Add `index=True` on `start_at`, `unique_together = (("device", "hour"),)` on `TirolesaDeviceHour`, and related names `created_justifications` and `deleted_justifications` on the two `User` FKs of `TirolesaJustification`.

- [ ] **Step 2: Add `ensure_admin_or_manager`**

Same shape as `ensure_hr_or_admin`, with detail `"Forbidden: Admin or Manager role required"`.

- [ ] **Step 3: Implement `device_auth.py`**

`secrets.token_urlsafe(32)` for the key and `hashlib.sha256` hex for the hash. `get_current_device` raises 401 `"Invalid device key"` for a missing or unknown key or an inactive device. On success it sets `last_seen_at`, then runs `TirolesaDeviceHour.get_or_create(device=device, hour=<now truncated to UTC hour>)`. All device health tracking lives in this one place.

- [ ] **Step 4: Create the router, wire it into `app/main.py`, and start the docs**

`urls.py` starts with no included routers. `specs/api/tirolesa.md` starts with a heading and a note on `X-Device-Key` auth. In `shared.md`, add the two enums, `X-Device-Key` as an auth exception, and `Requires: ADMIN or MANAGER` for `/tirolesa/*` management endpoints. In `CLAUDE.md`, add `tirolesa` to the context list and to the `specs/api/` file list.

- [ ] **Step 5: Verify**

Run: `python -c "import app.main"`, then start the server.
Expected: no import error, and the five `tirolesa_*` tables exist.

- [ ] **Step 6: Commit**

```bash
git add app CLAUDE.md specs/api
git commit -m "add tirolesa models, device auth and router"
```

### Task 2: Device management

**Files:**
- Create: `app/slices/tirolesa/create_device/`, `list_devices/`, `update_device/` (each with `application/use_case.py`, `ui/route.py`, `ui/schemas.py`, `infra/repository.py`)
- Modify: `app/slices/tirolesa/urls.py`, `specs/api/tirolesa.md`

**Interfaces:**
- Consumes: `generate_device_key`, `ensure_admin_or_manager`, `TirolesaDevice`

- [ ] **Step 1: `POST /devices` → 201**

`CreateDevice.execute(name: str) -> tuple[TirolesaDevice, str]`, returning the device and plain key. Response: `id`, `name`, `active`, `created_at`, `api_key`.

- [ ] **Step 2: `GET /devices`**

Response list: `id`, `name`, `active`, `last_seen_at`, `offline`. `offline` is `active and (last_seen_at is None or older than 15 minutes)`, calculated in the use case. `api_key_hash` is never returned.

- [ ] **Step 3: `PUT /devices/{device_id}`**

`UpdateDevice.execute(device_id: UUID, name: Optional[str], active: Optional[bool]) -> TirolesaDevice`. Unknown id returns 404. Response has the `GET` fields except `offline`.

- [ ] **Step 4: Include the routers, document all three endpoints**

- [ ] **Step 5: Verify**

Create a device with `$TOKEN` and keep its `api_key`. Rename it with `PUT`. Call `GET /tirolesa/devices` with a non-manager token.
Expected: `api_key` appears only in the create response; 403 for the non-manager.

- [ ] **Step 6: Commit**

```bash
git add app/slices/tirolesa specs/api/tirolesa.md
git commit -m "add tirolesa device management"
```

### Task 3: Device endpoints

**Files:**
- Create: `app/slices/tirolesa/record_trip/` (with `domain/rules.py`), `app/slices/tirolesa/device_heartbeat/` (`ui/` and `application/` only, no repository)
- Modify: `app/slices/tirolesa/urls.py`, `specs/api/tirolesa.md`

**Interfaces:**
- Consumes: `get_current_device`, `TirolesaTrip`
- Produces: `is_clock_suspect(start: datetime, end: datetime, now: datetime) -> bool` in `record_trip/domain/rules.py`

- [ ] **Step 1: Implement `is_clock_suspect`**

True when `start` or `end` is over 5 minutes after `now`, `start` is over 7 days before `now`, or `end <= start`. Constants at the top of the file.

- [ ] **Step 2: Implement `POST /trips`**

Request fields `id: UUID`, `start: AwareDatetime`, `end: AwareDatetime`. `RecordTrip.execute(device_id: UUID, trip_id: UUID, start: datetime, end: datetime) -> bool` returns `True` when created. The repository calls `TirolesaTrip.create` and turns `tortoise.exceptions.IntegrityError` into `False`, with no existence check first, so concurrent duplicates are safe. Response `{ id, duplicate }`: set 201 when created, 200 when duplicate, through the injected `Response`.

- [ ] **Step 3: Implement `POST /devices/heartbeat`**

Returns `{ server_time }` in UTC. The dependency has already recorded the visit.

- [ ] **Step 4: Include the routers, document both endpoints**

Include the 201/200 behaviour and the required timezone offset.

- [ ] **Step 5: Verify**

```bash
ID=$(python -c "import uuid;print(uuid.uuid4())")
BODY="{\"id\":\"$ID\",\"start\":\"2026-11-05T14:00:00-03:00\",\"end\":\"2026-11-05T14:01:30-03:00\"}"
curl -si -XPOST localhost:8000/tirolesa/trips -H "X-Device-Key: $KEY" -H 'Content-Type: application/json' -d "$BODY"
```

Expected: 201 on the first call and 200 with `"duplicate": true` on a resend. Send the same request twice in parallel with `&`: one 201 and one 200, no 500. A `start` without an offset returns 422. A wrong key returns 401. After setting the device inactive, a new trip returns 401 and no row is stored; set it active again afterwards. A trip with `end` before `start` returns 201 and has `clock_suspect = true` in the database. `last_seen_at` updates, and one `tirolesa_device_hour` row exists after several calls.

- [ ] **Step 6: Commit**

```bash
git add app/slices/tirolesa specs/api/tirolesa.md
git commit -m "add tirolesa trip and heartbeat endpoints"
```

### Task 4: Product linking

**Files:**
- Create: `app/slices/tirolesa/link_product/`, `list_products/`, `unlink_product/`
- Modify: `app/slices/tirolesa/urls.py`, `specs/api/tirolesa.md`

- [ ] **Step 1: Implement the three slices**

- `POST /products` → 201. `units_per_descent: int = Field(default=1, ge=1)`. `LinkProduct.execute(product_id: UUID, units_per_descent: int) -> TirolesaProduct`. Unknown product returns 404, already linked returns 409.
- `GET /products`: `id`, `product_id`, `product_name`, `units_per_descent`.
- `DELETE /products/{tirolesa_product_id}` → 204, a hard delete, 404 if missing.

All call `ensure_admin_or_manager`.

- [ ] **Step 2: Include the routers, document the endpoints**

- [ ] **Step 3: Verify**

Link a product, list it, link it again (409), unlink it (204), unlink it again (404).

- [ ] **Step 4: Commit**

```bash
git add app/slices/tirolesa specs/api/tirolesa.md
git commit -m "add tirolesa product linking"
```

### Task 5: Justifications

**Files:**
- Create: `app/slices/tirolesa/create_justification/`, `delete_justification/`
- Modify: `app/slices/tirolesa/urls.py`, `specs/api/tirolesa.md`

- [ ] **Step 1: `POST /audit/justifications` → 201**

Request: `audit_date: date`, `quantity: int = Field(ge=1)`, `type: TirolesaJustificationType`, `reason: str = Field(min_length=1)`. `CreateJustification.execute(audit_date: date, quantity: int, justification_type: TirolesaJustificationType, reason: str, created_by_id: UUID) -> TirolesaJustification`. Response: `id`, `audit_date`, `quantity`, `type`, `reason`, `created_at`.

- [ ] **Step 2: `DELETE /audit/justifications/{justification_id}` → 204**

`DeleteJustification.execute(justification_id: UUID, deleted_by_id: UUID) -> bool`. Sets `is_deleted`, `deleted_by`, `deleted_at`. Missing or already deleted returns 404. The row is never removed.

- [ ] **Step 3: Include the routers, document the endpoints**

- [ ] **Step 4: Verify**

Create one (201), with `quantity: 0` (422) and `reason: ""` (422). Delete it twice (204 then 404). The row remains with `deleted_by` set.

- [ ] **Step 5: Commit**

```bash
git add app/slices/tirolesa specs/api/tirolesa.md
git commit -m "add tirolesa audit justifications"
```

### Task 6: Daily audit

**Files:**
- Create: `app/slices/tirolesa/get_daily_audit/` (including `domain/rules.py`)
- Modify: `app/slices/tirolesa/urls.py`, `specs/api/tirolesa.md`

**Interfaces:**
- Consumes: all Task 1 models, `TirolesaAuditStatus`
- Produces, in `domain/rules.py`:

```python
@dataclass(frozen=True)
class SoldLine:
    product_id: UUID
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    default_price: Decimal
    units_per_descent: int

@dataclass(frozen=True)
class LinkedProduct:
    default_price: Decimal
    units_per_descent: int

@dataclass(frozen=True)
class DayFigures:
    descents_detected: int
    descents_sold: int
    descents_below_default_price: int
    descents_justified: int
    unexplained: int
    sold_above_detected: int
    sales_amount: Decimal
    estimated_unpaid_value: Decimal
    status: TirolesaAuditStatus
    device_hours: int
    clock_suspect_trips: int
    sensor_warning: bool

def local_date(moment: datetime, utc_offset_minutes: int) -> date: ...
def trip_audit_date(start_at: datetime, received_at: datetime, clock_suspect: bool, utc_offset_minutes: int) -> date: ...
def count_descents(lines: list[SoldLine]) -> int: ...
def calculate_day(trips: int, lines: list[SoldLine], justified: int, device_hours: int, clock_suspect_trips: int, linked: list[LinkedProduct]) -> DayFigures: ...
```

- [ ] **Step 1: Implement the rules**

`count_descents` groups by `product_id`, sums quantity, and adds `ceil(total / units_per_descent)` per product. Below-price descents are `count_descents` of the lines with `unit_price < default_price`. Status, floors and `estimated_unpaid_value` follow the design's Audit response section. With no sales, the average is the mean of `default_price * units_per_descent` over `linked`; with no linked products it is 0. Round money to 2 decimal places.

- [ ] **Step 2: Check the rules by hand**

Run `python -c` with assertions, not committed.
Expected:
- `local_date(datetime(2026,11,6,2,30,tzinfo=utc), -180) == date(2026,11,5)`
- 3 units at `units_per_descent=2` gives 2 descents; 2 lines of different products at 1 unit each gives 2
- `calculate_day(trips=40, ...)` with 35 sold and 3 justified gives `unexplained=2`, status `UNEXPLAINED`
- 0 trips with 5 sold gives `sold_above_detected=5`, status `SOLD_ABOVE_DETECTED`, `estimated_unpaid_value=0`
- 1 trip, no sales, `linked=[]` gives `estimated_unpaid_value=0`, no exception
- `device_hours=0` gives `sensor_warning=True`
- 3 sold at R$0 against a R$50 default gives `descents_below_default_price=3`, status `BALANCED` with 3 trips

- [ ] **Step 3: Implement the repository**

`GetDailyAuditRepository` methods, each taking UTC bounds `(start: datetime, end: datetime)` with `end` exclusive:

- `get_utc_offset_minutes() -> int`: first `LatenessConfiguration`, else -180
- `get_linked_products() -> list[TirolesaProduct]`, with `product` prefetched
- `get_trips(start, end) -> list[TirolesaTrip]`: `Q(clock_suspect=False, start_at in range) | Q(clock_suspect=True, received_at in range)`
- `get_sale_items(product_ids: list[UUID], start, end) -> list[SaleItem]`: product in the list, `sale__created_at` in range, `sale__status__not=SaleStatus.CANCELED`, with `sale` prefetched
- `get_justifications(date_from: date, date_to: date) -> list[TirolesaJustification]`: `is_deleted=False`, with `created_by` prefetched
- `get_device_hours(start, end) -> list[datetime]`

Bounds are `datetime.combine(local_day, time.min, utc) - timedelta(minutes=offset)`, with `end` built from `date_to + 1 day`.

- [ ] **Step 4: Implement the use case and route**

`GET /audit?date_from&date_to`, both required `date`. `ensure_admin_or_manager`. Define `AuditDay` in `application/use_case.py` as a dataclass with `date: date`, `figures: DayFigures`, `justifications: list[TirolesaJustification]`. `GetDailyAudit.execute(date_from: date, date_to: date) -> list[AuditDay]` raises `ValueError`, mapped to 400, when `date_from > date_to` or the range exceeds 62 days. It groups the repository results by local date, places trips with `trip_audit_date`, sums non-deleted justification quantities per `audit_date`, and returns one row for every date in the range, in ascending order. `device_hours` is the number of distinct hours falling on that local date, so one device's hours are never counted twice. Row fields match the design's Audit response.

- [ ] **Step 5: Include the router, document the endpoint**

Document all response fields and the meaning of each status.

- [ ] **Step 6: Verify end to end**

Link a product at R$50. Create 2 sales for it today, then 3 trips with today's times. Add a justification of 1.
Expected: `GET /tirolesa/audit` for today shows `descents_detected=3`, `descents_sold=2`, `descents_justified=1`, status `BALANCED`. Delete the justification: `unexplained=1`, `estimated_unpaid_value=50.00`. Add a trip at 23:30 local and confirm it stays on today. A range with no activity returns zero rows for each day, not an error. 63 days returns 400.

- [ ] **Step 7: Commit**

```bash
git add app/slices/tirolesa specs/api/tirolesa.md
git commit -m "add tirolesa daily audit"
```

### Task 7: Contract check

**Files:**
- Modify: `specs/api/tirolesa.md`, `specs/api/shared.md` if anything differs

- [ ] **Step 1: Run the `update-api-contract` skill**

Expected: `specs/api/` matches the `tirolesa` routes and schemas.

- [ ] **Step 2: Commit any corrections**

```bash
git add specs/api
git commit -m "sync tirolesa api contract"
```
