"""Filters used by the category, seasonal and dietary views of the shop."""
from decimal import Decimal

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from apps.products.models import Category, Product


@pytest.fixture(autouse=True)
def temp_media_root(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path


def make_product(name, category, **extra):
    return Product.objects.create(
        name=name, description=name, category=category, price=Decimal('2.00'), stock=10,
        status='active', available=True,
        image=SimpleUploadedFile(f'{name}.png', b'\x89PNG', content_type='image/png'),
        **extra,
    )


@pytest.fixture
def catalog(db):
    breads = Category.objects.get(slug='breads')  # created by migration
    cakes = Category.objects.get(slug='cakes')
    make_product('Roggenbrot', breads, is_vegan=True)
    make_product('Stollen', cakes, is_seasonal=True)
    make_product('Käsekuchen', cakes)


def names(response):
    assert response.status_code == 200, response.content
    return sorted(p['name'] for p in response.json()['results'])


def test_bakery_categories_exist(db):
    slugs = set(Category.objects.values_list('slug', flat=True))
    assert {'breads', 'pastries', 'cakes', 'cookies'} <= slugs


def test_filter_by_category_slug(catalog):
    assert names(APIClient().get('/api/products/', {'category': 'cakes'})) == ['Käsekuchen', 'Stollen']


def test_seasonal_filter(catalog):
    assert names(APIClient().get('/api/products/', {'seasonal': 'true'})) == ['Stollen']


def test_false_dietary_flag_does_not_filter(catalog):
    assert len(names(APIClient().get('/api/products/', {'is_vegan': 'false'}))) == 3
    assert names(APIClient().get('/api/products/', {'is_vegan': 'true'})) == ['Roggenbrot']


def test_shop_hides_drafts_but_staff_can_list_everything(catalog):
    from apps.accounts.models import User
    make_product('Secret recipe', Category.objects.get(slug='cakes'), )
    Product.objects.filter(name='Secret recipe').update(status='draft')
    assert 'Secret recipe' not in names(APIClient().get('/api/products/'))
    # include_all is ignored for anonymous users
    assert 'Secret recipe' not in names(APIClient().get('/api/products/', {'include_all': 'true'}))

    staff = APIClient()
    staff.force_authenticate(User.objects.create_superuser(email='boss@example.com', password='Str0ng-Passw0rd!'))
    assert 'Secret recipe' in names(staff.get('/api/products/', {'include_all': 'true'}))
    assert names(staff.get('/api/products/', {'include_all': 'true', 'status': 'draft'})) == ['Secret recipe']


def test_inventory_reports_are_staff_only(catalog):
    assert APIClient().get('/api/products/report/').status_code in (401, 403)
    assert APIClient().get('/api/products/inventory_report/').status_code in (401, 403)
