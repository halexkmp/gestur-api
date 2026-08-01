import decimal
from calendar import monthrange
from decimal import Decimal
from uuid import UUID
from typing import List, Optional
from datetime import date
from tortoise.transactions import in_transaction

from app.shared.db.models import SalaryAdvance, Employee
from app.slices.employees.create_salary_advance.infra.repository import CreateSalaryAdvanceRepository
from app.slices.employees.create_salary_advance.domain.rules import (
    ensure_monthly_advances_do_not_exceed_salary,
)


def _add_months(d: date, months: int) -> date:
    # compute year and month roll-over, preserving the original day (clamped to the target month's length)
    m = d.month - 1 + months
    year = d.year + m // 12
    month = m % 12 + 1
    day = min(d.day, monthrange(year, month)[1])
    return date(year, month, day)


class CreateSalaryAdvance:
    def __init__(self, repository: CreateSalaryAdvanceRepository):
        self.repository = repository

    async def execute(
        self,
        employee_id: UUID,
        amount: Decimal,
        advance_date: date,
        times: int,
        note: Optional[str] = None,
    ):
        # Load employee
        employee = await Employee.get_or_none(id=employee_id)
        if not employee:
            raise ValueError("Employee not found")

        start_date = date(advance_date.year, advance_date.month, advance_date.day)

        advances: list[SalaryAdvance] = []

        async with in_transaction():
            new_amount = round(amount/Decimal(times), 2)
            for idx in range(times):
                target_month = _add_months(start_date, idx)
                # Apply domain rule per month
                await ensure_monthly_advances_do_not_exceed_salary(
                    employee=employee,
                    new_amount=new_amount,
                    advance_month=target_month,
                )
                adv = SalaryAdvance(
                    employee=employee,
                    amount=new_amount,
                    advance_date=target_month,
                    note=note,
                )
                advances.append(adv)

            await self.repository.save_many(advances)
