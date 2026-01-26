from fastapi import APIRouter
from app.slices.partners.create_partner.ui.route import router as create_partner
from app.slices.partners.update_partner.ui.route import router as update_partner
from app.slices.partners.delete_partner.ui.route import router as delete_partner
from app.slices.partners.list_partners.ui.route import router as list_partners
from app.slices.partners.get_partner.ui.route import router as get_partner
from app.slices.partners.list_partners_by_type.ui.route import router as list_partners_by_type

router = APIRouter(prefix="/partners", tags=["partners"]) 
router.include_router(create_partner)
router.include_router(update_partner)
router.include_router(delete_partner)
router.include_router(list_partners)
router.include_router(get_partner)
router.include_router(list_partners_by_type)