from fastapi import APIRouter, Depends
from uuid import UUID
from app.shared.security.current_password import get_current_user
from app.slices.sales.update_sale.application.use_case import UpdateSale
from app.slices.sales.update_sale.infra.repository import UpdateSaleRepository
from app.slices.sales.update_sale.ui.schemas import SaleUpdate
from app.slices.sales.update_sale.ui.schemas import SaleResponse

router = APIRouter()

use_case = UpdateSale(UpdateSaleRepository())

@router.put("/{sale_id}", response_model=SaleResponse)
async def route(
    sale_id: UUID,
    data: SaleUpdate,
    current_user=Depends(get_current_user),
):
    return await use_case.execute(
        sale_id=sale_id,
        partner_id=data.partner_id,
        status=data.status,
        notes=data.notes,
        observations=data.observations,
        items=data.items,
        payments=data.payments,
        modified_by=data.modified_by,
    )
