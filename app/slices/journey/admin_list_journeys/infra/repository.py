from uuid import UUID
from typing import List, Optional
from app.shared.db.models import JourneyRegistry
from datetime import datetime

class AdminListJourneysRepository:
    async def list_journeys(
        self,
        user_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[JourneyRegistry]:
        query = JourneyRegistry.all()
        if user_id:
            query = query.filter(user_id=user_id)
        if start_date:
            query = query.filter(timestamp__gte=start_date)
        if end_date:
            query = query.filter(timestamp__lte=end_date)
        
        return await query.order_by("-timestamp")
