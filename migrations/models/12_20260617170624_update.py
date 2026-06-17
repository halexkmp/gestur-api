from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "journey_registry" (
    "id" UUID NOT NULL PRIMARY KEY,
    "timestamp" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "latitude" DOUBLE PRECISION NOT NULL,
    "longitude" DOUBLE PRECISION NOT NULL,
    "is_deleted" BOOL NOT NULL DEFAULT False,
    "edit_reason" TEXT,
    "original_data" JSONB,
    "user_id" UUID NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
        COMMENT ON COLUMN "role"."name" IS 'ADMIN: ADMIN
MANAGER: MANAGER
HUMAN_RESOURCES: HUMAN_RESOURCES
OPERATOR: OPERATOR
EMPLOYEE: EMPLOYEE';
        INSERT INTO "role" (id, name) VALUES ('7740ffa5-cb50-4e9f-95f9-248989038576', 'EMPLOYEE') ON CONFLICT (name) DO NOTHING;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        COMMENT ON COLUMN "role"."name" IS 'ADMIN: ADMIN
MANAGER: MANAGER
HUMAN_RESOURCES: HUMAN_RESOURCES
OPERATOR: OPERATOR';
        DROP TABLE IF EXISTS "journey_registry";"""


MODELS_STATE = (
    "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"
)
