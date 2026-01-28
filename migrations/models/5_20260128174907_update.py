from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "stock" ADD "reason" TEXT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "stock" DROP COLUMN "reason";"""


MODELS_STATE = (
    "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"
    "nLNo+G3Se0//A2s3CjM="
)
