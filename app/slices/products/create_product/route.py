from fastapi import APIRouter, Depends
from app.layers.auth import get_current_user
from app.slices.products.ui.schemas import ProductCreate, ProductResponse
from app.slices.products.create_product.handler import create_product

router = APIRouter()

@router.post("", response_model=ProductResponse, status_code=201)
async def route(product_in: ProductCreate, current_user = Depends(get_current_user)):
    return await create_product(product_in)
