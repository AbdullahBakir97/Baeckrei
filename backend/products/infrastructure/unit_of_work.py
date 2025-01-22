from abc import ABC, abstractmethod
from django.db import transaction
from typing import Optional

from .repositories import (
    DjangoProductRepository,
    DjangoCategoryRepository,
    DjangoIngredientRepository,
    DjangoAllergenRepository
)

class IUnitOfWork(ABC):
    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass

class DjangoUnitOfWork(IUnitOfWork):
    def __init__(self):
        self.products: Optional[DjangoProductRepository] = None
        self.categories: Optional[DjangoCategoryRepository] = None
        self.ingredients: Optional[DjangoIngredientRepository] = None
        self.allergens: Optional[DjangoAllergenRepository] = None

    def __enter__(self):
        self.products = DjangoProductRepository()
        self.categories = DjangoCategoryRepository()
        self.ingredients = DjangoIngredientRepository()
        self.allergens = DjangoAllergenRepository()
        self.transaction = transaction.atomic()
        self.transaction.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        self.transaction.__exit__(exc_type, exc_val, exc_tb)

    def commit(self):
        self.transaction.commit()

    def rollback(self):
        self.transaction.rollback()
