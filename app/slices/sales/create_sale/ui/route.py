from fastapi import APIRouter, Depends
from app.shared.security.current_user import get_current_user
from app.slices.sales.create_sale.ui.schemas import SaleCreate
from app.slices.sales.list_sales.ui.schemas import SaleResponse
from app.slices.sales.create_sale.application.use_case import CreateSale
from app.slices.sales.create_sale.infra.repository import CreateSaleRepository

router = APIRouter()

use_case = CreateSale(CreateSaleRepository())

@router.post("/", response_model=SaleResponse, status_code=201)
async def route(sale_in: SaleCreate, current_user = Depends(get_current_user)):
    return await use_case.execute(
        user_id=current_user.id,
        partner_id=sale_in.partner_id,
        items=[{
            "product_id": i.product_id,
            "quantity": i.quantity,
            "unit_price": i.unit_price,
        } for i in sale_in.items],
        payments=[{
            "payment_method": p.payment_method,
            "amount": p.amount,
        } for p in sale_in.payments],
        notes=sale_in.notes,
        observations=sale_in.observations,
        partner_customer_shift=sale_in.partner_customer_shift,
        partner_customer_quantity=sale_in.partner_customer_quantity
    )
