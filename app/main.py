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
from app.slices.roles.urls import router as permissions_router
from app.slices.employees.urls import router as employees_router
from app.slices.journey.urls import router as journey_router
from app.slices.partner_loan.urls import router as partner_loan_router


def create_app() -> FastAPI:
    is_production = settings.ENVIRONMENT == "production"
    app = FastAPI(
        title="Gestur API",
        version="1.0.0",
        docs_url=None if is_production else "/docs",
        redoc_url=None if is_production else "/redoc",
        openapi_url=None if is_production else "/openapi.json",
    )

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
    app.include_router(permissions_router)
    app.include_router(employees_router)
    app.include_router(journey_router)
    app.include_router(partner_loan_router)

    # Register Tortoise
    register_tortoise(
        app,
        config=TORTOISE_ORM,
        generate_schemas=settings.GENERATE_SCHEMAS,  # False in production when using migrations
        add_exception_handlers=True,
    )


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
