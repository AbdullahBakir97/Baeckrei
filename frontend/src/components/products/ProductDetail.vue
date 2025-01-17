<template>
  <div class="container py-8">
    <!-- Loading State -->
    <div v-if="productStore.loading" class="grid place-items-center h-96">
      <div class="text-6xl text-primary-600">
        <font-awesome-icon icon="spinner" class="animate-spin" />
      </div>
      <p class="mt-4 text-gray-400">Loading product details...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="productStore.error" class="text-center py-12">
      <font-awesome-icon icon="circle-xmark" class="text-4xl text-red-500 mb-4" />
      <p class="text-lg text-gray-600">{{ productStore.error }}</p>
      <button @click="loadProduct" class="btn btn-primary mt-4">
        <font-awesome-icon icon="rotate" class="mr-2" />
        Try Again
      </button>
    </div>

    <!-- Product Details -->
    <div v-else-if="product" class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <!-- Product Images -->
      <div class="space-y-4 bg-[rgba(23,23,23,0.7)] backdrop-blur-[10px] border border-white/10 
                  hover:border-white/20 hover:shadow-red-500/10 transition-all duration-300 p-4 rounded-lg">
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
      <div class="space-y-6 bg-[rgba(23,23,23,0.7)] backdrop-blur-[10px] border border-white/10 
                  hover:border-white/20 hover:shadow-red-500/10 transition-all duration-300 p-6 rounded-lg">
        <!-- Breadcrumbs -->
        <nav class="flex items-center space-x-2 text-sm text-gray-400">
          <router-link to="/" class="hover:text-red-500">Home</router-link>
          <span>/</span>
          <router-link to="/products" class="hover:text-red-500">Products</router-link>
          <span>/</span>
          <router-link
            v-if="product?.category?.slug"
            :to="{ name: 'category', params: { slug: product.category.slug }}"
            class="hover:text-red-500"
          >
            {{ product?.category?.name }}
          </router-link>
          <span v-else class="text-gray-400">Uncategorized</span>
          <span>/</span>
          <span class="text-gray-900">{{ product.name }}</span>
        </nav>

        <!-- Title and Price -->
        <div>
          <h1 class="text-3xl font-bold bg-gradient-to-r from-amber-400 to-amber-600 
                     bg-clip-text text-transparent mb-2">
            {{ product.name }}
          </h1>
          <div class="flex items-center gap-4">
            <span class="text-3xl font-bold text-transparent bg-clip-text 
                         bg-gradient-to-r from-amber-400 to-amber-600">
              {{ formatPrice(product.price) }} €
            </span>
          </div>
        </div>

        <!-- Stock Status -->
        <div class="flex items-center gap-2">
          <span :class="[
            'px-3 py-1 rounded-full text-sm font-medium',
            product.stock > 5 ? 'bg-green-500/20 text-green-300' :
            product.stock > 0 ? 'bg-yellow-500/20 text-yellow-300' :
            'bg-red-500/20 text-red-300'
          ]">
            {{ product.stock > 5 ? 'In Stock' :
               product.stock > 0 ? `Only ${product.stock} left` :
               'Out of Stock' }}
          </span>
        </div>

        <!-- Description -->
        <div>
          <h2 class="text-lg font-semibold mb-2 text-gray-200">Description</h2>
          <p class="text-gray-400">{{ product.description }}</p>
        </div>

        <!-- Dietary Information -->
        <div>
          <h2 class="text-lg font-semibold mb-2 text-gray-200">Dietary Information</h2>
          <div class="flex flex-wrap gap-2">
            <span v-if="product.is_vegan" 
                  class="text-sm px-2 py-1 rounded-full bg-green-500/20 text-green-300">
              <font-awesome-icon icon="leaf" class="mr-1" />
              Vegan
            </span>
            <span v-if="product.is_vegetarian"
                  class="text-sm px-2 py-1 rounded-full bg-green-500/20 text-green-300">
              <font-awesome-icon icon="seedling" class="mr-1" />
              Vegetarian
            </span>
            <span v-if="product.is_gluten_free"
                  class="text-sm px-2 py-1 rounded-full bg-yellow-500/20 text-yellow-300">
              <font-awesome-icon icon="wheat-alt" class="mr-1" />
              Gluten Free
            </span>
          </div>
        </div>

        <!-- Ingredients -->
        <div>
          <h2 class="text-lg font-semibold mb-2 text-gray-200">Ingredients</h2>
          <ul class="space-y-1">
            <li v-for="ingredient in product.ingredients" 
                :key="ingredient.id"
                class="text-gray-400 flex items-center gap-2">
              <font-awesome-icon icon="utensils" class="text-xs text-amber-500" />
              {{ ingredient.name }}
            </li>
          </ul>
        </div>

        <!-- Allergens -->
        <div v-if="product.allergens?.length">
          <h2 class="text-lg font-semibold mb-2 text-gray-200">Allergens</h2>
          <div class="flex flex-wrap gap-2">
            <span v-for="allergen in product.allergens"
                  :key="allergen.id"
                  class="text-sm px-2 py-1 rounded-full bg-red-500/20 text-red-300">
              <font-awesome-icon icon="exclamation-triangle" class="mr-1" />
              {{ allergen.name }}
            </span>
          </div>
        </div>

        <!-- Nutrition Information -->
        <div v-if="product.nutrition_info">
          <h2 class="text-lg font-semibold mb-2 text-gray-200">Nutrition Information</h2>
          <div class="grid grid-cols-2 gap-4">
            <div class="bg-[rgba(255,255,255,0.02)] p-3 rounded-lg">
              <div class="flex items-center gap-2 mb-1">
                <font-awesome-icon icon="bolt" class="text-amber-400" />
                <p class="text-sm text-gray-400">Calories</p>
              </div>
              <p class="text-lg font-semibold text-amber-400">
                {{ product.nutrition_info.calories }} kcal
              </p>
            </div>
            <div class="bg-[rgba(255,255,255,0.02)] p-3 rounded-lg">
              <div class="flex items-center gap-2 mb-1">
                <font-awesome-icon icon="dumbbell" class="text-amber-400" />
                <p class="text-sm text-gray-400">Proteins</p>
              </div>
              <p class="text-lg font-semibold text-amber-400">
                {{ product.nutrition_info.proteins }}g
              </p>
            </div>
            <div class="bg-[rgba(255,255,255,0.02)] p-3 rounded-lg">
              <div class="flex items-center gap-2 mb-1">
                <font-awesome-icon icon="bread-slice" class="text-amber-400" />
                <p class="text-sm text-gray-400">Carbohydrates</p>
              </div>
              <p class="text-lg font-semibold text-amber-400">
                {{ product.nutrition_info.carbohydrates }}g
              </p>
            </div>
            <div class="bg-[rgba(255,255,255,0.02)] p-3 rounded-lg">
              <div class="flex items-center gap-2 mb-1">
                <font-awesome-icon icon="oil-can" class="text-amber-400" />
                <p class="text-sm text-gray-400">Fats</p>
              </div>
              <p class="text-lg font-semibold text-amber-400">
                {{ product.nutrition_info.fats }}g
              </p>
            </div>
          </div>
        </div>

        <!-- Add to Cart -->
        <div class="border-t border-white/10 pt-6">
          <div v-if="cartItem" class="flex items-center gap-4 mb-4">
            <QuantityControl
              :quantity="currentQuantity"
              :loading="loading"
              :product="product"
              :unit-price="Number(product?.price) || 0"
              :total-price="(Number(product?.price) || 0) * currentQuantity"
              @update-quantity="handleQuantityUpdate"
              @remove-item="handleRemoveItem"
              :disabled="!product?.available"
            />
          </div>
          <div v-else class="flex items-center gap-4 mb-4">
            <div class="flex items-center gap-2">
              <button 
                @click="() => handleQuantityUpdate(null, 1)"
                class="btn btn-primary flex items-center gap-2"
                :disabled="!product?.available || loading"
              >
                <font-awesome-icon icon="cart-plus" />
                Add to Cart
                <font-awesome-icon v-if="loading" icon="spinner" class="animate-spin" />
              </button>
            </div>
          </div>
          <p v-if="!product?.available"
             class="text-red-400 text-sm">
            This product is currently out of stock
          </p>
        </div>
      </div>
    </div>

    <!-- Related Products -->
    <div v-if="product" class="mt-16 bg-[rgba(23,23,23,0.7)] backdrop-blur-[10px] border border-white/10 
                             hover:border-white/20 hover:shadow-red-500/10 transition-all duration-300 p-6 rounded-lg">
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
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProductStore } from '@/stores/productStore'
import { useCartStore } from '@/stores/cartStore'
import { useToast } from '@/composables/useToast'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import ProductCard from './ProductCard.vue'
import QuantityControl from '../cart/QuantityControl.vue'

const route = useRoute()
const router = useRouter()
const productStore = useProductStore()
const cartStore = useCartStore()
const { showToast } = useToast()

// State
const quantity = ref(1)
const selectedImage = ref(null)
const loading = ref(false)

// Computed
const product = computed(() => productStore.product)
const cartItem = computed(() => 
  cartStore.items.find(item => item.product.id === product.value?.id)
)

const currentQuantity = computed(() => cartItem.value?.quantity || quantity.value)

const relatedProducts = computed(() => {
  if (!product.value) return []
  return productStore.products.filter(p => 
    p.category?.id === product.value.category?.id && 
    p.id !== product.value.id
  ).slice(0, 4)
})

// Methods
const loadProduct = async () => {
  if (!route.params.id) {
    showToast('Invalid product ID', 'error')
    router.push('/products')
    return
  }

  try {
    await productStore.fetchProductById(route.params.id)
    if (!productStore.product) {
      showToast('Product not found', 'error')
      router.push('/products')
    }
    // Update quantity if item is in cart
    const item = cartStore.items.find(item => item.product.id === route.params.id)
    if (item) {
      quantity.value = item.quantity
    } else {
      quantity.value = 1
    }
  } catch (error) {
    console.error('Error loading product:', error)
    showToast('Failed to load product details', 'error')
    router.push('/products')
  }
}

const formatPrice = (price) => {
  return Number(price).toFixed(2)
}

const handleQuantityUpdate = async (_, newQuantity) => {
  if (!product.value?.id) return
  
  try {
    loading.value = true
    if (cartItem.value) {
      await cartStore.updateQuantity(product.value.id, newQuantity)
    } else {
      await cartStore.addItem(product.value.id, newQuantity)
    }
    quantity.value = newQuantity
    showToast('Cart updated successfully')
  } catch (error) {
    console.error('Failed to update cart:', error)
    showToast('Failed to update cart', 'error')
  } finally {
    loading.value = false
  }
}

const handleRemoveItem = async () => {
  if (!product.value?.id) return
  
  try {
    loading.value = true
    await cartStore.removeItem(product.value.id)
    quantity.value = 1
    showToast('Item removed from cart')
  } catch (error) {
    console.error('Failed to remove item:', error)
    showToast('Failed to remove item from cart', 'error')
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadProduct()
  cartStore.fetchCart()
})

// Watch for route changes
watch(
  () => route.params.id,
  (newId) => {
    if (newId) {
      loadProduct()
    }
  }
)
</script>

<style scoped>
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
