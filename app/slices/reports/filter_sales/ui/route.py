from typing import List, Optional
from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from app.shared.security.current_user import get_current_user
from app.slices.reports.filter_sales.application.use_case import FilterSales
from app.slices.reports.filter_sales.infra.repository import FilterSalesRepository
from .schemas import SaleReportResponse

router = APIRouter()

use_case = FilterSales(FilterSalesRepository())


@router.get("/sales", response_model=List[SaleReportResponse])
async def route(
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    user_id: Optional[UUID] = Query(default=None),
    product_id: Optional[UUID] = Query(default=None),
    partner_id: Optional[UUID] = Query(default=None),
    current_user=Depends(get_current_user),
):
    return await use_case.execute(
        date_from=date_from,
        date_to=date_to,
        user_id=user_id,
        product_id=product_id,
        partner_id=partner_id,
        current_user_id = current_user.id,
        current_user_role=current_user.role,
    )
