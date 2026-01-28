from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from app.shared.security.current_password import get_current_user
from app.slices.reports.get_partner_customers_by_sales.application.use_case import (
    GetPartnerCustomersBySales,
)
from app.slices.reports.get_partner_customers_by_sales.infra.repository import (
    GetPartnerCustomersBySalesRepository,
)
from .schemas import PartnerCustomerReport

router = APIRouter()

use_case = GetPartnerCustomersBySales(GetPartnerCustomersBySalesRepository())


@router.post("/partner-customers", response_model=List[PartnerCustomerReport])
async def route(sale_ids: List[UUID],current_user=Depends(get_current_user),
):
    return await use_case.execute(sale_ids=sale_ids)
