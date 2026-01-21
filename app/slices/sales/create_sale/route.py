from fastapi import APIRouter, Depends
from app.layers.auth import get_current_user
from app.slices.sales.ui.schemas import SaleCreate, SaleResponse
from app.slices.sales.create_sale.handler import create_sale

router = APIRouter()

@router.post("", response_model=SaleResponse, status_code=201)
async def route(sale_in: SaleCreate, current_user = Depends(get_current_user)):
    return await create_sale(sale_in, current_user.id)
