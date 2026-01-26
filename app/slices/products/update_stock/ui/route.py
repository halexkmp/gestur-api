from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.shared.security.current_password import get_current_user
from app.slices.products.update_stock.application.use_case import UpdateStock
from app.slices.products.update_stock.infra.repository import UpdateStockRepository
from .schemas import UpdateStockRequest, StockResponse

router = APIRouter()

use_case = UpdateStock(UpdateStockRepository())


@router.post("/stock/update", response_model=List[StockResponse], status_code=201)
async def route(data: List[UpdateStockRequest], current_user = Depends(get_current_user)):
    responses: List[StockResponse] = []
    for idx, item in enumerate(data):
        stock = await use_case.execute(
            product_id=item.product_id,
            change_type=item.change_type,
            quantity_change=item.quantity_change,
            sale_id=item.sale_id,
            user_id=current_user.id,
        )
        if not stock:
            raise HTTPException(status_code=404, detail=f"Product or user not found for item at index {idx}")
        responses.append(StockResponse(
            id=stock.id,
            change_type=stock.change_type,
            created_at=stock.created_at,
            product_id=stock.product.id,
            quantity_change=stock.quantity_change,
            sale_id=stock.sale.id,
            user_id=stock.user.id,
        ))
    return responses
