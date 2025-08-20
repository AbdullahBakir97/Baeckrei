"""Custom exceptions for cart operations."""
from apps.core.exceptions import VersionConflictError, VersionLockTimeoutError

class CartError(Exception):
    """Base exception for all cart-related errors."""
    pass

class CartException(CartError):
    """Base exception for cart operations."""
    pass

class VersionConflict(VersionConflictError, CartException):
    """Cart-specific version conflict that maintains compatibility."""
    pass

class VersionLockTimeout(VersionLockTimeoutError, CartException):
    """Cart-specific lock timeout that maintains compatibility."""
    pass

class CartNotFoundError(CartException):
    """Exception raised when cart is not found."""
    def __init__(self, message="Cart not found"):
        self.message = message
        super().__init__(self.message)

class InvalidQuantityError(CartException):
    """Exception raised when quantity is invalid."""
    def __init__(self, quantity: int):
        self.quantity = quantity
        super().__init__(f"Invalid quantity: {quantity}. Quantity must be greater than 0.")

class InsufficientStockError(CartException):
    """Raised when attempting to add more items than available in stock."""
    def __init__(self, message: str, available_stock: int = None):
        self.available_stock = available_stock
        super().__init__(message)

class CartAlreadyCheckedOutError(CartException):
    """Raised when attempting to modify a cart that has been checked out."""
    def __init__(self, message="Cart has already been checked out"):
        self.message = message
        super().__init__(self.message)

class EmptyCartError(CartException):
    """Raised when attempting to checkout an empty cart."""
    def __init__(self):
        super().__init__("Cannot checkout an empty cart.")

class InvalidCouponError(CartException):
    """Raised when an invalid coupon is applied."""
    def __init__(self, coupon_code: str):
        self.coupon_code = coupon_code
        super().__init__(f"Invalid coupon code: {coupon_code}")

class CouponAlreadyAppliedError(CartException):
    """Raised when attempting to apply a coupon that's already applied."""
    def __init__(self, coupon_code: str):
        self.coupon_code = coupon_code
        super().__init__(f"Coupon {coupon_code} has already been applied to this cart.")

class CartLockedException(CartException):
    """Raised when attempting to modify a locked cart."""
    pass

class StockNotAvailableError(CartException):
    """Raised when attempting to add items that exceed available stock."""
    def __init__(self, message: str, available_stock: int = None):
        self.available_stock = available_stock
        super().__init__(message)

class InvalidCartOperationError(CartException):
    """Raised when an invalid operation is attempted on a cart."""
    pass

class CartValidationError(CartException):
    """Raised when cart validation fails."""
    pass
