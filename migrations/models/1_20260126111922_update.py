from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "stock" (
    "id" UUID NOT NULL PRIMARY KEY,
    "change_type" VARCHAR(3) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "quantity_change" INT NOT NULL,
    "product_id" UUID NOT NULL REFERENCES "product" ("id") ON DELETE CASCADE,
    "sale_id" UUID REFERENCES "sale" ("id") ON DELETE CASCADE,
    "user_id" UUID NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "stock"."change_type" IS 'IN: IN\nOUT: OUT';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "stock";"""


MODELS_STATE = (
    "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"
    "ZD6ckf5GRsovoTc449Hwz0nvPfwPrm6icQ=="
)
