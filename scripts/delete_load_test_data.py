"""Delete the synthetic data created by seed_load_test_data.py.

Scoped strictly to users tagged "load_employee_001".."load_employee_100"
(and their dependent employee/schedule/salary_advance/justified_absence/
journey_registry rows). Does not touch roles or the lateness_configuration
row, since those are shared/global and not created by the seed script
unless previously absent.

Usage:
    uv run python scripts/delete_load_test_data.py
"""

import asyncio

from tortoise import Tortoise
from tortoise.transactions import in_transaction

from app.config import TORTOISE_ORM
from app.shared.db.models import (
    Employee,
    EmployeeSchedule,
    JourneyRegistry,
    JustifiedAbsence,
    SalaryAdvance,
    User,
)

USERNAME_PREFIX = "load_employee_"


async def run() -> None:
    await Tortoise.init(config=TORTOISE_ORM)
    try:
        async with in_transaction():
            users = await User.filter(username__startswith=USERNAME_PREFIX)
            user_ids = [u.id for u in users]
            employees = await Employee.filter(user_id__in=user_ids)
            employee_ids = [e.id for e in employees]

            journeys_deleted = await JourneyRegistry.filter(user_id__in=user_ids).delete()
            advances_deleted = await SalaryAdvance.filter(employee_id__in=employee_ids).delete()
            absences_deleted = await JustifiedAbsence.filter(employee_id__in=employee_ids).delete()
            schedules_deleted = await EmployeeSchedule.filter(employee_id__in=employee_ids).delete()
            employees_deleted = await Employee.filter(id__in=employee_ids).delete()

            for user in users:
                await user.roles.clear()
            users_deleted = await User.filter(id__in=user_ids).delete()

        print(f"Deleted {users_deleted} users, {employees_deleted} employees, "
              f"{schedules_deleted} schedules, {advances_deleted} salary advances, "
              f"{absences_deleted} justified absences, {journeys_deleted} journey registries.")
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(run())
