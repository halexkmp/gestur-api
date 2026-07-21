from uuid import UUID
from app.shared.db.models import EmployeeSchedule
from app.slices.employees.get_my_employee_schedule.infra.repository import GetMyEmployeeScheduleRepository


class GetMyEmployeeSchedule:
    def __init__(self, repository: GetMyEmployeeScheduleRepository):
        self.repository = repository

    async def execute(self, employee_id: UUID) -> EmployeeSchedule:
        employee = await self.repository.get_employee(employee_id)
        if not employee:
            raise ValueError("Employee not found")

        schedule = await self.repository.get_schedule(employee_id)
        if not schedule:
            raise ValueError("Schedule not found")

        return schedule
