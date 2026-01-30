from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends

from app.shared.security.current_user import get_current_user
from app.slices.products.list_stock_changes.application.use_case import ListStockChanges
from app.slices.products.list_stock_changes.infra.repository import ListStockChangesRepository
from app.slices.products.list_stock_changes.ui.schemas import StockResponse

router = APIRouter()

use_case = ListStockChanges(ListStockChangesRepository())


@router.get("/stock/changes", response_model=List[StockResponse])
async def route(product_id: Optional[UUID] = None, current_user=Depends(get_current_user)):
    stocks = await use_case.execute(product_id=product_id)
    return [
        StockResponse(
            id=s.id,
            change_type=s.change_type,
            created_at=s.created_at,
            product=s.product,
            quantity_change=s.quantity_change,
            sale=s.sale,
            user=s.user
        )
        for s in stocks
    ]
