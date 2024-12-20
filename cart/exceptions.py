class CartException(Exception):
    """Base exception for cart-related errors."""
    pass

class CartNotFoundError(CartException):
    """Raised when a cart is not found."""
    def __init__(self, cart_id: int):
        self.cart_id = cart_id
        super().__init__(f"Cart with ID {cart_id} not found.")

class InvalidQuantityError(CartException):
    """Raised when an invalid quantity is provided."""
    def __init__(self, quantity: int):
        self.quantity = quantity
        super().__init__(f"Invalid quantity: {quantity}. Quantity must be greater than 0.")

class InsufficientStockError(CartException):
    """Raised when there is not enough stock for a product."""
    def __init__(self, item: str, required_quantity: int, available_stock: int):
        self.item = item
        self.required_quantity = required_quantity
        self.available_stock = available_stock
        super().__init__(
            f"Insufficient stock for {item}. "
            f"Required: {required_quantity}, Available: {available_stock}"
        )

class CartAlreadyCheckedOutError(CartException):
    """Raised when attempting to modify a cart that has been checked out."""
    pass

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
