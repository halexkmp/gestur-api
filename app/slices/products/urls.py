from fastapi import APIRouter
from app.slices.products.create_product.ui.route import router as create_router
from app.slices.products.list_products.ui.route import router as list_router
from app.slices.products.get_product.ui.route import router as get_router
from app.slices.products.update_product.ui.route import router as update_router
from app.slices.products.delete_product.ui.route import router as delete_router
from app.slices.products.update_stock.ui.route import router as update_stock_router

router = APIRouter(prefix="/products", tags=["products"])
router.include_router(create_router)
router.include_router(list_router)
router.include_router(get_router)
router.include_router(update_router)
router.include_router(delete_router)
router.include_router(update_stock_router)
