from fastapi import APIRouter
from app.slices.reports.filter_sales.ui.route import router as filter_sales_router

router = APIRouter(prefix="/reports", tags=["reports"]) 
router.include_router(filter_sales_router)
