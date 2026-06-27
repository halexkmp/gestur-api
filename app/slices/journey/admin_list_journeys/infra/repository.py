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
        filters = {'is_deleted':False}
        if user_id:
            filters["user_id"] = user_id
        if start_date:
            filters["timestamp__gte"] = start_date
        if end_date:
            filters["timestamp__lte"] = end_date
        
        return await query.filter(**filters).order_by("-timestamp")
