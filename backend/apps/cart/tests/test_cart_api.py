"""End-to-end tests for the cart REST endpoints the frontend uses."""
from decimal import Decimal

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.products.models import Category, Product

CART_URL = '/api/shopping-cart/'


@pytest.fixture(autouse=True)
def temp_media_root(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path


@pytest.fixture
def product(db):
    category = Category.objects.create(name='Brot', description='Bread')
    return Product.objects.create(
        name='Roggenbrot',
        description='Rye bread',
        category=category,
        price=Decimal('3.50'),
        stock=5,
        status='active',
        available=True,
        image=SimpleUploadedFile('rye.png', b'\x89PNG', content_type='image/png'),
    )


@pytest.fixture
def client():
    return APIClient()


def add(client, product, quantity=1):
    return client.post(f'{CART_URL}add/', {'product_id': str(product.id), 'quantity': quantity}, format='json')


def test_guest_can_view_empty_cart(client):
    response = client.get(CART_URL)
    assert response.status_code == 200, response.content
    assert response.json()['items'] == []


def test_guest_add_update_remove_and_clear(client, product):
    response = add(client, product, 2)
    assert response.status_code == 200, response.content
    items = response.json()['items']
    assert len(items) == 1
    assert items[0]['product'] == str(product.id)
    assert items[0]['quantity'] == 2
    assert response.json()['total_items'] == 2

    # The same session sees the same cart.
    assert client.get(CART_URL).json()['items'][0]['quantity'] == 2

    response = client.put(f'{CART_URL}update/{product.id}/', {'quantity': 3}, format='json')
    assert response.status_code == 200, response.content
    assert response.json()['items'][0]['quantity'] == 3

    response = client.delete(f'{CART_URL}remove/{product.id}/')
    assert response.status_code == 200, response.content
    assert response.json()['items'] == []

    add(client, product, 1)
    response = client.post(f'{CART_URL}clear/')
    assert response.status_code == 200, response.content
    assert response.json()['items'] == []


def test_cart_operations_never_change_stock(client, product):
    # Stock is only deducted at checkout.
    add(client, product, 3)
    client.put(f'{CART_URL}update/{product.id}/', {'quantity': 4}, format='json')
    product.refresh_from_db()
    assert product.stock == 5
    client.delete(f'{CART_URL}remove/{product.id}/')
    product.refresh_from_db()
    assert product.stock == 5


def test_cart_quantity_is_capped_by_stock(client, product):
    assert add(client, product, 3).status_code == 200
    assert add(client, product, 2).status_code == 200  # 5 of 5
    response = add(client, product, 1)                  # 6 of 5
    assert response.status_code == 400
    assert response.json()['error_type'] == 'insufficient_stock'
    response = client.put(f'{CART_URL}update/{product.id}/', {'quantity': 6}, format='json')
    assert response.status_code == 400
    assert client.get(CART_URL).json()['items'][0]['quantity'] == 5


def test_cannot_add_more_than_stock(client, product):
    response = add(client, product, 6)
    assert response.status_code == 400
    assert response.json()['error_type'] == 'insufficient_stock'


def test_jwt_user_cart_follows_the_user_not_the_session(product):
    user = User.objects.create_user(email='jwt@example.com', password='Str0ng-Passw0rd!')
    first = APIClient()
    first.force_authenticate(user)
    assert add(first, product, 2).status_code == 200

    # A different client (new session) authenticated as the same user
    # sees the same cart.
    second = APIClient()
    second.force_authenticate(user)
    items = second.get(CART_URL).json()['items']
    assert [i['quantity'] for i in items] == [2]
