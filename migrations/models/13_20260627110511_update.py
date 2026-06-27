from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "journey_registry" ADD "selfie_id" VARCHAR(500);
        ALTER TABLE "journey_registry" ALTER COLUMN "original_data" TYPE JSONB USING "original_data"::JSONB;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "journey_registry" DROP COLUMN "selfie_id";
        ALTER TABLE "journey_registry" ALTER COLUMN "original_data" TYPE JSONB USING "original_data"::JSONB;"""


MODELS_STATE = (
    "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"
    "8VvuJG"
)
