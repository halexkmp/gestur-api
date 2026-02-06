from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

        CREATE TABLE IF NOT EXISTS "role" (
    "id" UUID NOT NULL PRIMARY KEY DEFAULT uuid_generate_v4(),
    "name" VARCHAR(100) NOT NULL UNIQUE
);
COMMENT ON COLUMN "role"."name" IS 'MANAGER: MANAGER\nHUMAN_RESOURCES: HUMAN_RESOURCES\nOPERATOR: OPERATOR';
        CREATE TABLE IF NOT EXISTS "user_role" (
    "role_id" UUID NOT NULL REFERENCES "role" ("id") ON DELETE CASCADE,
    "user_id" UUID NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    UNIQUE ("user_id", "role_id")
);
        -- Seed roles with fixed UUIDs to enable backfill
        INSERT INTO "role" ("name") VALUES
            ('ADMIN')
        ON CONFLICT ("name") DO NOTHING;            
        INSERT INTO "role" ("name") VALUES
            ('MANAGER')
        ON CONFLICT ("name") DO NOTHING;
        INSERT INTO "role" ("name") VALUES
            ('OPERATOR')
        ON CONFLICT ("name") DO NOTHING;
        INSERT INTO "role" ("name") VALUES
            ('HUMAN_RESOURCES')
        ON CONFLICT ("name") DO NOTHING;
        -- Backfill user_role from legacy user.role, mapping ADMIN -> MANAGER
        INSERT INTO "user_role" (user_id, role_id)
        SELECT u.id, r.id
        FROM "user" u
        JOIN "role" r ON r.name = CASE WHEN u.role = 'ADMIN' THEN 'MANAGER' ELSE u.role END
        WHERE u.role IS NOT NULL;
        -- Drop legacy role column
        ALTER TABLE "user" DROP COLUMN IF EXISTS "role";
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- Recreate legacy role column
        ALTER TABLE "user" ADD COLUMN IF NOT EXISTS "role" VARCHAR(20) NOT NULL DEFAULT 'OPERATOR';
        COMMENT ON COLUMN "user"."role" IS 'ADMIN: ADMIN\nOPERATOR: OPERATOR';
        -- Recover a single role from user_role: prefer MANAGER (mapped back to ADMIN), else OPERATOR
        UPDATE "user" u SET role = 'ADMIN'
        WHERE EXISTS (
            SELECT 1 FROM "user_role" ur JOIN "role" r ON r.id = ur.role_id
            WHERE ur.user_id = u.id AND r.name = 'MANAGER'
        );
        UPDATE "user" u SET role = 'OPERATOR'
        WHERE role <> 'ADMIN' AND EXISTS (
            SELECT 1 FROM "user_role" ur JOIN "role" r ON r.id = ur.role_id
            WHERE ur.user_id = u.id AND r.name = 'OPERATOR'
        );
        -- Drop M2M tables
        DROP TABLE IF EXISTS "user_role";
        DROP TABLE IF EXISTS "role";"""


MODELS_STATE = (
    "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"
    "eA43u9MVOSvOBiq9cpcpaXp/8B0VhtpA=="
)
