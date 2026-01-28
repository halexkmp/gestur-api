from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "partner_customer" ADD "quantity" INT NOT NULL;
        ALTER TABLE "partner_customer" DROP COLUMN "client_date";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "partner_customer" ADD "client_date" DATE NOT NULL;
        ALTER TABLE "partner_customer" DROP COLUMN "quantity";"""


MODELS_STATE = (
    "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"
)
