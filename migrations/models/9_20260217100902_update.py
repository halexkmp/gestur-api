from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "employee" (
    "id" UUID NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "pix_key" VARCHAR(255),
    "salary" DECIMAL(10,2) NOT NULL,
    "active" BOOL NOT NULL DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
        CREATE TABLE IF NOT EXISTS "salary_advance" (
    "id" UUID NOT NULL PRIMARY KEY,
    "amount" DECIMAL(10,2) NOT NULL,
    "paid_at" DATE NOT NULL,
    "note" TEXT,
    "employee_id" UUID NOT NULL REFERENCES "employee" ("id") ON DELETE CASCADE
);
        ALTER TABLE "role" ALTER COLUMN "name" TYPE VARCHAR(15) USING "name"::VARCHAR(15);
        COMMENT ON COLUMN "role"."name" IS 'ADMIN: ADMIN
MANAGER: MANAGER
HUMAN_RESOURCES: HUMAN_RESOURCES
OPERATOR: OPERATOR';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        COMMENT ON COLUMN "role"."name" IS 'ADMIN: ADMIN
OPERATOR: OPERATOR';
        ALTER TABLE "role" ALTER COLUMN "name" TYPE VARCHAR(8) USING "name"::VARCHAR(8);
        DROP TABLE IF EXISTS "salary_advance";
        DROP TABLE IF EXISTS "employee";"""


MODELS_STATE = (
    "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"
    "5ejkqSCm4OeiG0YHt5/j+sy7x4"
)
