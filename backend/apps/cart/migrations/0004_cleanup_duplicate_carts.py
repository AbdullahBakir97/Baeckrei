from django.db import migrations

def cleanup_duplicate_carts(apps, schema_editor):
    Cart = apps.get_model('cart', 'Cart')
    Customer = apps.get_model('accounts', 'Customer')
    
    # For each customer, keep only their most recent cart
    for customer in Customer.objects.all():
        carts = Cart.objects.filter(customer=customer).order_by('-created_at')
        if carts.count() > 1:
            # Keep the most recent cart, delete the rest
            latest_cart = carts.first()
            carts.exclude(id=latest_cart.id).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('cart', '0003_cartitem_unit_price'),
    ]

    operations = [
        migrations.RunPython(cleanup_duplicate_carts, reverse_code=migrations.RunPython.noop),
    ]
