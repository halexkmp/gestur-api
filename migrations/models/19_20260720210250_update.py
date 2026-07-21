from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "employee" DROP CONSTRAINT IF EXISTS "fk_employee_user_27cdd818";
        ALTER TABLE "lateness_configuration" ADD "utc_offset_minutes" INT NOT NULL DEFAULT -180;
        ALTER TABLE "employee" ADD CONSTRAINT "fk_employee_user_27cdd818" FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE CASCADE;
        CREATE UNIQUE INDEX IF NOT EXISTS "uid_employee_user_id_f327b9" ON "employee" ("user_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "employee" DROP CONSTRAINT IF EXISTS "employee_user_id_key";
        DROP INDEX IF EXISTS "uid_employee_user_id_f327b9";
        ALTER TABLE "employee" DROP CONSTRAINT IF EXISTS "fk_employee_user_27cdd818";
        ALTER TABLE "lateness_configuration" DROP COLUMN "utc_offset_minutes";
        ALTER TABLE "employee" ADD CONSTRAINT "fk_employee_user_27cdd818" FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE CASCADE;"""


MODELS_STATE = (
    "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"
)
