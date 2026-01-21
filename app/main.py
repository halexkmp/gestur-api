from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from app.config import settings, TORTOISE_ORM
from app.slices.auth.ui.urls import router as auth_router
from app.slices.users.ui.urls import router as users_router
from app.slices.products.ui.urls import router as products_router
from app.slices.sales.ui.urls import router as sales_router

def create_app() -> FastAPI:
    app = FastAPI(title="Gestur API", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register Routers
    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(products_router)
    # app.include_router(bugueiros_router)
    # app.include_router(partners_router)
    app.include_router(sales_router)
    # app.include_router(stock_router)

    # Register Tortoise
    register_tortoise(
        app,
        config=TORTOISE_ORM,
        generate_schemas=True, # Set to False when using migrations in production
        add_exception_handlers=True,
    )

    return app

app = create_app()

@app.get("/")
async def root():
    return {"message": "Welcome to Gestur API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
