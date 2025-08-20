from django.apps import AppConfig


class CartConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.cart'
    
    def ready(self):
        """Initialize app and register signals."""
        # Import signals to register handlers
        from . import signals  # noqa
