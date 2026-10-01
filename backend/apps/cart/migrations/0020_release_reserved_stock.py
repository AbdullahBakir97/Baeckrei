from django.db import migrations
from django.db.models import F


def release_reserved_stock(apps, schema_editor):
    """Stock used to be deducted when items were added to a cart. It is now
    only deducted at checkout, so give back what open carts were holding."""
    CartItem = apps.get_model('cart', 'CartItem')
    Product = apps.get_model('products', 'Product')
    open_items = CartItem.objects.filter(cart__completed=False, product__isnull=False)
    for item in open_items.iterator():
        Product.objects.filter(pk=item.product_id).update(stock=F('stock') + item.quantity)


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0019_rename_modified_at_cart_updated_at_and_more'),
        ('products', '0003_product_version'),
    ]

    operations = [
        migrations.RunPython(release_reserved_stock, migrations.RunPython.noop),
    ]
