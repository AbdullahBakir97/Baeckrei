from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Order, OrderItem, Payment

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal',)
    fields = ('product', 'quantity', 'price_per_item', 'subtotal')

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form
        form.base_fields['price_per_item'].required = True
        form.base_fields['quantity'].required = True
        return formset

class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0
    readonly_fields = ('created_at', 'updated_at', 'payment_date')
    fields = (
        ('payment_method', 'status', 'amount'),
        ('payment_date', 'is_verified'),
        ('transaction_id', 'ip_address'),
        ('payment_gateway_response', 'failure_reason'),
        ('created_at', 'updated_at')
    )

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer_name', 'total_price', 'status', 'created_at', 'payment_status')
    list_filter = ('status', 'created_at', 'order_payment__status')
    search_fields = ('order_number', 'customer__name', 'notes')
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'total_items', 'total_price')
    inlines = [OrderItemInline, PaymentInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': (
                'order_number', 'customer', 'status', ('total_items', 'total_price')
            )
        }),
        ('Shipping Details', {
            'fields': (
                'address', 'shipping_tracking_number', 'estimated_delivery_date'
            )
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def customer_name(self, obj):
        return obj.customer.name
    customer_name.admin_order_field = 'customer__name'

    def payment_status(self, obj):
        payment = getattr(obj, 'order_payment', None)
        if payment:
            status_colors = {
                'Pending': 'orange',
                'Completed': 'green',
                'Failed': 'red',
                'Refunded': 'blue'
            }
            color = status_colors.get(payment.status, 'gray')
            return format_html(
                '<span style="color: {};">{}</span>',
                color,
                payment.get_status_display()
            )
        return '-'
    payment_status.short_description = 'Payment Status'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_link', 'amount', 'payment_method', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'is_verified')
    search_fields = ('order__order_number', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at', 'payment_date')
    
    fieldsets = (
        ('Payment Information', {
            'fields': (
                'order', 'amount', 'payment_method', 'status', 'is_verified'
            )
        }),
        ('Transaction Details', {
            'fields': (
                'transaction_id', 'payment_date', 'ip_address', 
                'payment_gateway_response', 'failure_reason'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def order_link(self, obj):
        url = reverse('admin:orders_order_change', args=[obj.order.id])
        return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
    order_link.short_description = 'Order'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_link', 'product', 'quantity', 'price_per_item', 'subtotal')
    list_filter = ('order__status',)
    search_fields = ('order__order_number', 'product__name')
    
    def order_link(self, obj):
        url = reverse('admin:orders_order_change', args=[obj.order.id])
        return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
    order_link.short_description = 'Order'