from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from app.config import TORTOISE_ORM, settings
from app.slices.auth.urls import router as auth_router
from app.slices.users.urls import router as users_router
from app.slices.products.urls import router as products_router
from app.slices.sales.urls import router as sales_router
from app.slices.partners.urls import router as partners_router
from app.slices.reports.urls import router as reports_router


def create_app() -> FastAPI:
    app = FastAPI(title="Gestur API", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register Routers
    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(products_router)
    app.include_router(partners_router)
    app.include_router(sales_router)
    app.include_router(reports_router)

    # Register Tortoise
    register_tortoise(
        app,
        config=TORTOISE_ORM,
        generate_schemas=settings.GENERATE_SCHEMAS,  # False in production when using migrations
        add_exception_handlers=True,
    )

    # Optionally run Aerich migrations on startup
    @app.on_event("startup")
    async def run_migrations_on_startup():
        if not settings.RUN_MIGRATIONS_ON_STARTUP:
            return
        try:
            import sys
            import asyncio

            # Run `python -m aerich upgrade` to avoid conflicts with Tortoise init
            proc = await asyncio.create_subprocess_exec(
                sys.executable,
                "-m",
                "aerich",
                "upgrade",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode != 0:
                raise RuntimeError(
                    f"aerich upgrade failed with code {proc.returncode}: {stderr.decode().strip()}"
                )
            out = stdout.decode().strip()
            if out:
                print(out)
            print("Aerich migrations applied on startup.")
        except Exception as e:
            # Fail fast so the deployment doesn't run with an out-of-date schema
            print(f"Failed to run Aerich migrations on startup: {e}")
            raise

    return app


app = create_app()


@app.get("/")
async def root():
    return {"message": "Welcome to Gestur API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG
    )
