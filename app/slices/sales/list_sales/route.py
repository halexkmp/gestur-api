from fastapi import APIRouter, Depends
from app.layers.auth import get_current_user
from app.slices.sales.ui.schemas import SaleResponse
from app.slices.sales.list_sales.handler import list_sales
from typing import List

router = APIRouter()

@router.get("", response_model=List[SaleResponse])
async def route(current_user = Depends(get_current_user)):
    return await list_sales()
