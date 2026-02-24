from uuid import UUID
from datetime import date
from decimal import Decimal
from app.slices.employees.get_salary_summary.infra.repository import GetSalarySummaryRepository


class GetSalarySummary:
    def __init__(self, repository: GetSalarySummaryRepository):
        self.repository = repository

    async def execute(
        self,
        employee_id: UUID,
        month: int | None = None,
        year: int | None = None,
    ):
        # Default month/year to current when not provided
        today = date.today()
        month = month or today.month
        year = year or today.year

        employee, advances_total = await self.repository.get_employee_and_month_advances(
            employee_id=employee_id,
            month=month,
            year=year,
        )
        # Ensure Decimal math and round to 2 decimal places for money
        salary: Decimal = Decimal(employee.salary)
        advances: Decimal = Decimal(advances_total)
        net = salary - advances
        return {
            "employee_id": employee.id,
            "month": month,
            "year": year,
            "gross_salary": salary,
            "advances_total": advances,
            "net_salary": net,
        }
