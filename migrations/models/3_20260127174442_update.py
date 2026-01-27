from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "partner" ADD "pix_key" VARCHAR(255);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "partner" DROP COLUMN "pix_key";"""


MODELS_STATE = (
    "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"
    "l9ATnKbR8C9J7z3+D4Lknh8="
)
