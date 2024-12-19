# Generated by Django 5.1.4 on 2024-12-19 12:39

import django.core.validators
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AllergenInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Name')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('icon', models.ImageField(blank=True, null=True, upload_to='allergens/', verbose_name='Icon')),
            ],
            options={
                'verbose_name': 'Allergen Information',
                'verbose_name_plural': 'Allergen Information',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Name')),
                ('slug', models.SlugField(blank=True, max_length=120, unique=True, verbose_name='Slug')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('image', models.ImageField(blank=True, null=True, upload_to='categories/', verbose_name='Image')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Display Order')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='NutritionInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('calories', models.DecimalField(decimal_places=2, max_digits=7, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Calories')),
                ('proteins', models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Proteins (g)')),
                ('carbohydrates', models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Carbohydrates (g)')),
                ('fats', models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Fats (g)')),
                ('fiber', models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Fiber (g)')),
            ],
            options={
                'verbose_name': 'Nutrition Information',
                'verbose_name_plural': 'Nutrition Information',
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Name')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('allergens', models.ManyToManyField(blank=True, related_name='ingredients', to='products.allergeninfo', verbose_name='Allergens')),
            ],
            options={
                'verbose_name': 'Ingredient',
                'verbose_name_plural': 'Ingredients',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('slug', models.SlugField(blank=True, max_length=220, unique=True, verbose_name='Slug')),
                ('description', models.TextField(verbose_name='Description')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Price')),
                ('image', models.ImageField(upload_to='products/', verbose_name='Image')),
                ('is_vegan', models.BooleanField(default=False, verbose_name='Vegan')),
                ('is_vegetarian', models.BooleanField(default=False, verbose_name='Vegetarian')),
                ('is_gluten_free', models.BooleanField(default=False, verbose_name='Gluten Free')),
                ('available', models.BooleanField(default=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('active', 'Active'), ('discontinued', 'Discontinued')], default='draft', max_length=20, verbose_name='Status')),
                ('stock', models.PositiveIntegerField(default=0, help_text='Current stock quantity', verbose_name='Stock')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='products', to='products.category', verbose_name='Category')),
                ('ingredients', models.ManyToManyField(related_name='products', to='products.ingredient', verbose_name='Ingredients')),
                ('nutrition_info', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='product', to='products.nutritioninfo', verbose_name='Nutrition Information')),
            ],
            options={
                'verbose_name': 'Product',
                'verbose_name_plural': 'Products',
                'ordering': ['category', 'name'],
                'indexes': [models.Index(fields=['status', 'category'], name='products_pr_status_142af0_idx'), models.Index(fields=['name', 'slug'], name='products_pr_name_49020f_idx')],
            },
        ),
    ]
