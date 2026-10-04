from django.contrib import admin

from .models import MenuScreen, MenuSlide


class SlideInline(admin.TabularInline):
    model = MenuSlide
    extra = 0


@admin.register(MenuScreen)
class MenuScreenAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'code', 'layout', 'theme', 'is_default', 'last_seen_at')
    inlines = [SlideInline]
