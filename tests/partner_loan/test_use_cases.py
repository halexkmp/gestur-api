import pytest
import contextlib
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import date
from decimal import Decimal
from app.shared.db.enums import PartnerType, LoanStatus
from app.slices.partner_loan.create_loan.domain.rules import (
    check_partner_eligibility,
    generate_due_dates,
    get_due_date_for_month
)
from app.slices.partner_loan.create_loan.application.use_case import CreateLoan
from app.slices.partner_loan.get_loan.application.use_case import GetLoan
from app.slices.partner_loan.list_loans.application.use_case import ListLoans
from app.slices.partner_loan.update_loan.application.use_case import UpdateLoan
from app.slices.partner_loan.list_loan_installments.application.use_case import ListLoanInstallments
from app.slices.partner_loan.pay_loan_installment.application.use_case import PayLoanInstallment

def test_due_date_generation_standard():
    start = date(2026, 1, 15)
    due_dates = generate_due_dates(start, 10, 3)
    assert due_dates == [
        date(2026, 2, 10),
        date(2026, 3, 10),
        date(2026, 4, 10),
    ]

def test_due_date_generation_leap_year_february():
    # 2024 is a leap year (February has 29 days)
    start = date(2024, 1, 31)
    due_dates = generate_due_dates(start, 31, 2)
    assert due_dates == [
        date(2024, 2, 29),  # February (last valid day of leap year)
        date(2024, 3, 31),  # March
    ]

def test_due_date_generation_non_leap_year_february():
    # 2026 is not a leap year (February has 28 days)
    start = date(2026, 1, 30)
    due_dates = generate_due_dates(start, 30, 2)
    assert due_dates == [
        date(2026, 2, 28),  # February (last valid day of non-leap year)
        date(2026, 3, 30),  # March
    ]

def test_partner_eligibility_boggyman():
    partner = MagicMock()
    partner.type = PartnerType.BUGGYMAN
    # Should not raise exception
    check_partner_eligibility(partner)

def test_partner_eligibility_business_raises_error():
    partner = MagicMock()
    partner.type = PartnerType.BUSINESS
    with pytest.raises(ValueError, match="Only partners of type BUGGYMAN are eligible for loans"):
        check_partner_eligibility(partner)


import contextlib


@pytest.mark.asyncio
@patch("app.slices.partner_loan.create_loan.application.use_case.Partner.get_or_none")
@patch("app.slices.partner_loan.create_loan.application.use_case.in_transaction")
async def test_create_loan_success(mock_in_transaction, mock_get_partner):
    # 1. Criamos um gerenciador de contexto assíncrono real usando as ferramentas do Python
    @contextlib.asynccontextmanager
    async def mock_in_transaction_cm(*args, **kwargs):
        yield MagicMock()  # Isso simula o bloco dentro do 'async with'

    # 2. Atribuímos o metadado __name__ diretamente na nossa função dublê
    mock_in_transaction_cm.__name__ = "in_transaction"

    # 3. Forçamos o patch do pytest a retornar a nossa função real em vez de um MagicMock genérico
    mock_in_transaction.side_effect = mock_in_transaction_cm

    # --- Configuração do Partner ---
    partner = MagicMock()
    partner.type = PartnerType.BUGGYMAN
    mock_get_partner.side_effect = AsyncMock(return_value=partner)

    # --- Configuração do Repositório ---
    repo = AsyncMock()
    repo.save_loan.side_effect = lambda l: l

    # --- Execução do Caso de Uso ---
    use_case = CreateLoan(repo)
    loan = await use_case.execute(
        partner_id=uuid4(),
        principal_amount=Decimal("1000.00"),
        interest_rate=Decimal("5.00"),
        installments=2,
        due_day=15,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 3, 15),
    )

    # --- Asserts ---
    assert loan.principal_amount == Decimal("1000.00")
    assert loan.interest_rate == Decimal("5.00")
    assert loan.total_amount == Decimal("1050.00")
    assert loan.installments_qty == 2
    assert loan.due_day == 15

    repo.save_loan.assert_called_once()
    repo.save_installments.assert_called_once()

    saved_installments = repo.save_installments.call_args[0][0]
    assert len(saved_installments) == 2
    assert saved_installments[0].installment_number == 1
    assert saved_installments[0].amount == Decimal("525.00")
    assert saved_installments[0].due_date == date(2026, 2, 15)
    assert saved_installments[1].installment_number == 2
    assert saved_installments[1].amount == Decimal("525.00")
    assert saved_installments[1].due_date == date(2026, 3, 15)

@pytest.mark.asyncio
@patch("app.slices.partner_loan.create_loan.application.use_case.Partner.get_or_none")
async def test_create_loan_validation_failures(mock_get_partner):
    partner = MagicMock()
    partner.type = PartnerType.BUGGYMAN
    mock_get_partner.side_effect = AsyncMock(return_value=partner)

    repo = AsyncMock()
    use_case = CreateLoan(repo)
    partner_id = uuid4()

    # Invalid principal amount
    with pytest.raises(ValueError, match="Principal amount must be greater than zero"):
        await use_case.execute(partner_id, Decimal("-10.00"), Decimal("5.00"), 5, 10, date(2026,1,1), date(2026,6,1))

    # Invalid interest rate
    with pytest.raises(ValueError, match="Interest rate cannot be negative"):
        await use_case.execute(partner_id, Decimal("10.00"), Decimal("-1.00"), 5, 10, date(2026,1,1), date(2026,6,1))

    # Invalid end_date before start_date
    with pytest.raises(ValueError, match="End date cannot be before start date"):
        await use_case.execute(partner_id, Decimal("10.00"), Decimal("1.00"), 5, 10, date(2026,2,1), date(2026,1,1))

@pytest.mark.asyncio
async def test_get_loan_success():
    repo = AsyncMock()
    loan = MagicMock()
    repo.get.return_value = loan
    use_case = GetLoan(repo)
    
    loan_id = uuid4()
    result = await use_case.execute(loan_id)
    assert result == loan
    repo.get.assert_called_once_with(loan_id)

@pytest.mark.asyncio
async def test_get_loan_not_found():
    repo = AsyncMock()
    repo.get.return_value = None
    use_case = GetLoan(repo)
    
    with pytest.raises(ValueError, match="Loan not found"):
        await use_case.execute(uuid4())

@pytest.mark.asyncio
async def test_list_loans_success():
    repo = AsyncMock()
    repo.list_all.return_value = ["loan1", "loan2"]
    use_case = ListLoans(repo)
    
    result = await use_case.execute()
    assert result == ["loan1", "loan2"]
    repo.list_all.assert_called_once()

@pytest.mark.asyncio
async def test_update_loan_success():
    repo = AsyncMock()
    loan = MagicMock()
    loan.principal_amount = Decimal("500.00")
    loan.interest_rate = Decimal("3.00")
    loan.total_amount = Decimal("515.00")
    loan.installments_qty = 5
    loan.due_day = 10
    loan.start_date = date(2026, 1, 1)
    loan.end_date = date(2026, 6, 1)
    loan.status = LoanStatus.ACTIVE
    repo.get.return_value = loan
    
    use_case = UpdateLoan(repo)
    updated_loan = await use_case.execute(
        loan_id=uuid4(),
        principal_amount=Decimal("600.00"),
        status=LoanStatus.PAID
    )
    
    # 600.00 * (1 + 3.00 / 100) = 618.00
    assert updated_loan.total_amount == Decimal("618.00")
    assert updated_loan.status == LoanStatus.PAID
    repo.save.assert_called_once_with(loan)

@pytest.mark.asyncio
@patch("app.slices.partner_loan.list_loan_installments.application.use_case.Loan.get_or_none")
async def test_list_loan_installments_success(mock_get_loan):
    loan_mock = MagicMock()
    mock_get_loan.side_effect = AsyncMock(return_value=loan_mock)

    repo = AsyncMock()
    repo.get_by_loan.return_value = ["inst1", "inst2"]
    use_case = ListLoanInstallments(repo)
    
    loan_id = uuid4()
    result = await use_case.execute(loan_id)
    assert result == ["inst1", "inst2"]
    repo.get_by_loan.assert_called_once_with(loan_id)

@pytest.mark.asyncio
async def test_pay_loan_installment_success():
    repo = AsyncMock()
    inst = MagicMock()
    inst.paid = False
    inst.payment_date = None
    repo.get.return_value = inst
    
    use_case = PayLoanInstallment(repo)
    pay_date = date(2026, 5, 20)
    result = await use_case.execute(uuid4(), pay_date)
    
    assert result.paid is True
    assert result.payment_date == pay_date
    repo.save.assert_called_once_with(inst)
