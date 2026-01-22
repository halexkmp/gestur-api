from fastapi import APIRouter
from app.slices.partners.create_partner.ui.route import router as create_partner

router = APIRouter(prefix="/partners", tags=["partners"])
router.include_router(create_partner)
