from django.contrib import admin

from .models import ClosingDay, ShopSettings

admin.site.register(ShopSettings)
admin.site.register(ClosingDay)
