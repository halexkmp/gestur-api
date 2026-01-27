from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "product" DROP COLUMN "has_stock";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "product" ADD "has_stock" BOOL NOT NULL DEFAULT False;"""


MODELS_STATE = (
    "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"
    "AaATNbo="
)
