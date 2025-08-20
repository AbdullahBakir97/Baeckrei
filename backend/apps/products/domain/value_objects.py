from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from datetime import datetime

@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "Euro"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")

@dataclass(frozen=True)
class Weight:
    value: Decimal
    unit: str = "g"

    def to_grams(self) -> Decimal:
        conversions = {
            "g": Decimal("1"),
            "kg": Decimal("1000"),
            "mg": Decimal("0.001"),
            "oz": Decimal("28.3495"),
            "lb": Decimal("453.592")
        }
        return self.value * conversions[self.unit]

@dataclass(frozen=True)
class NutritionValues:
    calories: Decimal
    proteins: Decimal
    carbohydrates: Decimal
    fats: Decimal
    fiber: Optional[Decimal] = None
    weight: Optional[Weight] = None

    def __post_init__(self):
        if any(v < 0 for v in [self.calories, self.proteins, self.carbohydrates, self.fats]):
            raise ValueError("Nutrition values cannot be negative")
        
        if self.fiber is not None and self.fiber < 0:
            raise ValueError("Fiber cannot be negative")

    def per_100g(self) -> 'NutritionValues':
        """Convert nutrition values to per 100g if weight is provided"""
        if not self.weight:
            return self
            
        weight_in_g = self.weight.to_grams()
        factor = Decimal("100") / weight_in_g
        
        return NutritionValues(
            calories=self.calories * factor,
            proteins=self.proteins * factor,
            carbohydrates=self.carbohydrates * factor,
            fats=self.fats * factor,
            fiber=self.fiber * factor if self.fiber else None
        )

@dataclass(frozen=True)
class StockLevel:
    quantity: int
    last_updated: datetime = datetime.now()
    minimum_threshold: Optional[int] = None

    def __post_init__(self):
        if self.quantity < 0:
            raise ValueError("Stock quantity cannot be negative")
        if self.minimum_threshold is not None and self.minimum_threshold < 0:
            raise ValueError("Minimum threshold cannot be negative")

    def is_low(self) -> bool:
        """Check if stock is below minimum threshold"""
        if self.minimum_threshold is None:
            return False
        return self.quantity <= self.minimum_threshold
