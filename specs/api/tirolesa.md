# Tirolesa API

Daily audit of tirolesa descents detected by a device against descents sold.

## Authentication

Device endpoints use `X-Device-Key: <key>`, returned once by `POST /tirolesa/devices`.
All other endpoints use the bearer token and `Requires: ADMIN or MANAGER`.
