"""Fill an empty database with a small demo bakery.

    python manage.py seed_demo
    python manage.py seed_demo --customer demo@example.com --password '...'

Creates a few categories and products (with simple generated photos) and,
if asked, a customer account. Safe to run again: existing entries are kept.
Used by the end-to-end tests (frontend/e2e) and for trying the shop locally.
"""
import io
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw

from apps.products.models import Category, Product

CATEGORIES = [
    ('Brot', 'Breads', 'Sauerteigbrote, lange geführt.', 'Sourdough loaves, slowly proved.'),
    ('Gebäck', 'Pastries', 'Jeden Morgen frisch laminiert.', 'Laminated fresh every morning.'),
    ('Kuchen', 'Cakes', 'Nach Hausrezept.', 'From our own recipes.'),
]

PRODUCTS = [
    # name, English name, category, price, colour, vegan
    ('Roggenbrot', 'Rye bread', 'Brot', '4.20', (122, 78, 44), True),
    ('Dinkelvollkornbrot', 'Spelt wholemeal bread', 'Brot', '4.80', (164, 112, 64), True),
    ('Buttercroissant', 'Butter croissant', 'Gebäck', '2.10', (221, 158, 82), False),
    ('Franzbrötchen', 'Cinnamon roll', 'Gebäck', '2.40', (190, 120, 60), False),
    ('Käsekuchen', 'Cheesecake', 'Kuchen', '3.60', (238, 210, 150), False),
]


def photo(colour):
    """A plain round 'pastry' on a transparent background."""
    image = Image.new('RGBA', (600, 600), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((60, 110, 540, 490), fill=colour + (255,))
    highlight = tuple(min(255, c + 40) for c in colour) + (255,)
    draw.ellipse((150, 170, 400, 300), fill=highlight)
    buffer = io.BytesIO()
    image.save(buffer, 'PNG')
    return buffer.getvalue()


class Command(BaseCommand):
    help = 'Create demo categories, products and (optionally) a customer account.'

    def add_arguments(self, parser):
        parser.add_argument('--customer', help='Email of a customer account to create')
        parser.add_argument('--password', help='Password for that account')
        parser.add_argument('--stock', type=int, default=50, help='Stock for each demo product')

    def handle(self, *args, **options):
        categories = {}
        for name, name_en, description, description_en in CATEGORIES:
            categories[name], _created = Category.objects.get_or_create(
                name=name, defaults={'name_en': name_en, 'description': description, 'description_en': description_en},
            )

        created = 0
        for name, name_en, category, price, colour, vegan in PRODUCTS:
            if Product.objects.filter(name=name).exists():
                continue
            product = Product(
                name=name, name_en=name_en, category=categories[category], price=Decimal(price),
                description=f'{name} aus unserer Backstube.', description_en=f'{name_en} from our bakery.',
                stock=options['stock'], status='active', available=True, is_vegan=vegan, is_vegetarian=True,
            )
            product.image.save(f'{product.slug or name.lower()}.png', ContentFile(photo(colour)), save=False)
            product.save()
            created += 1

        if options['customer']:
            User = get_user_model()
            if not User.objects.filter(email=options['customer']).exists():
                User.objects.create_user(
                    email=options['customer'], password=options['password'], first_name='Demo', last_name='Kunde',
                )
                self.stdout.write(f"Created customer {options['customer']}")

        self.stdout.write(self.style.SUCCESS(f'Demo bakery ready ({created} new products).'))
