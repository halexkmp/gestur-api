from enum import Enum

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    HUMAN_RESOURCES = "HUMAN_RESOURCES"
    OPERATOR = "OPERATOR"
    EMPLOYEE = "EMPLOYEE"

class PartnerType(str, Enum):
    BUGGYMAN = "BUGGYMAN"
    BUSINESS = "BUSINESS"

class ProductType(str, Enum):
    SERVICE = "SERVICE"
    CONSUMABLE = "CONSUMABLE"

class SaleStatus(str, Enum):
    COMPLETED = "COMPLETED"
    PENDING = "PENDING"
    CANCELED = "CANCELED"

class PaymentMethod(str, Enum):
    PIX = "PIX"
    CURRENCY = "CURRENCY"
    CREDIT_CARD = "CREDIT_CARD"
    BUSINESS_PARTNER = "BUSINESS_PARTNER"

class PartnerCustomerShift(str, Enum):
    AFTERNOON = "AFTERNOON"
    MORNING = "MORNING"

class StockChangeType(str, Enum):
    IN = "IN"
    OUT = "OUT"
