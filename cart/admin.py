from django.contrib import admin
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('total_price',)
    raw_id_fields = ('product',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'total_items', 'subtotal', 'tax', 'total', 'completed', 'completed_at', 'created_at', 'modified_at')
    list_filter = ('completed', 'created_at')
    search_fields = ('customer__user__email', 'customer__customer_id')
    readonly_fields = ('total_items', 'subtotal', 'tax', 'total', 'completed_at')
    inlines = [CartItemInline]
    date_hierarchy = 'created_at'

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of carts
        return False

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity', 'total_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('cart__customer__user__email', 'cart__customer__customer_id', 'product__name')
    readonly_fields = ('total_price',)
    raw_id_fields = ('cart', 'product')
    date_hierarchy = 'created_at'
