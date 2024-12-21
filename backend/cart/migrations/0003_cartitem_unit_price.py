# Generated by Django 5.1.4 on 2024-12-20 21:30

import django.core.validators
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cart", "0002_remove_cart_is_active_remove_cart_session_id_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="cartitem",
            name="unit_price",
            field=models.DecimalField(
                decimal_places=2,
                default=12,
                max_digits=10,
                validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
            ),
            preserve_default=False,
        ),
    ]