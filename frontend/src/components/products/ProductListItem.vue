<template>
  <div class="card flex bg-[rgba(255,255,255,0.03)] backdrop-blur-[8px] border border-white/10 
              hover:border-red-500/30 hover:shadow-red-500/10 transition-all duration-300
              rounded-lg overflow-hidden">
    <!-- Product Image -->
    <div class="w-48 flex-shrink-0">
      <div class="relative h-full">
        <img
          :src="getImageUrl(product)"
          :alt="product.name"
          @error="handleImageError"
          class="w-full h-full object-cover"
        >
        <!-- Badges -->
        <div class="absolute top-2 left-2 flex flex-col gap-1">
          <span
            v-if="product.isNew"
            class="bg-red-500/80 backdrop-blur-sm text-white text-xs px-2 py-1 rounded"
          >
            New
          </span>
          <span
            v-if="!product.available"
            class="bg-red-500/80 backdrop-blur-sm text-white text-xs px-2 py-1 rounded"
          >
            Out of Stock
          </span>
        </div>
      </div>
    </div>

    <!-- Product Info -->
    <div class="flex-grow p-4 flex flex-col bg-[rgba(255,255,255,0.02)] backdrop-blur-[5px]">
      <div class="flex-grow">
        <!-- Category -->
        <div class="text-sm text-gray-400 mb-1">
          {{ product.category.name }}
        </div>

        <!-- Name -->
        <h3 class="text-lg font-semibold mb-2 text-white hover:text-red-500 transition-colors">
          <router-link :to="{ name: 'product-detail', params: { id: product.id }}">
            {{ product.name }}
          </router-link>
        </h3>

        <!-- Description -->
        <p class="text-gray-300 text-sm mb-4">
          {{ product.description }}
        </p>

        <!-- Dietary Info -->
        <div class="flex gap-2 mb-4">
          <span
            v-if="product.isVegan"
            class="text-xs px-2 py-1 bg-green-100 text-green-800 rounded-full"
          >
            Vegan
          </span>
          <span
            v-if="product.isVegetarian"
            class="text-xs px-2 py-1 bg-green-100 text-green-800 rounded-full"
          >
            Vegetarian
          </span>
          <span
            v-if="product.isGlutenFree"
            class="text-xs px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full"
          >
            Gluten Free
          </span>
        </div>
      </div>

      <!-- Price and Actions -->
      <div class="flex items-center justify-between mt-4">
        <div class="flex flex-col">
          <span class="text-2xl font-bold text-amber-500" v-if="product.price">
            ${{ formatPrice(product.price) }}
          </span>
          <span
            v-if="product.old_price || product.oldPrice"
            class="text-sm text-gray-400"
          >
            ${{ formatPrice(product.old_price || product.oldPrice || 0) }} each
          </span>
        </div>

        <div class="flex items-center gap-2">
          <button
            v-if="product.available && !isInCart"
            @click="addToCart(product)"
            class="px-4 py-2 rounded-lg text-white font-medium
                  bg-gradient-to-r from-amber-500/90 to-amber-600/90
                  hover:from-amber-500 hover:to-amber-600
                  transform hover:-translate-y-0.5 transition-all duration-300
                  shadow-lg hover:shadow-amber-500/25">
            Add to Cart
          </button>
          <button
            v-if="product.available && isInCart"
            @click="removeFromCart(product)"
            class="px-4 py-2 rounded-lg text-white font-medium
                  bg-gradient-to-r from-red-500/90 to-red-600/90
                  hover:from-red-500 hover:to-red-600
                  transform hover:-translate-y-0.5 transition-all duration-300
                  shadow-lg hover:shadow-red-500/25">
            Remove
          </button>
          <button
            v-if="!product.available"
            disabled
            class="px-4 py-2 rounded-lg text-gray-400 font-medium
                  bg-[rgba(255,255,255,0.03)]
                  cursor-not-allowed opacity-50">
            Out of Stock
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Quick View Modal -->
  <QuickViewModal
    v-if="showQuickView"
    :product="product"
    @close="showQuickView = false"
    @add-to-cart="addToCart(product)"
  />
</template>

<script setup>
import { ref, computed } from 'vue'
import QuickViewModal from './QuickViewModal.vue'
import { useCartStore } from '@/stores/cartStore'
import { storeToRefs } from 'pinia'

const cartStore = useCartStore()
const { items } = storeToRefs(cartStore)
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const defaultImage = ref('/assets/images/placeholder.jpg')

const props = defineProps({
  product: {
    type: Object,
    required: true
  }
})

const isInCart = computed(() => {
  return items.value.some(item => 
    String(item.product.id) === String(props.product.id)
  )
})

const addToCart = async (product) => {
  try {
    await cartStore.addItem(product.id)
    cartStore.showDropdown() // Show the cart dropdown after adding
  } catch (error) {
    console.error('Failed to add item to cart:', error)
  }
}

const removeFromCart = async (product) => {
  try {
    await cartStore.removeItem(product.id)
  } catch (error) {
    console.error('Failed to remove item from cart:', error)
  }
}

// State
const showQuickView = ref(false)

// Methods
const formatPrice = (price) => {
  if (!price) return '0.00'
  return parseFloat(price).toFixed(2)
}

const getImageUrl = (product) => {
  if (!product) {
    console.log('Debug - No product provided')
    return defaultImage.value
  }

  console.log('Debug - Processing image for product:', {
    id: product.id,
    image: product.image,
    defaultImage: defaultImage.value
  })
  
  // Use the image URL directly if it's already absolute
  if (product.image?.startsWith('http')) {
    return product.image
  }
  
  // If we have an image path, construct the full URL
  if (product.image) {
    const fullUrl = `${API_URL}${product.image.startsWith('/') ? '' : '/'}${product.image}`
    console.log('Debug - Constructed image URL:', fullUrl)
    return fullUrl
  }
  
  console.log('Debug - Using default image')
  return defaultImage.value
}

const handleImageError = (event) => {
  console.error('Image failed to load:', {
    src: event.target.src,
    product: props.product?.id,
    fallback: defaultImage.value
  })
  event.target.src = defaultImage.value
}
</script>

<style scoped>
.card {
  background: rgba(255, 255, 255, 0.03) !important;
  backdrop-filter: blur(8px) !important;
  -webkit-backdrop-filter: blur(8px) !important;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.card:hover {
  background: rgba(255, 255, 255, 0.05) !important;
  border-color: rgba(239, 68, 68, 0.3);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.1),
    0 4px 8px rgba(239, 68, 68, 0.2);
  transform: translateY(-2px);
}

.flex-grow {
  background: rgba(255, 255, 255, 0.02) !important;
  backdrop-filter: blur(5px) !important;
  -webkit-backdrop-filter: blur(5px) !important;
  border: none !important;
}

/* Add fallback for browsers that don't support backdrop-filter */
@supports not (backdrop-filter: blur(8px)) {
  .card,
  .flex-grow {
    background: rgba(23, 23, 23, 0.95) !important;
  }
}

/* Override any other background colors that might be applied */
:deep(.product-info),
:deep(.card-body) {
  background: transparent !important;
}
</style>
