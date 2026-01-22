from fastapi import APIRouter, Depends
from app.shared.auth import get_current_user
from app.slices.products.list_products.ui.schemas import ProductResponse
from app.slices.products.list_products.application.use_case import list_products
from typing import List

router = APIRouter()

@router.get("", response_model=List[ProductResponse])
async def route(current_user = Depends(get_current_user)):
    return await list_products()
