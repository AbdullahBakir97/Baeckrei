from django.db import migrations

BAKERY_CATEGORIES = [
    ('Breads', 'breads', 'Fresh bread baked every morning'),
    ('Pastries', 'pastries', 'Croissants, Danish and other pastries'),
    ('Cakes', 'cakes', 'Whole cakes and slices'),
    ('Cookies', 'cookies', 'Cookies, biscuits and small bakes'),
]


def add_bakery_categories(apps, schema_editor):
    Category = apps.get_model('products', 'Category')
    for name, slug, description in BAKERY_CATEGORIES:
        if not Category.objects.filter(slug=slug).exists() and not Category.objects.filter(name=name).exists():
            Category.objects.create(name=name, slug=slug, description=description, is_active=True)


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_product_is_seasonal'),
    ]

    operations = [
        migrations.RunPython(add_bakery_categories, migrations.RunPython.noop),
    ]
