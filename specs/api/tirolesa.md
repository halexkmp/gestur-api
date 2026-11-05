# Tirolesa API

Daily audit of tirolesa descents detected by a device against descents sold.

## Authentication

Device endpoints use `X-Device-Key: <key>`, returned once by `POST /tirolesa/devices`.
All other endpoints use the bearer token and `Requires: ADMIN or MANAGER`.

---

## Devices

### POST /tirolesa/devices → 201

Requires: ADMIN or MANAGER

Request:

```text
name
```

Response. `api_key` appears only here and cannot be retrieved later:

```text
id
name
active
created_at
api_key
```

### GET /tirolesa/devices

Requires: ADMIN or MANAGER

```text
[
  {
    id
    name
    active
    last_seen_at   # nullable
    offline        # true when active and not seen for 15 minutes
  }
]
```

### PUT /tirolesa/devices/{device_id}

Requires: ADMIN or MANAGER. 404 when the device does not exist.

To replace a key, set `active` to false and create a new device.

Request, all optional:

```text
name
active
```

Response:

```text
id
name
active
last_seen_at   # nullable
```
