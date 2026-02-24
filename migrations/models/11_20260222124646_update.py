from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "salary_advance" ADD "advance_date" DATE NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "salary_advance" DROP COLUMN "advance_date";"""


MODELS_STATE = (
    "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"
)
