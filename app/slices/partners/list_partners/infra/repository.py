from typing import List
from app.shared.db.models import Partner

class ListPartnersRepository:
    async def list(self) -> List[Partner]:
        return await Partner.all()
