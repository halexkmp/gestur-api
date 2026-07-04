import calendar
from datetime import date,timedelta
from decimal import Decimal
from app.shared.db.enums import PartnerType
from app.shared.db.models import Partner

def calculate_total_amount(principal_amount: Decimal, interest_rate: Decimal) -> Decimal:
    return round(principal_amount * (Decimal('1') + interest_rate / Decimal('100')), 2)

def check_partner_eligibility(partner: Partner):
    if partner.type != PartnerType.BUGGYMAN:
        raise ValueError("Only partners of type BUGGYMAN are eligible for loans")

def generate_due_dates(start_date: date, num_installments: int) -> list[date]:
    return [
        start_date + timedelta(days=7 * i)
        for i in range(1, num_installments + 1)
    ]

def validate_amount_dates(installments_qty, interest_rate, principal_amount, start_date,
                          total_amount):
    if principal_amount <= 0:
        raise ValueError("Principal amount must be greater than zero")
    if interest_rate < 0:
        raise ValueError("Interest rate cannot be negative")
    if total_amount <= 0:
        raise ValueError("Total amount must be greater than zero")
    if installments_qty <= 0:
        raise ValueError("Installments must be greater than zero")