from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Customer, Address

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_admin', 'is_active')
    list_filter = ('is_staff', 'is_admin', 'is_active', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_admin', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'is_admin'),
        }),
    )

class AddressInline(admin.StackedInline):
    model = Address
    extra = 0
    fields = (
        ('address_line_1', 'address_line_2'),
        ('city', 'state'),
        ('postal_code', 'country'),
    )

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'user', 'name', 'email', 'address_display', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('customer_id', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [AddressInline]
    
    fieldsets = (
        (_('Customer Info'), {
            'fields': ('customer_id', 'user', 'address')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def name(self, obj):
        return obj.name
    
    def email(self, obj):
        return obj.email

    def address_display(self, obj):
        return obj.address if obj.address else '-'
    address_display.short_description = 'Primary Address'

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'address_line_1', 'city', 'state', 'country')
    list_filter = ('country', 'state', 'city')
    search_fields = ('address_line_1', 'address_line_2', 'city', 'state', 'country', 'customer__customer_id')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Address Info'), {
            'fields': (
                'customer',
                ('address_line_1', 'address_line_2'),
                ('city', 'state'),
                ('postal_code', 'country'),
            )
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )