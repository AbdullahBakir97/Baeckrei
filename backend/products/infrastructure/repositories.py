from typing import List, Optional, Dict, Any
from django.db.models import QuerySet, Q
from django.core.exceptions import ObjectDoesNotExist

from ..domain.repositories import (
    IProductRepository, ICategoryRepository,
    IIngredientRepository, IAllergenRepository
)
from ..models import Product, Category, Ingredient, AllergenInfo, NutritionInfo
from ..domain.value_objects import Money, Weight, NutritionValues, StockLevel
from ..domain.exceptions import DomainException

class DjangoProductRepository(IProductRepository):
    def get(self, id: int) -> Optional[Product]:
        try:
            return Product.objects.get(id=id)
        except ObjectDoesNotExist:
            return None

    def list(self, **filters) -> QuerySet:
        return Product.objects.filter(**filters)

    def create(self, data: Dict) -> Product:
        return Product.objects.create(**data)

    def update(self, id: int, data: Dict) -> Optional[Product]:
        try:
            product = Product.objects.get(id=id)
            for key, value in data.items():
                setattr(product, key, value)
            product.save()
            return product
        except ObjectDoesNotExist:
            return None

    def delete(self, id: int) -> None:
        Product.objects.filter(id=id).delete()

    def get_by_slug(self, slug: str) -> Optional[Product]:
        try:
            return Product.objects.get(slug=slug)
        except ObjectDoesNotExist:
            return None

    def get_with_relations(self, id: int) -> Optional[Product]:
        try:
            return Product.objects.select_related(
                'category',
                'nutrition_info'
            ).prefetch_related(
                'ingredients',
                'allergens'
            ).get(id=id)
        except ObjectDoesNotExist:
            return None

    def find_similar_nutrition(self, nutrition: NutritionValues, limit: int) -> List[Product]:
        # Implement similarity search based on nutrition values
        base_qs = Product.objects.select_related('nutrition_info')
        
        # Calculate similarity based on nutrition values
        similar_products = []
        for product in base_qs:
            if not product.nutrition_info:
                continue
            
            # Simple similarity score based on nutritional differences
            score = abs(product.nutrition_info.calories - nutrition.calories)
            score += abs(product.nutrition_info.proteins - nutrition.proteins)
            score += abs(product.nutrition_info.carbohydrates - nutrition.carbohydrates)
            score += abs(product.nutrition_info.fats - nutrition.fats)
            
            similar_products.append((score, product))
        
        # Sort by similarity score and return top matches
        similar_products.sort(key=lambda x: x[0])
        return [product for score, product in similar_products[:limit]]

    def update_stock(self, id: int, stock_level: StockLevel) -> Product:
        try:
            product = Product.objects.get(id=id)
            product.stock_quantity = stock_level.quantity
            product.save()
            return product
        except ObjectDoesNotExist:
            raise DomainException("Product not found", "PRODUCT_NOT_FOUND")

class DjangoCategoryRepository(ICategoryRepository):
    def get(self, id: int) -> Optional[Category]:
        try:
            return Category.objects.get(id=id)
        except ObjectDoesNotExist:
            return None

    def list(self, **filters) -> QuerySet:
        return Category.objects.filter(**filters)

    def create(self, data: Dict) -> Category:
        return Category.objects.create(**data)

    def update(self, id: int, data: Dict) -> Optional[Category]:
        try:
            category = Category.objects.get(id=id)
            for key, value in data.items():
                setattr(category, key, value)
            category.save()
            return category
        except ObjectDoesNotExist:
            return None

    def delete(self, id: int) -> None:
        Category.objects.filter(id=id).delete()

    def get_active(self) -> QuerySet:
        return Category.objects.filter(is_active=True)

    def get_by_slug(self, slug: str) -> Optional[Category]:
        try:
            return Category.objects.get(slug=slug)
        except ObjectDoesNotExist:
            return None

    def update_order(self, id: int, new_order: int) -> Category:
        try:
            category = Category.objects.get(id=id)
            category.order = new_order
            category.save()
            return category
        except ObjectDoesNotExist:
            raise DomainException("Category not found", "CATEGORY_NOT_FOUND")

class DjangoIngredientRepository(IIngredientRepository):
    def get(self, id: int) -> Optional[Ingredient]:
        try:
            return Ingredient.objects.get(id=id)
        except ObjectDoesNotExist:
            return None

    def list(self, **filters) -> QuerySet:
        return Ingredient.objects.filter(**filters)

    def create(self, data: Dict) -> Ingredient:
        return Ingredient.objects.create(**data)

    def update(self, id: int, data: Dict) -> Optional[Ingredient]:
        try:
            ingredient = Ingredient.objects.get(id=id)
            for key, value in data.items():
                setattr(ingredient, key, value)
            ingredient.save()
            return ingredient
        except ObjectDoesNotExist:
            return None

    def delete(self, id: int) -> None:
        Ingredient.objects.filter(id=id).delete()

    def get_with_allergens(self, id: int) -> Optional[Ingredient]:
        try:
            return Ingredient.objects.prefetch_related('allergens').get(id=id)
        except ObjectDoesNotExist:
            return None

    def get_commonly_used(self, limit: int) -> List[Ingredient]:
        return Ingredient.objects.annotate(
            usage_count=models.Count('product')
        ).order_by('-usage_count')[:limit]

class DjangoAllergenRepository(IAllergenRepository):
    def get(self, id: int) -> Optional[AllergenInfo]:
        try:
            return AllergenInfo.objects.get(id=id)
        except ObjectDoesNotExist:
            return None

    def list(self, **filters) -> QuerySet:
        return AllergenInfo.objects.filter(**filters)

    def create(self, data: Dict) -> AllergenInfo:
        return AllergenInfo.objects.create(**data)

    def update(self, id: int, data: Dict) -> Optional[AllergenInfo]:
        try:
            allergen = AllergenInfo.objects.get(id=id)
            for key, value in data.items():
                setattr(allergen, key, value)
            allergen.save()
            return allergen
        except ObjectDoesNotExist:
            return None

    def delete(self, id: int) -> None:
        AllergenInfo.objects.filter(id=id).delete()

    def get_by_ingredient(self, ingredient_id: int) -> List[AllergenInfo]:
        return AllergenInfo.objects.filter(ingredients__id=ingredient_id)

    def get_by_category(self, category_id: int) -> List[AllergenInfo]:
        return AllergenInfo.objects.filter(
            ingredients__product__category_id=category_id
        ).distinct()
