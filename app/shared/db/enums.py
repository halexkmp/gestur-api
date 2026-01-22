from enum import Enum

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    OPERATOR = "OPERATOR"

class PartnerType(str, Enum):
    BUGGYMAN = "BUGGYMAN"
    BUSINESS = "BUSINESS"

class SaleStatus(str, Enum):
    COMPLETED = "COMPLETED"
    PENDING = "PENDING"
    CANCELED = "CANCELED"

class PaymentMethod(str, Enum):
    PIX = "PIX"
    CURRENCY = "CURRENCY"
    CREDIT_CARD = "CREDIT_CARD"

class PartnerCustomerShift(str, Enum):
    AFTERNOON = "AFTERNOON"
    MORNING = "MORNING"
