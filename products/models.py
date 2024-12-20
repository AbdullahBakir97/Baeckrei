from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from decimal import Decimal
import uuid
from .manager import ProductManager

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

class AllergenInfo(TimeStampedModel):
    """Model for storing allergen information."""
    name = models.CharField(_('Name'), max_length=100, unique=True)
    description = models.TextField(_('Description'), blank=True)
    icon = models.ImageField(_('Icon'), upload_to='allergens/', blank=True, null=True)

    class Meta:
        verbose_name = _('Allergen Information')
        verbose_name_plural = _('Allergen Information')
        ordering = ['name']

    def __str__(self):
        return self.name

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

    class Meta:
        verbose_name = _('Nutrition Information')
        verbose_name_plural = _('Nutrition Information')

    def __str__(self):
        return f"Nutrition Info (ID: {self.id})"

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

    class Meta:
        verbose_name = _('Ingredient')
        verbose_name_plural = _('Ingredients')
        ordering = ['name']

    def __str__(self):
        return self.name



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
    # preparation_time = models.DurationField(
    #     _('Preparation Time'),
    #     help_text=_('Expected preparation time'),
    #     null=True,
    #     blank=True
    # )

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
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        """Validate the model fields."""
        super().clean()
        if self.price < 0:
            raise ValidationError(_('Price cannot be negative.'))
        if self.stock < 0:
            raise ValidationError(_('Stock cannot be negative.'))

    @property
    def is_in_stock(self):
        """Check if the product is currently in stock."""
        return self.stock > 0

    @property
    def allergens(self):
        """Get all allergens from the product's ingredients."""
        return AllergenInfo.objects.filter(ingredients__products=self).distinct()

    def update_stock(self, quantity):
        """Update product stock."""
        if self.stock + quantity < 0:
            raise ValidationError(_('Insufficient stock available.'))
        self.stock += quantity
        self.save()

    def mark_unavailable(self):
        """Mark the product as unavailable."""
        self.available = False
        self.save()

    def calculate_total_price(self, quantity=1):
        """Calculate total price based on quantity."""
        return self.price * quantity