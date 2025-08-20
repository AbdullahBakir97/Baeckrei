from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from products.models import Product, Category
from decimal import Decimal
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Create sample products for testing'

    def create_placeholder_image(self, name):
        """Create a simple text file as a placeholder image"""
        content = f"Placeholder image for {name}"
        return ContentFile(content.encode(), name=f"{name.lower().replace(' ', '_')}.txt")

    def handle(self, *args, **options):
        # Create media directory if it doesn't exist
        media_root = settings.MEDIA_ROOT
        products_dir = os.path.join(media_root, 'products')
        categories_dir = os.path.join(media_root, 'categories')
        
        os.makedirs(products_dir, exist_ok=True)
        os.makedirs(categories_dir, exist_ok=True)

        # Create categories
        categories = {
            'Pizza': 'Delicious Italian pizzas',
            'Pasta': 'Fresh homemade pasta',
            'Salads': 'Fresh and healthy salads',
            'Desserts': 'Sweet treats',
            'Beverages': 'Refreshing drinks'
        }

        for name, description in categories.items():
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={
                    'description': description,
                    'image': self.create_placeholder_image(f"category_{name}")
                }
            )

        # Create products
        products = [
            {
                'name': 'Margherita Pizza',
                'description': 'Classic tomato sauce, mozzarella, and basil',
                'price': Decimal('12.99'),
                'category': 'Pizza',
                'is_vegetarian': True,
            },
            {
                'name': 'Pepperoni Pizza',
                'description': 'Tomato sauce, mozzarella, and pepperoni',
                'price': Decimal('14.99'),
                'category': 'Pizza',
            },
            {
                'name': 'Spaghetti Carbonara',
                'description': 'Classic Roman pasta with eggs, cheese, and pancetta',
                'price': Decimal('13.99'),
                'category': 'Pasta',
            },
            {
                'name': 'Vegan Pasta Primavera',
                'description': 'Fresh vegetables and herbs in olive oil sauce',
                'price': Decimal('12.99'),
                'category': 'Pasta',
                'is_vegan': True,
                'is_vegetarian': True,
            },
            {
                'name': 'Caesar Salad',
                'description': 'Romaine lettuce, croutons, parmesan, and Caesar dressing',
                'price': Decimal('9.99'),
                'category': 'Salads',
                'is_vegetarian': True,
            },
            {
                'name': 'Tiramisu',
                'description': 'Classic Italian coffee-flavored dessert',
                'price': Decimal('6.99'),
                'category': 'Desserts',
                'is_vegetarian': True,
            },
            {
                'name': 'Italian Soda',
                'description': 'Refreshing carbonated beverage with fruit syrup',
                'price': Decimal('3.99'),
                'category': 'Beverages',
                'is_vegan': True,
                'is_vegetarian': True,
            },
        ]

        for product_data in products:
            category_name = product_data.pop('category')
            category = Category.objects.get(name=category_name)
            
            defaults = {
                **product_data,
                'category': category,
                'available': True,
                'status': 'active',
                'image': self.create_placeholder_image(product_data['name'])
            }
            
            Product.objects.get_or_create(
                name=product_data['name'],
                defaults=defaults
            )

        self.stdout.write(self.style.SUCCESS('Successfully created sample products'))
