import pytest
from decimal import Decimal
from django.test import TestCase
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from ...models import Product, Category, Ingredient, AllergenInfo
from ...domain.value_objects import Money, Weight, NutritionValues
from ...infrastructure.container import Container
from ...application.commands import (
    CreateProductCommand,
    UpdateProductCommand,
    UpdateStockCommand
)

@pytest.mark.django_db
class TestProductManagement(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.container = Container()
        
        # Clear cache before each test
        cache.clear()
        
        # Create test data
        self.category = Category.objects.create(
            name="Test Category",
            description="Test Description"
        )
        
        self.product = Product.objects.create(
            name="Test Product",
            category=self.category,
            price=Decimal("9.99")
        )
        
        self.ingredient = Ingredient.objects.create(
            name="Test Ingredient"
        )
        
        self.allergen = AllergenInfo.objects.create(
            name="Test Allergen"
        )

    def test_create_product(self):
        """Test creating a new product"""
        command = CreateProductCommand(
            name="New Product",
            category_id=self.category.id,
            price=Decimal("19.99"),
            description="New Description",
            ingredients=[self.ingredient.id],
            allergens=[self.allergen.id],
            nutrition_info={
                "calories": 100,
                "proteins": 10,
                "carbohydrates": 20,
                "fats": 5
            }
        )
        
        response = self.client.post(
            reverse('product-list'),
            data=command.__dict__,
            format='json'
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == "New Product"
        assert response.data['category']['id'] == self.category.id
        
        # Verify cache invalidation
        cached_product = cache.get(f"product:{response.data['id']}")
        assert cached_product is None

    def test_update_product(self):
        """Test updating an existing product"""
        command = UpdateProductCommand(
            product_id=self.product.id,
            name="Updated Product",
            price=Decimal("29.99")
        )
        
        response = self.client.patch(
            reverse('product-detail', args=[self.product.id]),
            data=command.__dict__,
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == "Updated Product"
        assert Decimal(response.data['price']) == Decimal("29.99")

    def test_update_stock(self):
        """Test updating product stock"""
        command = UpdateStockCommand(
            product_id=self.product.id,
            quantity=100,
            reason="Stock refill"
        )
        
        response = self.client.post(
            reverse('product-update-stock', args=[self.product.id]),
            data=command.__dict__,
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['stock_quantity'] == 100

    def test_get_product_nutrition(self):
        """Test retrieving product nutrition information"""
        # Create nutrition info
        self.product.nutrition_info = {
            "calories": 200,
            "proteins": 15,
            "carbohydrates": 25,
            "fats": 10
        }
        self.product.save()
        
        response = self.client.get(
            reverse('product-nutrition', args=[self.product.id])
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['calories'] == 200
        assert response.data['proteins'] == 15

    def test_find_similar_products(self):
        """Test finding similar products based on nutrition"""
        # Create products with nutrition info
        for i in range(5):
            Product.objects.create(
                name=f"Similar Product {i}",
                category=self.category,
                nutrition_info={
                    "calories": 200 + i * 10,
                    "proteins": 15 + i,
                    "carbohydrates": 25 + i,
                    "fats": 10 + i
                }
            )
        
        response = self.client.get(
            reverse('product-similar', args=[self.product.id])
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) <= 5  # Max results

    def test_category_nutrition(self):
        """Test retrieving category nutrition analysis"""
        # Create multiple products in category
        for i in range(3):
            Product.objects.create(
                name=f"Category Product {i}",
                category=self.category,
                nutrition_info={
                    "calories": 200 + i * 10,
                    "proteins": 15 + i,
                    "carbohydrates": 25 + i,
                    "fats": 10 + i
                }
            )
        
        response = self.client.get(
            reverse('category-nutrition', args=[self.category.id])
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert 'average_calories' in response.data
        assert 'average_proteins' in response.data

    def tearDown(self):
        # Clean up after each test
        cache.clear()
