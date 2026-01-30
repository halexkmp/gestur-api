from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" ADD "active" BOOL NOT NULL DEFAULT True;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" DROP COLUMN "active";"""


MODELS_STATE = (
    "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"
    "v4Q0cM461NhmsPTpf46YdBk="
)
