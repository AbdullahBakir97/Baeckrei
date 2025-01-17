from rest_framework import serializers
from .models import Product, Category, Ingredient, AllergenInfo, NutritionInfo

class NutritionInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionInfo
        fields = ['calories', 'proteins', 'carbohydrates', 'fats', 'fiber']

class AllergenInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllergenInfo
        fields = ['id', 'name', 'description', 'icon']

class IngredientSerializer(serializers.ModelSerializer):
    allergens = AllergenInfoSerializer(many=True, read_only=True)

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'description', 'allergens', 'is_active']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'description', 'price', 'stock',
            'category', 'category_name', 'image', 'status',
            'is_vegan', 'is_vegetarian', 'is_gluten_free',
            'available', 'created_at', 'modified_at'
        )
        read_only_fields = ('id', 'created_at', 'modified_at')

class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category', 'price',
            'image', 'is_vegan', 'is_vegetarian',
            'is_gluten_free', 'available', 'stock'
        ]

class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)
    nutrition_info = NutritionInfoSerializer(read_only=True)
    allergens = AllergenInfoSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'category',
            'price', 'ingredients', 'nutrition_info', 'image',
            'is_vegan', 'is_vegetarian', 'is_gluten_free',
            'available', 'status', 'stock', 'created_at',
            'modified_at', 'allergens'
        ]
