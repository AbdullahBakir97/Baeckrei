# services/reports.py
from django.db.models import Avg, Count, Sum, F, Q
from django.core.cache import cache
from datetime import datetime, timedelta
from typing import Dict, Any, List

from ..models import Product, Category, Ingredient, AllergenInfo

class ReportService:
    """Service for generating various reports and analytics."""
    
    CACHE_TIMEOUT = 300  # 5 minutes
    
    @staticmethod
    def get_product_statistics() -> Dict[str, Any]:
        """Get comprehensive product statistics."""
        cache_key = "product_statistics"
        stats = cache.get(cache_key)
        
        if not stats:
            products = Product.objects.all()
            stats = {
                'total_products': products.count(),
                'active_products': products.filter(available=True).count(),
                'out_of_stock': products.filter(stock=0).count(),
                'low_stock': products.filter(stock__gt=0, stock__lt=10).count(),
                'average_price': products.aggregate(avg_price=Avg('price'))['avg_price'],
                'total_value': products.aggregate(
                    total=Sum(F('price') * F('stock')))['total'],
                'by_category': products.values('category__name').annotate(
                    count=Count('id'),
                    avg_price=Avg('price'),
                    total_stock=Sum('stock')
                ),
                'dietary_counts': {
                    'vegan': products.filter(is_vegan=True).count(),
                    'vegetarian': products.filter(is_vegetarian=True).count(),
                    'gluten_free': products.filter(is_gluten_free=True).count()
                }
            }
            cache.set(cache_key, stats, ReportService.CACHE_TIMEOUT)
        
        return stats
    
    @staticmethod
    def get_category_statistics() -> Dict[str, Any]:
        """Get comprehensive category statistics."""
        cache_key = "category_statistics"
        stats = cache.get(cache_key)
        
        if not stats:
            categories = Category.objects.all()
            stats = {
                'total_categories': categories.count(),
                'active_categories': categories.filter(is_active=True).count(),
                'by_products': categories.annotate(
                    product_count=Count('products'),
                    avg_product_price=Avg('products__price'),
                    total_stock=Sum('products__stock')
                ).values('name', 'product_count', 'avg_product_price', 'total_stock'),
                'empty_categories': categories.filter(products=None).count()
            }
            cache.set(cache_key, stats, ReportService.CACHE_TIMEOUT)
        
        return stats
    
    @staticmethod
    def get_ingredient_statistics() -> Dict[str, Any]:
        """Get comprehensive ingredient statistics."""
        cache_key = "ingredient_statistics"
        stats = cache.get(cache_key)
        
        if not stats:
            ingredients = Ingredient.objects.all()
            stats = {
                'total_ingredients': ingredients.count(),
                'active_ingredients': ingredients.filter(is_active=True).count(),
                'allergen_stats': ingredients.values('allergens__name').annotate(
                    count=Count('id')
                ).order_by('-count'),
                'most_used': ingredients.annotate(
                    usage_count=Count('products')
                ).order_by('-usage_count')[:10].values('name', 'usage_count'),
                'unused': ingredients.filter(products=None).count()
            }
            cache.set(cache_key, stats, ReportService.CACHE_TIMEOUT)
        
        return stats
    
    @staticmethod
    def get_allergen_statistics() -> Dict[str, Any]:
        """Get comprehensive allergen statistics."""
        cache_key = "allergen_statistics"
        stats = cache.get(cache_key)
        
        if not stats:
            allergens = AllergenInfo.objects.all()
            stats = {
                'total_allergens': allergens.count(),
                'by_ingredients': allergens.annotate(
                    ingredient_count=Count('ingredients', distinct=True),
                    product_count=Count('ingredients__products', distinct=True)
                ).values('name', 'ingredient_count', 'product_count'),
                'most_common': allergens.annotate(
                    usage_count=Count('ingredients__products', distinct=True)
                ).order_by('-usage_count')[:5].values('name', 'usage_count')
            }
            cache.set(cache_key, stats, ReportService.CACHE_TIMEOUT)
        
        return stats
    
    @staticmethod
    def generate_inventory_report() -> Dict[str, Any]:
        """Generate a comprehensive inventory report."""
        cache_key = "inventory_report"
        report = cache.get(cache_key)
        
        if not report:
            products = Product.objects.all()
            report = {
                'low_stock_items': products.filter(
                    stock__gt=0, stock__lt=10
                ).values('name', 'stock', 'category__name'),
                'out_of_stock': products.filter(
                    stock=0
                ).values('name', 'category__name'),
                'overstocked_items': products.filter(
                    stock__gt=F('max_stock')
                ).values('name', 'stock', 'max_stock', 'category__name'),
                'stock_value': products.aggregate(
                    total=Sum(F('price') * F('stock')))['total']
            }
            cache.set(cache_key, report, ReportService.CACHE_TIMEOUT)
        
        return report
