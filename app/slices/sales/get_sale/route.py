from fastapi import APIRouter, Depends
from app.layers.auth import get_current_user
from app.slices.sales.ui.schemas import SaleResponse
from app.slices.sales.get_sale.handler import get_sale
from uuid import UUID

router = APIRouter()

@router.get("/{sale_id}", response_model=SaleResponse)
async def route(sale_id: UUID, current_user = Depends(get_current_user)):
    return await get_sale(sale_id)
