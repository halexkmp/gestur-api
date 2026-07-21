from uuid import UUID
from typing import Optional

from app.shared.db.models import Employee, EmployeeSchedule


class SetEmployeeScheduleRepository:
    async def get_employee(self, employee_id: UUID) -> Optional[Employee]:
        return await Employee.get_or_none(id=employee_id)

    async def upsert(
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
        schedule = await EmployeeSchedule.get_or_none(employee_id=employee_id)
        if not schedule:
            return await EmployeeSchedule.create(
                employee_id=employee_id,
                monday=monday,
                tuesday=tuesday,
                wednesday=wednesday,
                thursday=thursday,
                friday=friday,
                saturday=saturday,
                sunday=sunday,
            )

        schedule.monday = monday
        schedule.tuesday = tuesday
        schedule.wednesday = wednesday
        schedule.thursday = thursday
        schedule.friday = friday
        schedule.saturday = saturday
        schedule.sunday = sunday
        await schedule.save()
        return schedule
