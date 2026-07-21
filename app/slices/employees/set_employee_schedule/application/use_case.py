from uuid import UUID
from app.shared.db.models import EmployeeSchedule
from app.slices.employees.set_employee_schedule.infra.repository import SetEmployeeScheduleRepository


class SetEmployeeSchedule:
    def __init__(self, repository: SetEmployeeScheduleRepository):
        self.repository = repository

    async def execute(
        self,
        employee_id: UUID,
        monday: bool,
        tuesday: bool,
        wednesday: bool,
        thursday: bool,
        friday: bool,
        saturday: bool,
        sunday: bool,
    ) -> EmployeeSchedule:
        employee = await self.repository.get_employee(employee_id)
        if not employee:
            raise ValueError("Employee not found")

        return await self.repository.upsert(
            employee_id=employee_id,
            monday=monday,
            tuesday=tuesday,
            wednesday=wednesday,
            thursday=thursday,
            friday=friday,
            saturday=saturday,
            sunday=sunday,
        )
