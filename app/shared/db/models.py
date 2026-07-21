from tortoise import fields, models
from app.shared.db.enums import UserRole, PartnerType, SaleStatus, PaymentMethod, PartnerCustomerShift, ProductType, StockChangeType, LoanStatus, LoanInstallmentStatus

class Role(models.Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharEnumField(UserRole, unique=True)

    class Meta:
        table = "role"

class User(models.Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=255)
    username = fields.CharField(max_length=255, unique=True)
    password_hash = fields.CharField(max_length=255)
    roles: fields.ManyToManyRelation[Role] = fields.ManyToManyField(
        "models.Role", related_name="users", through="user_role"
    )
    active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "user"

class Product(models.Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=255)
    type = fields.CharEnumField(ProductType, default=ProductType.SERVICE)
    default_price = fields.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = fields.IntField(default=0)
    active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "product"

class Partner(models.Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=255)
    pix_key = fields.CharField(max_length=255, null=True)
    type = fields.CharEnumField(PartnerType, default=PartnerType.BUSINESS)
    active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "partner"

class Employee(models.Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=255)
    pix_key = fields.CharField(max_length=255, null=True)
    salary = fields.DecimalField(max_digits=10, decimal_places=2)
    start_date = fields.DateField(auto_now_add=True)
    active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    user = fields.OneToOneField("models.User", related_name="employee", null=True)

    class Meta:
        table = "employee"

class SalaryAdvance(models.Model):
    id = fields.UUIDField(pk=True)
    employee = fields.ForeignKeyField("models.Employee", related_name="salary_advances")
    amount = fields.DecimalField(max_digits=10, decimal_places=2)
    advance_date = fields.DateField()
    created_at = fields.DatetimeField(auto_now_add=True)
    note = fields.TextField(null=True)

    class Meta:
        table = "salary_advance"

class Sale(models.Model):
    id = fields.UUIDField(pk=True)
    sale_code = fields.CharField(max_length=50)
    total_amount = fields.DecimalField(max_digits=10, decimal_places=2)
    partner = fields.ForeignKeyField("models.Partner", related_name="sales", null=True)
    user = fields.ForeignKeyField("models.User", related_name="sales")
    status = fields.CharEnumField(SaleStatus, default=SaleStatus.COMPLETED)
    notes = fields.TextField(null=True)
    observations = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    modified_by = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "sale"

class SaleItem(models.Model):
    id = fields.UUIDField(pk=True)
    sale = fields.ForeignKeyField("models.Sale", related_name="items")
    product = fields.ForeignKeyField("models.Product", related_name="sale_items")
    quantity = fields.IntField()
    unit_price = fields.DecimalField(max_digits=10, decimal_places=2)
    total_price = fields.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        table = "sale_item"

class SalePayment(models.Model):
    id = fields.UUIDField(pk=True)
    sale = fields.ForeignKeyField("models.Sale", related_name="payments")
    payment_method = fields.CharEnumField(PaymentMethod, max_length=255)
    amount = fields.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        table = "sale_payment"

class PartnerCustomer(models.Model):
    id = fields.UUIDField(pk=True)
    partner = fields.ForeignKeyField("models.Partner", related_name="customers", null=True)
    sale = fields.ForeignKeyField("models.Sale", related_name="partner_customer")
    quantity = fields.IntField()
    shift = fields.CharEnumField(PartnerCustomerShift)

    class Meta:
        table = "partner_customer"

class Stock(models.Model):
    id = fields.UUIDField(pk=True)
    change_type = fields.CharEnumField(StockChangeType)
    created_at = fields.DatetimeField(auto_now_add=True)
    product = fields.ForeignKeyField("models.Product", related_name="stock_entries")
    reason = fields.TextField(null=True, default=None, max_length=255)
    quantity_change = fields.IntField()
    sale = fields.ForeignKeyField("models.Sale", related_name="stock_entries", null=True)
    user = fields.ForeignKeyField("models.User", related_name="stock_entries")

    class Meta:
        table = "stock"

class JourneyRegistry(models.Model):
    id = fields.UUIDField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="journeys")
    timestamp = fields.DatetimeField(auto_now_add=True)
    latitude = fields.FloatField()
    longitude = fields.FloatField()
    selfie_id = fields.CharField(max_length=500, null=True)
    is_deleted = fields.BooleanField(default=False)
    edit_reason = fields.TextField(null=True)
    original_data = fields.JSONField(null=True) # To store previous values for auditing

    class Meta:
        table = "journey_registry"

class Loan(models.Model):
    id = fields.UUIDField(pk=True)
    partner = fields.ForeignKeyField("models.Partner", related_name="loans")
    principal_amount = fields.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = fields.DecimalField(max_digits=5, decimal_places=2)
    total_amount = fields.DecimalField(max_digits=10, decimal_places=2)
    installments_qty = fields.IntField()
    start_date = fields.DateField()
    end_date = fields.DateField()
    status = fields.CharEnumField(LoanStatus, default=LoanStatus.ACTIVE)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "loan"

class LoanInstallment(models.Model):
    id = fields.UUIDField(pk=True)
    loan = fields.ForeignKeyField("models.Loan", related_name="installments")
    installment_number = fields.IntField()
    amount = fields.DecimalField(max_digits=10, decimal_places=2)
    due_date = fields.DateField()
    payment_date = fields.DateField(null=True)
    status = fields.CharEnumField(LoanInstallmentStatus, default=LoanInstallmentStatus.PENDING)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "loan_installment"

class LoanInstallmentPayment(models.Model):
    id = fields.UUIDField(pk=True)
    loan_installment = fields.ForeignKeyField("models.LoanInstallment", related_name="payments")
    amount = fields.DecimalField(max_digits=10, decimal_places=2)
    payment_date = fields.DateField()
    notes = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "loan_installment_payment"

class EmployeeSchedule(models.Model):
    id = fields.UUIDField(pk=True)
    employee = fields.OneToOneField("models.Employee", related_name="schedule")
    monday = fields.BooleanField(default=False)
    tuesday = fields.BooleanField(default=False)
    wednesday = fields.BooleanField(default=False)
    thursday = fields.BooleanField(default=False)
    friday = fields.BooleanField(default=False)
    saturday = fields.BooleanField(default=False)
    sunday = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "employee_schedule"

class JustifiedAbsence(models.Model):
    id = fields.UUIDField(pk=True)
    employee = fields.ForeignKeyField("models.Employee", related_name="justified_absences")
    absence_date = fields.DateField()
    reason = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "justified_absence"
        unique_together = (("employee", "absence_date"),)

class LatenessConfiguration(models.Model):
    id = fields.UUIDField(pk=True)
    enabled = fields.BooleanField(default=False)
    expected_entrance_time = fields.TimeField()
    tolerance_minutes = fields.IntField(default=0)
    deduction_interval_minutes = fields.IntField(default=0)
    deduction_value = fields.DecimalField(max_digits=10, decimal_places=2, default=0)
    utc_offset_minutes = fields.IntField(default=-180)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "lateness_configuration"
