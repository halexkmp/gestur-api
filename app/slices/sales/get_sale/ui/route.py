from fastapi import APIRouter, Depends
from app.shared.security.current_password import get_current_user
from app.slices.sales.get_sale.ui.schemas import SaleResponse
from app.slices.sales.get_sale.application.use_case import GetSale
from app.slices.sales.get_sale.infra.repository import GetSaleRepository
from uuid import UUID

router = APIRouter()

use_case = GetSale(GetSaleRepository())

@router.get("/{sale_id}", response_model=SaleResponse)
async def route(sale_id: UUID, current_user=Depends(get_current_user)):
    return await use_case.execute(sale_id)
