from fastapi import APIRouter
from app.slices.sales.create_sale.ui.route import router as create_sale
from app.slices.sales.list_sales.ui.route import router as list_sales
from app.slices.sales.get_sale.ui.route import router as get_sale
from app.slices.sales.update_sale.ui.route import router as update_sale

router = APIRouter(prefix="/sales", tags=["sales"]) 
router.include_router(create_sale)
router.include_router(list_sales)
router.include_router(get_sale)
router.include_router(update_sale)
