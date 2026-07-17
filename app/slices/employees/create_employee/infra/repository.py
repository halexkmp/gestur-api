from datetime import date
from uuid import UUID

from app.shared.db.models import Employee

class CreateEmployeeRepository:
    async def create(
        self,
        name: str,
        pix_key: str | None,
        salary: float,
        active: bool,
        start_date: date,
        user_id: UUID | None = None
    ):
        return await Employee.create(
            name=name,
            pix_key=pix_key,
            salary=salary,
            active=active,
            start_date=start_date,
            user_id=user_id
        )
