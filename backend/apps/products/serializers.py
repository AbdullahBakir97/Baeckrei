from rest_framework import serializers
from .models import Product, Category, Ingredient, AllergenInfo, NutritionInfo
import logging

logger = logging.getLogger(__name__)

class NutritionInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionInfo
        fields = ['calories', 'proteins', 'carbohydrates', 'fats', 'fiber']

class NutritionInfoCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating nutrition information."""
    weight_grams = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False,
        help_text="Weight in grams for the nutrition values. If provided, values will be converted to per 100g."
    )

    class Meta:
        model = NutritionInfo
        fields = ['calories', 'proteins', 'carbohydrates', 'fats', 'fiber', 'weight_grams']

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
    product_count = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'image_url', 'is_active', 'order', 'product_count']

    def get_product_count(self, obj):
        return obj.products.filter(status='active', available=True).count()

    def get_image_url(self, obj):
        try:
            if obj.image:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(obj.image.url)
        except Exception as e:
            logger.warning(f"Error getting image URL for category {obj.id}: {str(e)}")
        return None

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
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category', 'price',
            'image', 'image_url', 'is_vegan', 'is_vegetarian',
            'is_gluten_free', 'available', 'stock'
        ]

    def get_image_url(self, obj):
        try:
            if obj.image:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(obj.image.url)
        except Exception as e:
            logger.warning(f"Error getting image URL for product {obj.id}: {str(e)}")
        return None

class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)
    allergens = AllergenInfoSerializer(many=True, read_only=True)
    nutrition_info = NutritionInfoSerializer(read_only=True)
    image_url = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    stock_status = serializers.SerializerMethodField()
    formatted_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'category',
            'price', 'formatted_price', 'image', 'image_url', 'images',
            'is_vegan', 'is_vegetarian', 'is_gluten_free',
            'available', 'stock', 'stock_status', 'ingredients', 
            'allergens', 'nutrition_info', 'created_at', 'modified_at'
        ]

    def get_image_url(self, obj):
        try:
            if obj.image:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(obj.image.url)
        except Exception as e:
            logger.warning(f"Error getting image URL for product {obj.id}: {str(e)}")
        return None

    def get_images(self, obj):
        request = self.context.get('request')
        if not request:
            return []
            
        images = []
        try:
            # Add main image if it exists
            if obj.image:
                images.append(request.build_absolute_uri(obj.image.url))
        except Exception as e:
            logger.warning(f"Error getting images for product {obj.id}: {str(e)}")
            
        return images

    def get_stock_status(self, obj):
        if not obj.available:
            return "Out of Stock"
        if obj.stock > 5:
            return "In Stock"
        return f"Only {obj.stock} left"

    def get_formatted_price(self, obj):
        if obj.price is None:
            return "0.00"
        return "{:.2f}".format(float(obj.price))

    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        # Add debug information using logger
        logger.debug(f"Serializing product {instance.id}:")
        logger.debug(f"- Image URL: {data.get('image_url')}")
        logger.debug(f"- Category: {data.get('category')}")
        logger.debug(f"- Ingredients: {data.get('ingredients')}")
        logger.debug(f"- Allergens: {data.get('allergens')}")
        logger.debug(f"- Nutrition: {data.get('nutrition_info')}")
        
        return data

class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating products."""
    nutrition_info = NutritionInfoCreateUpdateSerializer(required=False)
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Ingredient.objects.all(),
        required=False
    )

    class Meta:
        model = Product
        fields = [
            'name', 'slug', 'description', 'category',
            'price', 'stock', 'image', 'ingredients',
            'nutrition_info', 'is_vegan', 'is_vegetarian',
            'is_gluten_free', 'status', 'available'
        ]

    def create(self, validated_data):
        nutrition_data = validated_data.pop('nutrition_info', None)
        ingredients_data = validated_data.pop('ingredients', [])
        
        product = Product.objects.create(**validated_data)
        
        if nutrition_data:
            NutritionInfo.objects.create(product=product, **nutrition_data)
        
        if ingredients_data:
            product.ingredients.set(ingredients_data)
        
        return product

    def update(self, instance, validated_data):
        nutrition_data = validated_data.pop('nutrition_info', None)
        ingredients_data = validated_data.pop('ingredients', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if nutrition_data:
            if hasattr(instance, 'nutrition_info'):
                for attr, value in nutrition_data.items():
                    setattr(instance.nutrition_info, attr, value)
                instance.nutrition_info.save()
            else:
                NutritionInfo.objects.create(product=instance, **nutrition_data)
        
        if ingredients_data is not None:
            instance.ingredients.set(ingredients_data)
        
        instance.save()
        return instance

class CategoryCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating categories."""
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'image', 'is_active', 'order']

class IngredientCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating ingredients."""
    allergens = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=AllergenInfo.objects.all(),
        required=False
    )

    class Meta:
        model = Ingredient
        fields = ['name', 'description', 'allergens', 'is_active']

class AllergenCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating allergens."""
    class Meta:
        model = AllergenInfo
        fields = ['name', 'description', 'icon']

class NutritionAnalysisSerializer(serializers.Serializer):
    """Serializer for nutrition analysis results."""
    statistics = serializers.DictField(
        child=serializers.DictField(
            child=serializers.DecimalField(max_digits=10, decimal_places=2)
        )
    )
    distributions = serializers.DictField(
        child=serializers.DictField(
            child=serializers.ListField(child=serializers.FloatField())
        )
    )
    trends = serializers.DictField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )

class NutritionDetailSerializer(serializers.Serializer):
    """Serializer for detailed nutrition information including daily values."""
    nutrition_values = serializers.DictField(
        child=serializers.DecimalField(max_digits=10, decimal_places=2)
    )
    per_weight = serializers.IntegerField()
    daily_percentages = serializers.DictField(
        child=serializers.DecimalField(max_digits=5, decimal_places=1),
        required=False
    )
    weight_based = serializers.DictField(
        child=serializers.DictField(
            child=serializers.DecimalField(max_digits=10, decimal_places=2)
        ),
        required=False
    )

class SimilarProductSerializer(serializers.Serializer):
    """Serializer for similar product results."""
    product = ProductSerializer()
    similarity_score = serializers.DecimalField(max_digits=5, decimal_places=2)
    differences = serializers.DictField(
        child=serializers.DictField(
            child=serializers.DecimalField(max_digits=10, decimal_places=2)
        )
    )
    daily_values = serializers.DictField(
        child=serializers.DecimalField(max_digits=5, decimal_places=1),
        required=False
    )
