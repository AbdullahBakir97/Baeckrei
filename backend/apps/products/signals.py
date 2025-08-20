from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from .models import Product, NutritionInfo

@receiver(pre_save, sender=Product)
def check_stock(sender, instance, **kwargs):
    if instance.stock == 0 and instance.status != 'discontinued':
        instance.status = 'discontinued'
    elif instance.stock > 0 and instance.status == 'discontinued':
        instance.status = 'active'

@receiver(post_save, sender=Product)
def create_nutrition_info(sender, instance, created, **kwargs):
    """Auto-create NutritionInfo for a new Product."""
    if created:
        NutritionInfo.objects.create(product=instance)

@receiver(pre_delete, sender=Product)
def log_product_deletion(sender, instance, **kwargs):
    """Log or handle tasks before a Product is deleted."""
    # Example: Notify admin about product deletion
    print(f"Product '{instance.name}' is being deleted.")