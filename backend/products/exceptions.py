"""
Product Management System Exceptions

This module contains all custom exceptions used throughout the product management system.
Each exception is carefully documented and includes relevant attributes for detailed error reporting.
"""

class ProductError(Exception):
    """Base class for all product-related exceptions."""
    def __init__(self, message=None, code=None):
        self.message = message or "An unspecified product management error occurred."
        self.code = code or "PRODUCT_ERROR"
        super().__init__(self.message)

    def __repr__(self):
        return f"{self.__class__.__name__}(message={self.message!r}, code={self.code!r})"

# Product Exceptions
class ProductNotFoundError(ProductError):
    """Raised when a product is not found by the specified identifier."""
    def __init__(self, product_id=None, message=None):
        self.product_id = product_id
        self.message = message or f"Product with ID '{product_id}' could not be found in the system."
        self.code = "PRODUCT_NOT_FOUND"
        super().__init__(self.message, self.code)

    def __repr__(self):
        return f"{self.__class__.__name__}(product_id={self.product_id!r}, message={self.message!r})"

class DuplicateProductError(ProductError):
    """Raised when attempting to create a product that already exists."""
    def __init__(self, name=None, sku=None, message=None):
        self.name = name
        self.sku = sku
        self.message = message or f"Product with name '{name}' or SKU '{sku}' already exists."
        self.code = "DUPLICATE_PRODUCT"
        super().__init__(self.message, self.code)

class InsufficientStockError(ProductError):
    """Raised when there isn't enough stock for a requested product quantity."""
    def __init__(self, product_id=None, required_quantity=None, available_stock=None, message=None):
        self.product_id = product_id
        self.required_quantity = required_quantity
        self.available_stock = available_stock
        self.message = message or (
            f"Insufficient stock for product '{product_id}': "
            f"Requested {required_quantity} units, but only {available_stock} available."
        )
        self.code = "INSUFFICIENT_STOCK"
        super().__init__(self.message, self.code)

class NegativeStockError(ProductError):
    """Raised when an operation would result in negative stock."""
    def __init__(self, product_id=None, current_stock=None, adjustment=None, message=None):
        self.product_id = product_id
        self.current_stock = current_stock
        self.adjustment = adjustment
        self.message = message or (
            f"Cannot adjust stock for product '{product_id}': "
            f"Current stock {current_stock}, adjustment {adjustment} would result in negative stock."
        )
        self.code = "NEGATIVE_STOCK"
        super().__init__(self.message, self.code)

class PricingError(ProductError):
    """Raised when there are pricing-related issues."""
    def __init__(self, product_id=None, price=None, message=None, code=None):
        self.product_id = product_id
        self.price = price
        self.message = message or f"Invalid price '{price}' for product '{product_id}'. Price must be greater than 0."
        self.code = code or "INVALID_PRICE"
        super().__init__(self.message, self.code)

class NegativePriceError(PricingError):
    """Raised when attempting to set a negative price."""
    def __init__(self, product_id=None, price=None):
        super().__init__(
            product_id=product_id,
            price=price,
            message=f"Cannot set negative price '{price}' for product '{product_id}'.",
            code="NEGATIVE_PRICE"
        )

# Category Exceptions
class CategoryError(ProductError):
    """Base class for all category-related exceptions."""
    def __init__(self, message=None, code=None):
        self.message = message or "An unspecified category error occurred."
        self.code = code or "CATEGORY_ERROR"
        super().__init__(self.message, self.code)

class CategoryNotFoundError(CategoryError):
    """Raised when a category is not found by the specified identifier."""
    def __init__(self, category_id=None, message=None):
        self.category_id = category_id
        self.message = message or f"Category with ID '{category_id}' could not be found in the system."
        self.code = "CATEGORY_NOT_FOUND"
        super().__init__(self.message, self.code)

class DuplicateCategoryError(CategoryError):
    """Raised when attempting to create a category that already exists."""
    def __init__(self, name=None, message=None):
        self.name = name
        self.message = message or f"Category with name '{name}' already exists."
        self.code = "DUPLICATE_CATEGORY"
        super().__init__(self.message, self.code)

class CategoryInUseError(CategoryError):
    """Raised when attempting to delete a category that contains products."""
    def __init__(self, category_id=None, product_count=None, message=None):
        self.category_id = category_id
        self.product_count = product_count
        self.message = message or (
            f"Cannot delete category '{category_id}': "
            f"It contains {product_count} products. Please reassign or delete the products first."
        )
        self.code = "CATEGORY_IN_USE"
        super().__init__(self.message, self.code)

# Ingredient Exceptions
class IngredientError(ProductError):
    """Base class for all ingredient-related exceptions."""
    def __init__(self, message=None, code=None):
        self.message = message or "An unspecified ingredient error occurred."
        self.code = code or "INGREDIENT_ERROR"
        super().__init__(self.message, self.code)

class IngredientNotFoundError(IngredientError):
    """Raised when an ingredient is not found by the specified identifier."""
    def __init__(self, ingredient_id=None, message=None):
        self.ingredient_id = ingredient_id
        self.message = message or f"Ingredient with ID '{ingredient_id}' could not be found in the system."
        self.code = "INGREDIENT_NOT_FOUND"
        super().__init__(self.message, self.code)

class DuplicateIngredientError(IngredientError):
    """Raised when attempting to create an ingredient that already exists."""
    def __init__(self, name=None, message=None):
        self.name = name
        self.message = message or f"Ingredient with name '{name}' already exists."
        self.code = "DUPLICATE_INGREDIENT"
        super().__init__(self.message, self.code)

class IngredientInUseError(IngredientError):
    """Raised when attempting to delete an ingredient that is used in products."""
    def __init__(self, ingredient_id=None, product_count=None, message=None):
        self.ingredient_id = ingredient_id
        self.product_count = product_count
        self.message = message or (
            f"Cannot delete ingredient '{ingredient_id}': "
            f"It is used in {product_count} products. Please remove it from products first."
        )
        self.code = "INGREDIENT_IN_USE"
        super().__init__(self.message, self.code)

# Allergen Exceptions
class AllergenError(ProductError):
    """Base class for all allergen-related exceptions."""
    def __init__(self, message=None, code=None):
        self.message = message or "An unspecified allergen error occurred."
        self.code = code or "ALLERGEN_ERROR"
        super().__init__(self.message, self.code)

class AllergenNotFoundError(AllergenError):
    """Raised when an allergen is not found by the specified identifier."""
    def __init__(self, allergen_id=None, message=None):
        self.allergen_id = allergen_id
        self.message = message or f"Allergen with ID '{allergen_id}' could not be found in the system."
        self.code = "ALLERGEN_NOT_FOUND"
        super().__init__(self.message, self.code)

class DuplicateAllergenError(AllergenError):
    """Raised when attempting to create an allergen that already exists."""
    def __init__(self, name=None, message=None):
        self.name = name
        self.message = message or f"Allergen with name '{name}' already exists."
        self.code = "DUPLICATE_ALLERGEN"
        super().__init__(self.message, self.code)

class AllergenInUseError(AllergenError):
    """Raised when attempting to delete an allergen that is used in ingredients."""
    def __init__(self, allergen_id=None, ingredient_count=None, message=None):
        self.allergen_id = allergen_id
        self.ingredient_count = ingredient_count
        self.message = message or (
            f"Cannot delete allergen '{allergen_id}': "
            f"It is used in {ingredient_count} ingredients. Please remove it from ingredients first."
        )
        self.code = "ALLERGEN_IN_USE"
        super().__init__(self.message, self.code)

# Nutrition Exceptions
class NutritionError(ProductError):
    """Base exception for nutrition-related errors."""
    def __init__(self, message=None, code=None):
        self.message = message or "An unspecified nutrition error occurred."
        self.code = code or "NUTRITION_ERROR"
        super().__init__(self.message, self.code)

class NutritionNotFoundError(NutritionError):
    """Exception raised when nutrition information is not found."""
    def __init__(self, nutrition_id=None, message=None):
        self.nutrition_id = nutrition_id
        self.message = message or f"Nutrition information with ID '{nutrition_id}' not found"
        self.code = "NUTRITION_NOT_FOUND"
        super().__init__(self.message, self.code)

class NutritionValidationError(NutritionError):
    """Exception raised when nutrition data validation fails."""
    def __init__(self, field=None, value=None, reason=None, message=None):
        self.field = field
        self.value = value
        self.reason = reason
        self.message = message or f"Invalid nutrition data for field '{field}': {reason}"
        self.code = "NUTRITION_VALIDATION_ERROR"
        super().__init__(self.message, self.code)

# Validation Exceptions
class ValidationError(ProductError):
    """Raised when data validation fails."""
    def __init__(self, field=None, value=None, reason=None, message=None, code=None):
        self.field = field
        self.value = value
        self.reason = reason
        self.message = message or f"Validation failed for field '{field}': {reason}"
        self.code = code or "VALIDATION_ERROR"
        super().__init__(self.message, self.code)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"field={self.field!r}, "
            f"value={self.value!r}, "
            f"reason={self.reason!r}, "
            f"message={self.message!r}, "
            f"code={self.code!r})"
        )

# Create a module-like object to hold all exceptions
class _Exceptions:
    # Base
    ProductError = ProductError
    
    # Product
    ProductNotFoundError = ProductNotFoundError
    DuplicateProductError = DuplicateProductError
    InsufficientStockError = InsufficientStockError
    NegativeStockError = NegativeStockError
    PricingError = PricingError
    NegativePriceError = NegativePriceError
    
    # Category
    CategoryError = CategoryError
    CategoryNotFoundError = CategoryNotFoundError
    DuplicateCategoryError = DuplicateCategoryError
    CategoryInUseError = CategoryInUseError
    
    # Ingredient
    IngredientError = IngredientError
    IngredientNotFoundError = IngredientNotFoundError
    DuplicateIngredientError = DuplicateIngredientError
    IngredientInUseError = IngredientInUseError
    
    # Allergen
    AllergenError = AllergenError
    AllergenNotFoundError = AllergenNotFoundError
    DuplicateAllergenError = DuplicateAllergenError
    AllergenInUseError = AllergenInUseError
    
    # Nutrition
    NutritionError = NutritionError
    NutritionNotFoundError = NutritionNotFoundError
    NutritionValidationError = NutritionValidationError
    
    # Validation
    ValidationError = ValidationError

# Create a singleton instance
EXCEPTIONS = _Exceptions()
