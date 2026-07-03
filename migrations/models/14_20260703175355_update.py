from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "loan" (
    "id" UUID NOT NULL PRIMARY KEY,
    "principal_amount" DECIMAL(10,2) NOT NULL,
    "interest_rate" DECIMAL(5,2) NOT NULL,
    "total_amount" DECIMAL(10,2) NOT NULL,
    "installments_qty" INT NOT NULL,
    "due_day" INT NOT NULL,
    "start_date" DATE NOT NULL,
    "end_date" DATE NOT NULL,
    "status" VARCHAR(8) NOT NULL DEFAULT 'ACTIVE',
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "partner_id" UUID NOT NULL REFERENCES "partner" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "loan"."status" IS 'ACTIVE: ACTIVE\nPAID: PAID\nCANCELED: CANCELED';
        CREATE TABLE IF NOT EXISTS "loan_installment" (
    "id" UUID NOT NULL PRIMARY KEY,
    "installment_number" INT NOT NULL,
    "amount" DECIMAL(10,2) NOT NULL,
    "due_date" DATE NOT NULL,
    "payment_date" DATE,
    "paid" BOOL NOT NULL DEFAULT False,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "loan_id" UUID NOT NULL REFERENCES "loan" ("id") ON DELETE CASCADE
);
        ALTER TABLE "journey_registry" ALTER COLUMN "original_data" TYPE JSONB USING "original_data"::JSONB;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "journey_registry" ALTER COLUMN "original_data" TYPE JSONB USING "original_data"::JSONB;
        DROP TABLE IF EXISTS "loan";
        DROP TABLE IF EXISTS "loan_installment";"""


MODELS_STATE = (
    "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"
)
