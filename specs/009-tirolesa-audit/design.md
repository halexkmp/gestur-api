# Tirolesa Daily Audit: Design

Date: 2026-11-05
Status: approved by owner, 2026-11-05. Changed 2026-11-06: the audit counts passengers.

## Change, 2026-11-06

The owner added `passengers` to the trip request, to solve two people riding together.
This replaces the descent as the audit unit, and it overrides anything below that
says otherwise:

- `POST /tirolesa/trips` requires `passengers`, from 1 to 10. The range is wide so a
  high reading is kept and investigated rather than rejected and lost.
- `passengers_detected` is the sum of `passengers` on the day's trips.
- `TirolesaProduct.units_per_descent` becomes `passengers_per_unit`: Solo 1, Tandem 2,
  sold per person 1. `passengers_sold` is `sum(quantity x passengers_per_unit)`.
- All `descents_*` audit fields become `passengers_*`. Justification `quantity` counts
  passengers.
- The fallback price is the mean `default_price / passengers_per_unit`.
- The gaps "an extra person on a paid solo ride" and "a tandem sold as two solos" are
  closed, provided the count is reliable.
- New hardware requirement: the device must count passengers without operator input.
  A presence sensor fires once for two riders, so it cannot supply this number. If an
  operator enters it, the audited person controls the audit.

- `TirolesaTrip.start_at` and `end_at` are not null and default to the current time at
  the database. The API request still requires `start` and `end`.

- `TirolesaDevice.offline` is now stored. A Vercel Schedule (`tirolesa-check-offline`,
  every 30 minutes from 06:00 to 17:30 São Paulo time, every day) calls
  `POST /tirolesa/devices/check-offline`, which marks active
  devices not seen for 15 minutes as offline. Any device request clears it. The status
  can lag by up to about an hour. No notification is sent yet; the owner will choose a
  method later.

## Intent

The business sells tirolesa (zipline) rides. Today nothing independent confirms that
the rides that happened match the rides that were sold, so a ride run without a
registered sale is invisible.

Two presence sensors, one at the start and one at the finish, will give the business
an independent count of finished descents. Only the finish side sends a request, so
each request proves a descent reached the end. A daily audit compares that count with sales, like
a cash audit: each day shows descents detected, descents sold, the money for those
sales, and anything left unexplained.

## Goals

- Receive finished trips reliably, including trips delayed by lost connectivity.
- Produce a per-day audit of descents detected against descents sold.
- Let an ADMIN or MANAGER justify test and courtesy rides, with a reason and a record
  of who did it.
- Show the money tied to tirolesa sales and the estimated value of unexplained rides.
- Show when the device looks unhealthy, so a dead device is not read as a quiet day.

## Non-goals

- Linking a detected descent to a specific sale, ticket or customer.
- Counting riders on a descent (see Approaches, option B).
- Auditing all money received. Payments are recorded per sale, so a mixed sale cannot
  be split by product. Tirolesa money is the sum of `SaleItem.total_price`.
- Supporting more than one tirolesa line.
- Live alerts or notifications. The audit is read on demand.
- Formally closing or locking a day.
- Any frontend work. The frontend is a separate project; this delivers the API.

## Anti-goals

The feature fails, even if it technically works, if:

- An audited operator can excuse or hide their own rides. Trips are
  append-only through the API, and only ADMIN or MANAGER can justify rides.
- Routine test and courtesy rides make every day show a difference, so people stop
  reading the audit.
- A device outage or lost connection lowers the count without anyone being warned.
  A failed sensor on a device that stays online is a narrower case, accepted by the
  owner (see Known limitations).

## Constraints

- Rides are never sold one day and used another. Each local date stands alone.
- Two people can ride together, and a presence sensor fires once for them. The audit
  unit is therefore the **descent**, not the rider.
- Test and courtesy rides happen and have no sale.
- No hardware has been bought. This design defines what the hardware must do.
- Runs as a Vercel serverless function: no background workers and no in-process state
  shared between requests.
- Project rules apply: Vertical Slice layout, explicit use-case parameters, no new
  tests, no hand-written migrations, `specs/api/` updated in the same change.

## Approaches

### How test and courtesy rides are excused

- **A. A manager justifies rides after the fact. Chosen by the owner.** Sensors count
  everything, and a manager records the exceptions. Slight daily work, but the people
  being audited cannot excuse their own rides, and there is a record.
- B. The operator marks a test mode beforehand. Rejected: the audited person controls
  what is audited.
- C. Courtesy rides as R$0 sales. Rejected: operators create those sales themselves,
  and it does not cover test rides.

### How two riders together are handled

- **A. Audit descents, and sell tandem as its own product. Chosen by the owner.**
  Cheap, works with simple presence sensors. Known gap: an extra person added to a
  paid solo ride is not detected.
- B. Rider-counting sensor (overhead depth or camera). Fully independent and closes
  that gap, but costs more, needs testing at trolley speed, and a camera raises LGPD
  concerns. Left open as a later addition: a rider count field on the trip request.
- C. Presence sensors with no sales change, showing a range. Rejected: up to half the
  riders could go unpaid unnoticed.

## Design

### Decided by the owner

- Two sensors, start and finish. They are paired outside the API, and only the finish
  side sends a request: one request per trip, with a UUID and start and end datetimes.
- A trip with no finish is never sent. Reaching the finish is the proof of a descent.
- A daily audit comparing sensor counts with sales.
- Rides are compared per local day.
- Managers justify test and courtesy rides after the fact (approach A).
- Descents are the audit unit, and tandem is sold as its own product (approach A).
- Sales below a product's default price still count as sold, and each day shows how
  many descents were sold that way. Any logged-in user can create or edit a sale at
  any price, including R$0, so this makes covering a ride with a cheap sale visible
  without changing the sales flow. It flags the case and does not prevent it.

### Calls made by the designer

The owner has not specifically confirmed these.

1. **The UUID identifies the trip,** and is that trip's primary key. Resending the
   same UUID is ignored. `descents_detected` is the number of trips on that local
   date, placed by `start`.
2. **Each audited product has `units_per_descent`,** default 1. Solo = 1, Tandem = 1.
   A product sold per person that always rides in pairs would be 2. This works
   whether or not every descent has two people.
   For each linked product and local day,
   `ceil(sum of quantity / units_per_descent)`, because 3 people on a pairs product
   need at least 2 descents. `descents_sold` is the sum across products, and is
   always a whole number.
3. **Double readings are handled on the device,** since it decides what a trip is.
   The API does not filter trips by time.
4. **A separate `tirolesa` context,** not an extension of `reports`, because it owns
   its own models and device endpoints.
5. **Tirolesa products are linked in their own table,** leaving the `Product` API
   unchanged.
6. **Non-canceled sales count,** including `PENDING`, by the local date of
   `Sale.created_at`. A sold ride is a sold ride; whether it was paid is a separate
   question this audit does not answer.
7. **Days use the local time offset** from `LatenessConfiguration.utc_offset_minutes`,
   falling back to -180, as the attendance features do.
8. **Justifications are soft-deleted,** recording who deleted them, so the record of
   an excuse cannot be silently erased. Past days always recalculate, so a late trip
   or a changed link updates them.
9. **Device health is stored by the hour.** Any device request marks the device as
   seen for the current UTC hour. The audit shows hours online per day, so a past
   outage stays visible after it recovers, including a day when nothing was sold.
   Operating hours are not modelled, so the reader judges whether the hours look right.
10. **A new guard, `ensure_admin_or_manager`,** in `app/shared/security/permissions.py`.
    It protects all management and audit endpoints. It checks the role only, so a
    manager who also sells rides could justify their own day. The record of who
    justified each ride is the control for that case.
11. **Trips with a bad clock are kept, never dropped.** A `start` or `end` over 5
    minutes in the future, a `start` over 7 days old, or an `end` that is not after
    `start` is stored with `clock_suspect = true`. The audit places such a trip on the
    local date of `received_at` and counts it per day.

### Hardware requirements

- Programmable board with a presence sensor at each end (ESP32-class is the expected
  choice).
- A link between the two ends, or a single controller receiving both sensors, so the
  finish side knows the trip's start time. How this works is not visible to the API.
- The finish side has Wi-Fi or 4G and an HTTPS client that can send a custom header
  with the device key.
- Pairs each finish with its start, including riders who overlap on the line, and
  filters repeat triggers.
- Non-volatile storage for trips that could not be sent, resending until acknowledged.
- Real-time clock, resynced from `server_time` in the heartbeat response.
- Heartbeat every 5 minutes.
- Generates a UUID per trip.

### Data model

Added to `app/shared/db/models.py`; migration generated separately with Aerich.

`TirolesaDevice` (`tirolesa_device`): `id`, `name`, `api_key_hash` (unique), `active`,
`last_seen_at` (nullable), `created_at`.

`TirolesaTrip` (`tirolesa_trip`): `id` (UUID from the device, primary key), `device`
(FK), `start_at`, `end_at`, `clock_suspect` (bool, default false), `received_at`.
Indexed on `start_at`.

`TirolesaDeviceHour` (`tirolesa_device_hour`): `id`, `device` (FK), `hour` (datetime,
truncated to the UTC hour). Unique on (`device`, `hour`).

`TirolesaProduct` (`tirolesa_product`): `id`, `product` (one-to-one FK),
`units_per_descent` (int, default 1), `created_at`.

`TirolesaJustification` (`tirolesa_justification`): `id`, `audit_date` (date),
`quantity` (int, descents), `type` (`TirolesaJustificationType`), `reason` (text),
`created_by` (FK User), `created_at`, `is_deleted`, `deleted_by` (FK User, nullable),
`deleted_at` (nullable).

Enums added to `app/shared/db/enums.py`:

- `TirolesaJustificationType`: `TEST`, `COURTESY`, `OTHER`
- `TirolesaAuditStatus`: `BALANCED`, `UNEXPLAINED`, `SOLD_ABOVE_DETECTED`

### Device authentication

Devices send `X-Device-Key: <key>`. The key is 32 random bytes, generated by the API,
shown once at creation. Only its SHA-256 hash is stored, and lookup is by hash. An
inactive device or unknown key returns 401. To replace a key, deactivate the device
and create a new one. Device auth is a dependency in `app/shared/security/`.

### Endpoints

All live under the `/tirolesa` prefix, in a new `app/slices/tirolesa/` context.

**Device (X-Device-Key)**

`POST /tirolesa/trips` records one finished trip.

```text
Request:  { id, start, end }   # all required
Response: { id, duplicate }    # 201 when new, 200 when the id already exists
```

- A repeated `id` is ignored and returns 200, so resending is always safe.
- A trip with a bad clock is accepted and stored with `clock_suspect = true`.
- Updates `last_seen_at` and the device's hourly record.

`POST /tirolesa/devices/heartbeat` updates `last_seen_at` and the hourly record.

```text
Response: { server_time }
```

**Management (ADMIN or MANAGER)**

- `POST /tirolesa/devices` → 201, with `api_key` returned this one time
- `GET /tirolesa/devices`, including `last_seen_at` and an `offline` flag, true when
  an active device has not been seen for 15 minutes
- `PUT /tirolesa/devices/{device_id}` for `name` and `active`
- `POST /tirolesa/products` → 201 with `product_id`, `units_per_descent`
- `GET /tirolesa/products`
- `DELETE /tirolesa/products/{tirolesa_product_id}` → 204
- `GET /tirolesa/audit?date_from&date_to`, both required local dates, at most 62 days
- `POST /tirolesa/audit/justifications` → 201 with `audit_date`, `quantity` (at least
  1), `type`, `reason` (required)
- `DELETE /tirolesa/audit/justifications/{id}` → 204, soft delete

### Audit response

One row per local date in the range, including days with no activity:

```text
date
descents_detected        # trips on this local date
descents_sold
descents_below_default_price   # included in descents_sold; see below
descents_justified
unexplained              # detected - sold - justified, floored at 0
sold_above_detected      # sold + justified - detected, floored at 0
sales_amount             # sum of SaleItem.total_price for linked products
estimated_unpaid_value   # unexplained x average price per descent
status                   # TirolesaAuditStatus
device_hours             # distinct hours the device was seen that local date
clock_suspect_trips      # trips placed on this date by received_at
sensor_warning           # see below
justifications: [ { id, quantity, type, reason, created_by: { id, name }, created_at } ]
```

- `status` is `UNEXPLAINED` when `unexplained > 0`, `SOLD_ABOVE_DETECTED` when
  `sold_above_detected > 0`, otherwise `BALANCED`.
- Average price per descent is `sales_amount / descents_sold` for that day. With no
  sales that day, use the mean `default_price * units_per_descent` of linked products.
- `SOLD_ABOVE_DETECTED` means a sensor failed or a sale had no ride, and is the main
  sign of a failed finish sensor. It never means
  unpaid rides, so it carries no money value.
- `descents_below_default_price` applies the `descents_sold` calculation to sale items
  with `unit_price` below the product's current `default_price`. It does not change
  `status`, because real discounts and partner prices are normal. A manager reads it.
- `sensor_warning` is true when `device_hours` is 0 or `clock_suspect_trips > 0`.
- Counts, money calculation and status live in pure functions in `domain/rules.py`.

### Slices

```text
app/slices/tirolesa/
    urls.py
    record_trip/              # device
    device_heartbeat/         # device
    create_device/
    list_devices/
    update_device/
    link_product/
    list_products/
    unlink_product/
    get_daily_audit/          # domain/rules.py holds the audit calculation
    create_justification/
    delete_justification/
```

Wire the router into `app/main.py`.

### Documentation changes

- New `specs/api/tirolesa.md`.
- `specs/api/shared.md`: new enums, `X-Device-Key` auth exception, and the
  ADMIN/MANAGER requirement.
- `CLAUDE.md`: add `tirolesa` to the context lists.

## Known limitations

- An extra person on a paid solo ride is not detected.
- A ride covered by a R$0 or below-price sale still balances the day. It is only
  flagged by `descents_below_default_price`, which a manager must read. Sale editing
  stays open to any logged-in user.
- Changing a product's `default_price` changes the below-price figure for past days.
- A tandem sold as two solos reads as `SOLD_ABOVE_DETECTED`, and could mask an unsold
  ride that same day.
- **A failed finish sensor, or a failed link between the two ends, produces no trips
  while the device still looks online.** The audit only shows it as
  `SOLD_ABOVE_DETECTED`, and unsold rides during that time are not detected. Someone
  blocking the finish sensor has the same effect. The owner chose this over counting
  trips with no finish.
- Someone walking past both sensors can count as a descent. A manager would justify it
  or investigate it, which is the intended behaviour.
- Audit figures for a day can change if the device delivers delayed trips later.
- A user who created or deleted a justification cannot be deleted, so the record of an
  excuse survives. Deactivate that user instead.

## Left to the builder

- File-level structure inside each slice, following the existing patterns.
- How a repeated trip `id` is ignored, provided it is safe under concurrent requests. Serverless means two requests can run at once.
- Date-range handling in queries, converting local dates to UTC bounds.
- Exact Pydantic schema names and error messages.
