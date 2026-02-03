from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "sale_payment" ALTER COLUMN "payment_method" TYPE VARCHAR(255) USING "payment_method"::VARCHAR(255);
        COMMENT ON COLUMN "sale_payment"."payment_method" IS 'PIX: PIX
CURRENCY: CURRENCY
CREDIT_CARD: CREDIT_CARD
BUSINESS_PARTNER: BUSINESS_PARTNER';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        COMMENT ON COLUMN "sale_payment"."payment_method" IS 'PIX: PIX
CURRENCY: CURRENCY
CREDIT_CARD: CREDIT_CARD';
        ALTER TABLE "sale_payment" ALTER COLUMN "payment_method" TYPE VARCHAR(11) USING "payment_method"::VARCHAR(11);"""


MODELS_STATE = (
    "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"
    "PJ9N+CWkgQvWocY2ydKn/wHANn+5"
)
