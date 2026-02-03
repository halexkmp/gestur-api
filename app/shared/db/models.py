from tortoise import fields, models
from app.shared.db.enums import UserRole, PartnerType, SaleStatus, PaymentMethod, PartnerCustomerShift, ProductType, StockChangeType

class User(models.Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=255)
    username = fields.CharField(max_length=255, unique=True)
    password_hash = fields.CharField(max_length=255)
    role = fields.CharEnumField(UserRole)
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
