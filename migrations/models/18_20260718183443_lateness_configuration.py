from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "lateness_configuration" (
    "id" UUID NOT NULL PRIMARY KEY,
    "enabled" BOOL NOT NULL DEFAULT False,
    "expected_entrance_time" TIMETZ NOT NULL,
    "tolerance_minutes" INT NOT NULL DEFAULT 0,
    "deduction_interval_minutes" INT NOT NULL DEFAULT 0,
    "deduction_value" DECIMAL(10,2) NOT NULL DEFAULT 0,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
        -- Seed the single system-wide config row, disabled with zeroed numeric
        -- defaults; expected_entrance_time has no meaningful zero value so it is
        -- set to "now" at migration-apply time. Guarded by WHERE NOT EXISTS since
        -- this table has no natural unique key to key an ON CONFLICT off of.
        INSERT INTO "lateness_configuration"
            (id, enabled, expected_entrance_time, tolerance_minutes, deduction_interval_minutes, deduction_value)
        SELECT 'c9b1f5b0-6e5a-4b8b-9c1a-000000000001', false, CURRENT_TIME, 0, 0, 0
        WHERE NOT EXISTS (SELECT 1 FROM "lateness_configuration");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "lateness_configuration";"""


MODELS_STATE = (
    "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"
)
