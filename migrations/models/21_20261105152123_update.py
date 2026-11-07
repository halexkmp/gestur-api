from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "tirolesa_device" (
    "id" UUID NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "api_key_hash" VARCHAR(64) NOT NULL UNIQUE,
    "active" BOOL NOT NULL DEFAULT True,
    "last_seen_at" TIMESTAMPTZ,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
        CREATE TABLE IF NOT EXISTS "tirolesa_device_hour" (
    "id" UUID NOT NULL PRIMARY KEY,
    "hour" TIMESTAMPTZ NOT NULL,
    "device_id" UUID NOT NULL REFERENCES "tirolesa_device" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_tirolesa_de_device__f5033b" UNIQUE ("device_id", "hour")
);
        CREATE TABLE IF NOT EXISTS "tirolesa_justification" (
    "id" UUID NOT NULL PRIMARY KEY,
    "audit_date" DATE NOT NULL,
    "quantity" INT NOT NULL,
    "type" VARCHAR(8) NOT NULL,
    "reason" TEXT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "is_deleted" BOOL NOT NULL DEFAULT False,
    "deleted_at" TIMESTAMPTZ,
    "created_by_id" UUID NOT NULL REFERENCES "user" ("id") ON DELETE RESTRICT,
    "deleted_by_id" UUID REFERENCES "user" ("id") ON DELETE RESTRICT
);
COMMENT ON COLUMN "tirolesa_justification"."type" IS 'TEST: TEST\nCOURTESY: COURTESY\nOTHER: OTHER';
        CREATE TABLE IF NOT EXISTS "tirolesa_product" (
    "id" UUID NOT NULL PRIMARY KEY,
    "units_per_descent" INT NOT NULL DEFAULT 1,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "product_id" UUID NOT NULL UNIQUE REFERENCES "product" ("id") ON DELETE CASCADE
);
        CREATE TABLE IF NOT EXISTS "tirolesa_trip" (
    "id" UUID NOT NULL PRIMARY KEY,
    "start_at" TIMESTAMPTZ NOT NULL,
    "end_at" TIMESTAMPTZ NOT NULL,
    "clock_suspect" BOOL NOT NULL DEFAULT False,
    "received_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "device_id" UUID NOT NULL REFERENCES "tirolesa_device" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_tirolesa_tr_start_a_fcc9d9" ON "tirolesa_trip" ("start_at");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "tirolesa_device_hour";
        DROP TABLE IF EXISTS "tirolesa_justification";
        DROP TABLE IF EXISTS "tirolesa_product";
        DROP TABLE IF EXISTS "tirolesa_trip";
        DROP TABLE IF EXISTS "tirolesa_device";"""


MODELS_STATE = (
    "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"
    "jczq//A9GJuic="
)
