<template>
  <div class="container py-8">
    <!-- Loading State -->
    <div v-if="productStore.loading" class="grid place-items-center h-96">
      <div class="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="productStore.error" class="text-center py-12">
      <i class="fas fa-exclamation-circle text-4xl text-red-500 mb-4"></i>
      <p class="text-lg text-gray-600">{{ productStore.error }}</p>
      <button @click="loadProduct" class="btn btn-primary mt-4">
        Try Again
      </button>
    </div>

    <!-- Product Details -->
    <div v-else-if="product" class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <!-- Product Images -->
      <div class="space-y-4">
        <!-- Main Image -->
        <div class="aspect-w-1 aspect-h-1 bg-gray-100 rounded-lg overflow-hidden">
          <img
            :src="selectedImage || product.image"
            :alt="product.name"
            class="w-full h-full object-cover"
          >
        </div>
        <!-- Thumbnail Images -->
        <div class="grid grid-cols-4 gap-4">
          <button
            v-for="(image, index) in product.images"
            :key="index"
            @click="selectedImage = image"
            class="aspect-w-1 aspect-h-1 rounded-lg overflow-hidden"
            :class="{ 'ring-2 ring-primary-500': selectedImage === image }"
          >
            <img
              :src="image"
              :alt="`${product.name} thumbnail ${index + 1}`"
              class="w-full h-full object-cover"
            >
          </button>
        </div>
      </div>

      <!-- Product Info -->
      <div class="space-y-6">
        <!-- Breadcrumbs -->
        <nav class="flex items-center space-x-2 text-sm text-gray-500">
          <router-link to="/" class="hover:text-primary-600">Home</router-link>
          <span>/</span>
          <router-link to="/products" class="hover:text-primary-600">Products</router-link>
          <span>/</span>
          <router-link
            :to="{ name: 'category', params: { slug: product.category.slug }}"
            class="hover:text-primary-600"
          >
            {{ product.category.name }}
          </router-link>
          <span>/</span>
          <span class="text-gray-900">{{ product.name }}</span>
        </nav>

        <!-- Title and Price -->
        <div>
          <h1 class="text-3xl font-bold text-gray-900 mb-2">
            {{ product.name }}
          </h1>
          <div class="flex items-center gap-4">
            <span class="text-3xl font-bold text-gray-900">
              ${{ formatPrice(product.price) }}
            </span>
            <span
              v-if="product.oldPrice"
              class="text-xl text-gray-500 line-through"
            >
              ${{ formatPrice(product.oldPrice) }}
            </span>
          </div>
        </div>

        <!-- Description -->
        <div>
          <h2 class="text-lg font-semibold mb-2">Description</h2>
          <p class="text-gray-600">{{ product.description }}</p>
        </div>

        <!-- Dietary Information -->
        <div>
          <h2 class="text-lg font-semibold mb-2">Dietary Information</h2>
          <div class="flex flex-wrap gap-2">
            <span
              v-if="product.isVegan"
              class="badge badge-green"
            >
              <i class="fas fa-leaf mr-1"></i>
              Vegan
            </span>
            <span
              v-if="product.isVegetarian"
              class="badge badge-green"
            >
              <i class="fas fa-seedling mr-1"></i>
              Vegetarian
            </span>
            <span
              v-if="product.isGlutenFree"
              class="badge badge-yellow"
            >
              <i class="fas fa-wheat-alt mr-1"></i>
              Gluten Free
            </span>
          </div>
        </div>

        <!-- Ingredients -->
        <div>
          <h2 class="text-lg font-semibold mb-2">Ingredients</h2>
          <ul class="list-disc list-inside text-gray-600">
            <li v-for="ingredient in product.ingredients" :key="ingredient.id">
              {{ ingredient.name }}
            </li>
          </ul>
        </div>

        <!-- Allergens -->
        <div>
          <h2 class="text-lg font-semibold mb-2">Allergens</h2>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="allergen in product.allergens"
              :key="allergen.id"
              class="badge badge-red"
            >
              {{ allergen.name }}
            </span>
          </div>
        </div>

        <!-- Add to Cart -->
        <div class="border-t pt-6">
          <div class="flex items-center gap-4 mb-4">
            <div class="flex items-center border rounded-lg">
              <button
                @click="decrementQuantity"
                class="px-3 py-2 hover:bg-gray-100"
                :disabled="quantity <= 1"
              >
                <i class="fas fa-minus"></i>
              </button>
              <input
                type="number"
                v-model.number="quantity"
                min="1"
                class="w-16 text-center border-x py-2"
              >
              <button
                @click="incrementQuantity"
                class="px-3 py-2 hover:bg-gray-100"
              >
                <i class="fas fa-plus"></i>
              </button>
            </div>
            <button
              @click="addToCart"
              :disabled="!product.available || loading"
              class="btn btn-primary flex-grow"
              :class="{ 'opacity-50 cursor-not-allowed': !product.available || loading }"
            >
              <i class="fas fa-shopping-cart mr-2"></i>
              {{ loading ? 'Adding...' : 'Add to Cart' }}
            </button>
          </div>
          <p
            v-if="!product.available"
            class="text-red-600 text-sm"
          >
            This product is currently out of stock
          </p>
        </div>

        <!-- Additional Information -->
        <div class="border-t pt-6">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <h3 class="font-semibold mb-1">Weight</h3>
              <p class="text-gray-600">{{ product.weight }}g</p>
            </div>
            <div>
              <h3 class="font-semibold mb-1">Storage</h3>
              <p class="text-gray-600">{{ product.storage }}</p>
            </div>
            <div>
              <h3 class="font-semibold mb-1">Shelf Life</h3>
              <p class="text-gray-600">{{ product.shelfLife }}</p>
            </div>
            <div>
              <h3 class="font-semibold mb-1">SKU</h3>
              <p class="text-gray-600">{{ product.sku }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Related Products -->
    <div v-if="product" class="mt-16">
      <h2 class="text-2xl font-bold mb-6">Related Products</h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <ProductCard
          v-for="relatedProduct in relatedProducts"
          :key="relatedProduct.id"
          :product="relatedProduct"
          @add-to-cart="addToCart"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useProductStore } from '@/stores/productStore'
import { useCartStore } from '@/stores/cartStore'
import ProductCard from './ProductCard.vue'

const route = useRoute()
const productStore = useProductStore()
const cartStore = useCartStore()

// State
const quantity = ref(1)
const selectedImage = ref(null)
const loading = ref(false)

// Computed
const product = computed(() => productStore.product)

const relatedProducts = computed(() => {
  if (!product.value) return []
  return productStore.products.filter(p => 
    p.category.id === product.value.category.id && 
    p.id !== product.value.id
  ).slice(0, 4)
})

// Methods
const loadProduct = async () => {
  try {
    await productStore.fetchProductById(route.params.id)
  } catch (error) {
    console.error('Error loading product:', error)
  }
}

const formatPrice = (price) => {
  return price.toFixed(2)
}

const incrementQuantity = () => {
  quantity.value++
}

const decrementQuantity = () => {
  if (quantity.value > 1) {
    quantity.value--
  }
}

const addToCart = async () => {
  if (!product.value?.available) return

  try {
    loading.value = true
    await cartStore.addToCart(product.value, quantity.value)
    // You could add a toast notification here
  } catch (error) {
    console.error('Failed to add to cart:', error)
    // Handle error (show error toast, etc.)
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadProduct()
  // Load current cart
  cartStore.fetchCart()
})
</script>

<style scoped>
.badge {
  @apply px-2 py-1 rounded-full text-sm font-medium;
}

.badge-green {
  @apply bg-green-100 text-green-800;
}

.badge-yellow {
  @apply bg-yellow-100 text-yellow-800;
}

.badge-red {
  @apply bg-red-100 text-red-800;
}

.aspect-w-1 {
  position: relative;
  padding-bottom: 100%;
}

.aspect-w-1 > * {
  position: absolute;
  height: 100%;
  width: 100%;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
}
</style>
