from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.files.uploadedfile import SimpleUploadedFile
from products.models import Product, Category, Ingredient, AllergenInfo, NutritionInfo
import os

User = get_user_model()

class ProductAPITestCase(APITestCase):
    def setUp(self):
        # Create test image
        self.image_path = os.path.join(os.path.dirname(__file__), 'test_image.jpg')
        with open(self.image_path, 'wb') as img:
            img.write(b'fake image data')
        self.test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=open(self.image_path, 'rb').read(),
            content_type='image/jpeg'
        )
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test category
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category',
            description='Test Category Description'
        )
        
        # Create test allergen
        self.allergen = AllergenInfo.objects.create(
            name='Test Allergen',
            description='Test Allergen Description'
        )
        
        # Create test ingredient
        self.ingredient = Ingredient.objects.create(
            name='Test Ingredient',
            description='Test Ingredient Description'
        )
        self.ingredient.allergens.add(self.allergen)
        
        # Create test nutrition info
        self.nutrition = NutritionInfo.objects.create(
            calories=200,
            proteins=5,
            carbohydrates=30,
            fats=8,
            fiber=2
        )
        
        # Create test product
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            description='Test Product Description',
            category=self.category,
            price=10.00,  # Using exactly 2 decimal places
            nutrition_info=self.nutrition,
            stock=10,
            available=True,
            status='active',
            image=self.test_image
        )
        self.product.ingredients.add(self.ingredient)

    def tearDown(self):
        # Clean up test image file
        if os.path.exists(self.image_path):
            os.remove(self.image_path)
        # Clean up media files
        if self.product.image:
            if os.path.exists(self.product.image.path):
                os.remove(self.product.image.path)

    def get_token(self):
        refresh = RefreshToken.for_user(self.user)
        return str(refresh.access_token)

    def authenticate(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_token()}')

    def test_product_list(self):
        """Test retrieving product list"""
        url = '/api/products/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_product_detail(self):
        """Test retrieving product detail"""
        url = f'/api/products/{self.product.pk}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Product')

    def test_category_list(self):
        """Test retrieving category list"""
        url = '/api/categories/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_featured_products(self):
        """Test retrieving featured products"""
        url = '/api/products/featured/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_product_filtering(self):
        """Test product filtering"""
        url = '/api/products/'
        response = self.client.get(url, {'category__slug': 'test-category'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_product_search(self):
        """Test product search"""
        url = '/api/products/'
        response = self.client.get(url, {'search': 'Test Product'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_dietary_preferences_filtering(self):
        """Test filtering products by dietary preferences"""
        # Create nutrition info for vegan product
        vegan_nutrition = NutritionInfo.objects.create(
            calories=200,
            proteins=5,
            carbohydrates=30,
            fats=8,
            fiber=3
        )
        
        # Create a vegan and gluten-free product
        vegan_product = Product.objects.create(
            name='Vegan Product',
            slug='vegan-product',
            description='A vegan product',
            category=self.category,
            price=10.00,
            nutrition_info=vegan_nutrition,
            stock=10,
            available=True,
            status='active',
            is_vegan=True,
            is_gluten_free=True,
            image=self.test_image
        )

        # Test vegan filter
        url = '/api/products/'
        response = self.client.get(url, {'vegan': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Vegan Product')

        # Test gluten-free filter
        response = self.client.get(url, {'gluten_free': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Vegan Product')

        # Test combined filters
        response = self.client.get(url, {'vegan': 'true', 'gluten_free': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_ingredient_filtering(self):
        """Test filtering products by ingredient"""
        url = '/api/products/'
        response = self.client.get(url, {'ingredient': 'Test Ingredient'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Product')

    def test_allergen_filtering(self):
        """Test filtering products by allergen"""
        url = '/api/products/'
        response = self.client.get(url, {'allergen': 'Test Allergen'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Product')
