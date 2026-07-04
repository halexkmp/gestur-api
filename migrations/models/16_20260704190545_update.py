from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "loan_installment_payment" (
    "id" UUID NOT NULL PRIMARY KEY,
    "amount" DECIMAL(10,2) NOT NULL,
    "payment_date" DATE NOT NULL,
    "notes" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "loan_installment_id" UUID NOT NULL REFERENCES "loan_installment" ("id") ON DELETE CASCADE
);
        ALTER TABLE "loan_installment" ADD "status" VARCHAR(14) NOT NULL DEFAULT 'PENDING';
        ALTER TABLE "loan_installment" DROP COLUMN "paid";
        COMMENT ON COLUMN "loan_installment"."status" IS 'PENDING: PENDING\nPARTIALLY_PAID: PARTIALLY_PAID\nPAID: PAID';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "loan_installment" ADD "paid" BOOL NOT NULL DEFAULT False;
        ALTER TABLE "loan_installment" DROP COLUMN "status";
        DROP TABLE IF EXISTS "loan_installment_payment";"""


MODELS_STATE = (
    "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"
)
