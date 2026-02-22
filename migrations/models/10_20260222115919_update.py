from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "employee" ADD "start_date" DATE NOT NULL DEFAULT CURRENT_DATE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "employee" DROP COLUMN "start_date";"""


MODELS_STATE = (
    "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"
)
