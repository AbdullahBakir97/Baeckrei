from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Product, Category, Ingredient, AllergenInfo, NutritionInfo

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'order', 'product_count')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = _('Products')

@admin.register(AllergenInfo)
class AllergenInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_icon')
    search_fields = ('name', 'description')

    def display_icon(self, obj):
        if obj.icon:
            return format_html('<img src="{}" width="30" height="30" />', obj.icon.url)
        return '-'
    display_icon.short_description = _('Icon')

@admin.register(NutritionInfo)
class NutritionInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'calories', 'proteins', 'carbohydrates', 'fats', 'fiber')
    search_fields = ('id',)
    list_filter = ('calories', 'proteins')

class IngredientInline(admin.TabularInline):
    model = Product.ingredients.through
    extra = 1

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'allergen_list')
    list_filter = ('is_active', 'allergens')
    search_fields = ('name', 'description')
    filter_horizontal = ('allergens',)

    def allergen_list(self, obj):
        return ", ".join([allergen.name for allergen in obj.allergens.all()])
    allergen_list.short_description = _('Allergens')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'status', 'available', 'is_vegan', 'is_vegetarian', 'is_gluten_free')
    list_filter = (
        'status',
        'available',
        'category',
        'is_vegan',
        'is_vegetarian',
        'is_gluten_free'
    )
    search_fields = ('name', 'description', 'category__name')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('id',)
    filter_horizontal = ('ingredients',)
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('id', 'name', 'slug', 'description', 'category', 'price', 'image')
        }),
        (_('Stock Information'), {
            'fields': ('stock', 'available', 'status')
        }),
        (_('Dietary Information'), {
            'fields': ('is_vegan', 'is_vegetarian', 'is_gluten_free')
        }),
        (_('Additional Information'), {
            'fields': ('ingredients', 'nutrition_info'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'category',
            'nutrition_info'
        ).prefetch_related('ingredients')
