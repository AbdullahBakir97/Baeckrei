from django.db import migrations, models
from decimal import Decimal
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('cart', '0004_cleanup_duplicate_carts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='customer',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cart', to='accounts.customer'),
        ),
        migrations.AddField(
            model_name='cart',
            name='_total_items',
            field=models.IntegerField(db_column='total_items', default=0),
        ),
        migrations.AddField(
            model_name='cart',
            name='_subtotal',
            field=models.DecimalField(db_column='subtotal', decimal_places=2, default=Decimal('0.00'), max_digits=10),
        ),
        migrations.AddField(
            model_name='cart',
            name='_tax',
            field=models.DecimalField(db_column='tax', decimal_places=2, default=Decimal('0.00'), max_digits=10),
        ),
        migrations.AddField(
            model_name='cart',
            name='session',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
    ]
