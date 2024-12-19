from django.db import models

class ProductQuerySet(models.QuerySet):
    def available(self):
        """Filter available products."""
        return self.filter(available=True, status='active')

    def by_category(self, category_name):
        """Filter products by category."""
        return self.filter(category__name__iexact=category_name)

    def by_ingredient(self, ingredient_name):
        """Filter products containing a specific ingredient."""
        return self.filter(ingredients__name__iexact=ingredient_name)

    def by_allergen(self, allergen_name):
        """Filter products containing a specific allergen in their ingredients."""
        return self.filter(ingredients__allergens__name__iexact=allergen_name).distinct()

    def featured(self):
        """Get featured products."""
        return self.available().order_by('-created_at')[:6]

    def dietary_preferences(self, vegan=False, vegetarian=False, gluten_free=False):
        """Filter products by dietary preferences."""
        queryset = self.available()
        if vegan:
            queryset = queryset.filter(is_vegan=True)
        if vegetarian:
            queryset = queryset.filter(is_vegetarian=True)
        if gluten_free:
            queryset = queryset.filter(is_gluten_free=True)
        return queryset

class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def available(self):
        """Get all available products."""
        return self.get_queryset().available()

    def by_category(self, category_name):
        """Get products by category name."""
        return self.get_queryset().by_category(category_name)

    def by_ingredient(self, ingredient_name):
        """Get products containing a specific ingredient."""
        return self.get_queryset().by_ingredient(ingredient_name)

    def by_allergen(self, allergen_name):
        """Get products containing a specific allergen."""
        return self.get_queryset().by_allergen(allergen_name)

    def featured(self):
        """Get featured products."""
        return self.get_queryset().featured()

    def dietary_preferences(self, vegan=False, vegetarian=False, gluten_free=False):
        """Get products filtered by dietary preferences."""
        return self.get_queryset().dietary_preferences(vegan, vegetarian, gluten_free)