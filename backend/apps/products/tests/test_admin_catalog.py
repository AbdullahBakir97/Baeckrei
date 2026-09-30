"""Product and category management used by the admin pages."""
import io
import uuid
from decimal import Decimal

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APIClient

from apps.accounts.models import Customer, User
from apps.orders.models import Order, OrderItem
from apps.products.models import Category, Product


@pytest.fixture(autouse=True)
def temp_media_root(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path


def png(name='bread.png'):
    buffer = io.BytesIO()
    Image.new('RGB', (4, 4), 'orange').save(buffer, format='PNG')
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/png')


@pytest.fixture
def admin_client(db):
    admin = User.objects.create_superuser(email='boss@example.com', password='Str0ng-Passw0rd!')
    client = APIClient()
    client.force_authenticate(admin)
    return client


@pytest.fixture
def breads(db):
    return Category.objects.get(slug='breads')


def test_admin_creates_updates_and_deletes_a_product(admin_client, breads):
    response = admin_client.post('/api/products/', {
        'name': 'Dinkelbrot', 'description': 'Spelt bread', 'category': breads.id,
        'price': '4.20', 'stock': 12, 'status': 'active', 'available': True, 'image': png(),
    }, format='multipart')
    assert response.status_code == 201, response.content
    product_id = response.json()['id']

    response = admin_client.patch(f'/api/products/{product_id}/', {'price': '4.50', 'is_seasonal': True}, format='json')
    assert response.status_code == 200, response.content
    product = Product.objects.get(pk=product_id)
    assert product.price == Decimal('4.50') and product.is_seasonal

    assert admin_client.delete(f'/api/products/{product_id}/').status_code == 204
    assert not Product.objects.filter(pk=product_id).exists()


def test_product_needs_an_image_and_a_positive_price(admin_client, breads):
    response = admin_client.post('/api/products/', {
        'name': 'No image', 'description': 'x', 'category': breads.id, 'price': '0', 'stock': 1,
    }, format='multipart')
    assert response.status_code == 400
    assert set(response.json()) >= {'price'}


def test_rejects_non_image_upload(admin_client, breads):
    fake = SimpleUploadedFile('menu.txt', b'hello', content_type='text/plain')
    response = admin_client.post('/api/products/', {
        'name': 'Bad', 'description': 'x', 'category': breads.id, 'price': '1.00', 'stock': 1, 'image': fake,
    }, format='multipart')
    assert response.status_code == 400
    assert 'image' in response.json()


def test_deleting_an_ordered_product_discontinues_it(admin_client, breads):
    product = Product.objects.create(
        name='Brezel', description='x', category=breads, price=Decimal('1.00'), stock=5,
        status='active', available=True, image=png(),
    )
    user = User.objects.create_user(email='c@example.com', password='Str0ng-Passw0rd!')
    customer = Customer.objects.create(user=user, customer_id=uuid.uuid4().hex)
    order = Order.objects.create(customer=customer)
    OrderItem.objects.create(order=order, product=product, quantity=1, price_per_item=Decimal('1.00'))

    response = admin_client.delete(f'/api/products/{product.id}/')
    assert response.status_code == 200 and response.json()['discontinued']
    product.refresh_from_db()
    assert product.status == 'discontinued' and not product.available


def test_invalid_product_id_is_404(admin_client):
    assert admin_client.patch('/api/products/not-a-uuid/', {}, format='json').status_code == 404


def test_customers_cannot_manage_products(db, breads):
    user = User.objects.create_user(email='c@example.com', password='Str0ng-Passw0rd!')
    client = APIClient()
    client.force_authenticate(user)
    assert client.post('/api/products/', {}, format='json').status_code == 403
    assert client.post('/api/products/create_category/', {'name': 'X'}, format='json').status_code == 403


def test_category_crud(admin_client, breads):
    response = admin_client.post('/api/products/create_category/', {'name': 'Brötchen', 'description': 'Rolls'}, format='json')
    assert response.status_code == 201, response.content
    category_id = response.json()['id']
    assert response.json()['slug']

    response = admin_client.patch(f'/api/products/{category_id}/update_category/', {'is_active': False}, format='json')
    assert response.status_code == 200 and response.json()['is_active'] is False

    listed = admin_client.get('/api/products/categories/', {'include_inactive': 'true'}).json()['results']
    assert any(c['id'] == category_id for c in listed)
    public = APIClient().get('/api/products/categories/').json()['results']
    assert not any(c['id'] == category_id for c in public)

    assert admin_client.delete(f'/api/products/{category_id}/delete_category/').status_code == 204


def test_category_with_products_cannot_be_deleted(admin_client, breads):
    Product.objects.create(name='Roggen', description='x', category=breads, price=Decimal('1.00'),
                           stock=1, status='active', available=True, image=png())
    response = admin_client.delete(f'/api/products/{breads.id}/delete_category/')
    assert response.status_code == 400
    assert Category.objects.filter(pk=breads.id).exists()


def test_low_stock_report(admin_client, breads):
    Product.objects.create(name='Last loaf', description='x', category=breads, price=Decimal('1.00'),
                           stock=2, status='active', available=True, image=png())
    response = admin_client.get('/api/products/low_stock/')
    assert response.status_code == 200
    assert [p['name'] for p in response.json()] == ['Last loaf']
