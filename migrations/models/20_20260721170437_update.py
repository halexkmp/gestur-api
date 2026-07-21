from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "employee_schedule" (
    "id" UUID NOT NULL PRIMARY KEY,
    "monday" BOOL NOT NULL DEFAULT False,
    "tuesday" BOOL NOT NULL DEFAULT False,
    "wednesday" BOOL NOT NULL DEFAULT False,
    "thursday" BOOL NOT NULL DEFAULT False,
    "friday" BOOL NOT NULL DEFAULT False,
    "saturday" BOOL NOT NULL DEFAULT False,
    "sunday" BOOL NOT NULL DEFAULT False,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "employee_id" UUID NOT NULL UNIQUE REFERENCES "employee" ("id") ON DELETE CASCADE
);
        CREATE TABLE IF NOT EXISTS "justified_absence" (
    "id" UUID NOT NULL PRIMARY KEY,
    "absence_date" DATE NOT NULL,
    "reason" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "employee_id" UUID NOT NULL REFERENCES "employee" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_justified_a_employe_e79594" UNIQUE ("employee_id", "absence_date")
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "employee_schedule";
        DROP TABLE IF EXISTS "justified_absence";"""


MODELS_STATE = (
    "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"
)
