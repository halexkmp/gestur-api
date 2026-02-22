from datetime import date

from app.shared.db.models import Employee

class CreateEmployeeRepository:
    async def create(
        self,
        name: str,
        pix_key: str | None,
        salary: float,
        active: bool,
        start_date: date
    ):
        return await Employee.create(
            name=name,
            pix_key=pix_key,
            salary=salary,
            active=active,
            start_date=start_date
        )
