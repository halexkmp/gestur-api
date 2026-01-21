from fastapi import APIRouter
from app.slices.sales.create_sale.route import router as create_router
from app.slices.sales.list_sales.route import router as list_router
from app.slices.sales.get_sale.route import router as get_router

router = APIRouter(prefix="/sales", tags=["sales"])
router.include_router(create_router)
router.include_router(list_router)
router.include_router(get_router)
