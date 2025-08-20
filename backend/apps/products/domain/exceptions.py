from typing import Optional

class DomainException(Exception):
    """Base exception for all domain exceptions"""
    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code
        super().__init__(message)

class InvalidStateTransition(DomainException):
    """Raised when attempting an invalid state transition"""
    def __init__(self, entity: str, current_state: str, attempted_state: str):
        super().__init__(
            f"Cannot transition {entity} from {current_state} to {attempted_state}",
            "INVALID_STATE_TRANSITION"
        )

class BusinessRuleViolation(DomainException):
    """Raised when a business rule is violated"""
    def __init__(self, rule: str, details: Optional[str] = None):
        message = f"Business rule violated: {rule}"
        if details:
            message += f". Details: {details}"
        super().__init__(message, "BUSINESS_RULE_VIOLATION")

class InsufficientStock(DomainException):
    """Raised when attempting to reduce stock below available quantity"""
    def __init__(self, product_id: int, requested: int, available: int):
        super().__init__(
            f"Insufficient stock for product {product_id}. Requested: {requested}, Available: {available}",
            "INSUFFICIENT_STOCK"
        )

class InvalidNutritionValues(DomainException):
    """Raised when nutrition values violate business rules"""
    def __init__(self, details: str):
        super().__init__(
            f"Invalid nutrition values: {details}",
            "INVALID_NUTRITION_VALUES"
        )

class CategoryHierarchyError(DomainException):
    """Raised when category hierarchy rules are violated"""
    def __init__(self, message: str):
        super().__init__(message, "CATEGORY_HIERARCHY_ERROR")
