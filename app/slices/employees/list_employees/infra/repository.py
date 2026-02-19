from typing import Optional
from app.shared.db.models import Employee

class ListEmployeesRepository:
    async def list(self, active: Optional[bool] = None):
        qs = Employee.all().order_by("name")
        if active is not None:
            qs = qs.filter(active=active)
        return await qs
