from fastapi import APIRouter, Depends
from app.shared.security.current_user import get_current_user
from app.slices.sales.list_sales.application.use_case import ListSales
from app.slices.sales.list_sales.infra.repository import ListSalesRepository
from app.slices.sales.list_sales.ui.schemas import SaleResponse
from typing import List

router = APIRouter()

list_sales = ListSales(ListSalesRepository())

@router.get("/", response_model=List[SaleResponse])
async def route(current_user=Depends(get_current_user)):
    return await list_sales.execute()
