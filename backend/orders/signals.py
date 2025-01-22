from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order

@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, created, **kwargs):
    if not created and instance.tracker.has_changed('status'):
        # Send notification to customer
        if instance.status == Order.StatusChoices.PROCESSING:
            # Send order processing notification
            pass
        elif instance.status == Order.StatusChoices.COMPLETED:
            # Send order completed notification
            pass