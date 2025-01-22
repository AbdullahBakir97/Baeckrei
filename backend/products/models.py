from django.db import models, transaction
from typing import Dict, Any, Optional, List, Union
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from decimal import Decimal
import uuid
from .manager import (
    AllergenManager, IngredientManager, ProductManager, 
    CategoryManager, NutritionManager
)
from . import EXCEPTIONS

class TimeStampedModel(models.Model):
    """Abstract base model with created and modified timestamps."""
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Category(TimeStampedModel):
    """Model representing product categories (e.g., Bread, Cakes, Salads)."""
    name = models.CharField(_('Name'), max_length=100, unique=True)
    slug = models.SlugField(_('Slug'), max_length=120, unique=True, blank=True)
    description = models.TextField(_('Description'), blank=True)
    image = models.ImageField(_('Image'), upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(_('Active'), default=True)
    order = models.PositiveIntegerField(_('Display Order'), default=0)

    objects = CategoryManager()

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def merge_with(self, source_category):
        """Merge another category into this one."""
        with transaction.atomic():
            # Move all products from source to this category
            source_category.products.update(category=self)
            source_category.delete()
        return self

    def toggle_status(self):
        """Toggle active status."""
        self.is_active = not self.is_active
        self.save()
        return self

class AllergenInfo(TimeStampedModel):
    """Model for storing allergen information."""
    name = models.CharField(_('Name'), max_length=100, unique=True)
    description = models.TextField(_('Description'), blank=True)
    icon = models.ImageField(_('Icon'), upload_to='allergens/', blank=True, null=True)

    objects = AllergenManager()

    class Meta:
        verbose_name = _('Allergen Information')
        verbose_name_plural = _('Allergen Information')
        ordering = ['name']

    def __str__(self):
        return self.name

    def merge_with(self, source_allergen):
        """Merge another allergen into this one"""
        with transaction.atomic():
            ingredients_with_source = Ingredient.objects.filter(allergens=source_allergen)
            for ingredient in ingredients_with_source:
                ingredient.allergens.add(self)
                ingredient.allergens.remove(source_allergen)
            source_allergen.delete()
        return self

    def can_delete(self) -> bool:
        """Check if allergen can be safely deleted"""
        return self.ingredient_count == 0

    def delete(self, *args, **kwargs):
        """Override delete with validation"""
        if not self.can_delete():
            raise EXCEPTIONS.AllergenInUseError(
                self.id,
                self.ingredient_count
            )
        super().delete(*args, **kwargs)

class NutritionInfo(TimeStampedModel):
    """Model for storing nutritional information per 100g."""
    calories = models.DecimalField(
        _('Calories'), 
        max_digits=7, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    proteins = models.DecimalField(
        _('Proteins (g)'), 
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    carbohydrates = models.DecimalField(
        _('Carbohydrates (g)'), 
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    fats = models.DecimalField(
        _('Fats (g)'), 
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    fiber = models.DecimalField(
        _('Fiber (g)'), 
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    objects = NutritionManager()
    REQUIRED_FIELDS = ['calories', 'proteins', 'carbohydrates', 'fats', 'fiber']

    class Meta:
        verbose_name = _('Nutrition Information')
        verbose_name_plural = _('Nutrition Information')

    def __str__(self):
        return f"Nutrition Info (ID: {self.id})"

    @classmethod
    def validate_nutrition_data(cls, data: Dict[str, Any]) -> None:
        """
        Validate nutrition data fields.
        
        Args:
            data: Dictionary containing nutrition values
            
        Raises:
            NutritionValidationError: If validation fails
        """
        # Check for required fields
        missing_fields = [field for field in cls.REQUIRED_FIELDS if field not in data]
        if missing_fields:
            raise EXCEPTIONS.NutritionValidationError(
                field='required_fields',
                value=missing_fields,
                reason='Missing required nutrition fields',
                message=f"Missing required nutrition fields: {', '.join(missing_fields)}"
            )

        # Validate non-negative values
        for field in cls.REQUIRED_FIELDS:
            value = data.get(field)
            if value is not None and Decimal(str(value)) < 0:
                raise EXCEPTIONS.NutritionValidationError(
                    field=field,
                    value=value,
                    reason='Negative values not allowed',
                    message=f"Negative value not allowed for {field}: {value}"
                )

    def calculate_for_weight(self, 
                           weight_grams: Decimal,
                           round_decimals: int = 2,
                           custom_fields: Optional[List[str]] = None) -> Dict[str, Decimal]:
        """
        Calculate nutrition values for specific weight.
        
        Args:
            weight_grams: Target weight in grams
            round_decimals: Number of decimal places to round to
            custom_fields: Optional list of specific fields to calculate
            
        Returns:
            Dictionary with calculated nutrition values
            
        Raises:
            NutritionValidationError: If weight is non-positive
        """
        if weight_grams <= 0:
            raise EXCEPTIONS.NutritionValidationError(
                field='weight_grams',
                value=weight_grams,
                reason='Weight must be positive'
            )

        fields = custom_fields or self.REQUIRED_FIELDS
        multiplier = weight_grams / 100

        return {
            field: round(getattr(self, field) * multiplier, round_decimals)
            for field in fields
        }

    def get_available_fields(self) -> List[str]:
        """
        Get list of available nutrition fields.
        
        Returns:
            List of field names that contain nutrition values
        """
        return [
            field.name for field in self._meta.fields 
            if isinstance(field, (models.DecimalField, models.FloatField, models.IntegerField))
            and field.name != 'id'
        ]

    def validate_fields(self, fields: List[str]) -> None:
        """
        Validate that given fields exist in the model.
        
        Args:
            fields: List of field names to validate
            
        Raises:
            NutritionValidationError: If any field is invalid
        """
        available_fields = self.get_available_fields()
        invalid_fields = [f for f in fields if f not in available_fields]
        if invalid_fields:
            raise EXCEPTIONS.NutritionValidationError(
                field='fields',
                value=invalid_fields,
                reason='Invalid nutrition fields',
                message=f"Invalid nutrition fields: {', '.join(invalid_fields)}"
            )

    def to_dict(self) -> Dict[str, Decimal]:
        """
        Convert nutrition values to dictionary.
        
        Returns:
            Dictionary containing all nutrition values
        """
        return {
            field: getattr(self, field)
            for field in self.REQUIRED_FIELDS
        }

    def convert_to_weight(self, weight_grams: Decimal) -> Dict[str, Decimal]:
        """
        Convert nutrition values to a specific weight.
        
        Args:
            weight_grams: Target weight in grams
            
        Returns:
            Dictionary with nutrition values for target weight
        """
        return self.calculate_for_weight(weight_grams, custom_fields=self.REQUIRED_FIELDS)

class Ingredient(TimeStampedModel):
    """Model representing ingredients used in products."""
    name = models.CharField(_('Name'), max_length=100, unique=True)
    description = models.TextField(_('Description'), blank=True)
    allergens = models.ManyToManyField(
        AllergenInfo,
        verbose_name=_('Allergens'),
        related_name='ingredients',
        blank=True
    )
    is_active = models.BooleanField(_('Active'), default=True)

    objects = IngredientManager()

    class Meta:
        verbose_name = _('Ingredient')
        verbose_name_plural = _('Ingredients')
        ordering = ['name']

    def __str__(self):
        return self.name

    def merge_with(self, source_ingredient):
        """Merge another ingredient into this one"""
        with transaction.atomic():
            self.allergens.add(*source_ingredient.allergens.all())
            source_ingredient.products.update(ingredients=self)
            source_ingredient.delete()
        return self

    def toggle_status(self):
        """Toggle active status with validation"""
        if self.usage_count > 0 and self.is_active:
            raise EXCEPTIONS.IngredientInUseError(
                self.id,
                self.usage_count
            )
        self.is_active = not self.is_active
        self.save()
        return self

    def set_allergens(self, allergen_ids: List[uuid.UUID]):
        """Set allergens with validation"""
        if not AllergenInfo.objects.filter(id__in=allergen_ids).count() == len(allergen_ids):
            raise EXCEPTIONS.AllergenNotFoundError()
        self.allergens.set(allergen_ids)

class Product(TimeStampedModel):
    """Main product model for all bakery items."""
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('active', _('Active')),
        ('discontinued', _('Discontinued')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Name'), max_length=200)
    slug = models.SlugField(_('Slug'), max_length=220, unique=True, blank=True)
    description = models.TextField(_('Description'))
    category = models.ForeignKey(
        Category,
        verbose_name=_('Category'),
        related_name='products',
        on_delete=models.PROTECT
    )
    price = models.DecimalField(
        _('Price'), 
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name=_('Ingredients'),
        related_name='products'
    )
    nutrition_info = models.OneToOneField(
        NutritionInfo,
        verbose_name=_('Nutrition Information'),
        related_name='product',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    image = models.ImageField(_('Image'), upload_to='products/')
    is_vegan = models.BooleanField(_('Vegan'), default=False)
    is_vegetarian = models.BooleanField(_('Vegetarian'), default=False)
    is_gluten_free = models.BooleanField(_('Gluten Free'), default=False)
    available = models.BooleanField(default=True)
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    stock = models.PositiveIntegerField(
        _('Stock'),
        default=0,
        help_text=_('Current stock quantity')
    )

    objects = ProductManager()

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['status', 'category']),
            models.Index(fields=['name', 'slug']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def clean(self):
        """Validate the model fields."""
        if self.price and self.price < 0:
            raise EXCEPTIONS.NegativePriceError(self.id, self.price)
        if self.stock < 0:
            raise EXCEPTIONS.NegativeStockError(self.id, self.stock)

    def is_in_stock(self) -> bool:
        """Check if the product is currently in stock."""
        return self.available and self.stock > 0

    @property
    def allergens(self):
        """Get all allergens from the product's ingredients."""
        from django.db.models import Q
        allergen_ids = set()
        for ingredient in self.ingredients.all():
            allergen_ids.update(a.id for a in ingredient.allergens.all())
        return AllergenInfo.objects.filter(id__in=allergen_ids)

    def update_stock(self, quantity: int):
        """Update product stock."""
        if self.stock + quantity < 0:
            raise EXCEPTIONS.InsufficientStockError(
                self.id,
                self.stock,
                abs(quantity)
            )
        self.stock += quantity
        self.save()
        return self

    def mark_unavailable(self):
        """Mark the product as unavailable."""
        self.available = False
        self.save()
        return self

    def calculate_total_price(self, quantity: int = 1) -> Decimal:
        """Calculate total price based on quantity."""
        return self.price * Decimal(str(quantity))