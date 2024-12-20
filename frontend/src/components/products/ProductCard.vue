<template>
  <div class="product-card hover:scale-[1.02] relative">
    <!-- Message notification -->
    <div v-if="message" 
         :class="[
           'notification absolute top-2 right-2 p-2 rounded shadow-lg z-50',
           messageType === 'error' ? 'bg-red-500 text-white' : 'bg-green-500 text-white'
         ]"
    >
      {{ message }}
    </div>

    <div class="product-image-wrapper">
      <div class="product-image">
        <img :src="product.image" :alt="product.name" @error="handleImageError">
        <div v-if="product.stock <= 5 && product.stock > 0" class="stock-badge low-stock">
          Only {{ product.stock }} left!
        </div>
        <div v-else-if="product.stock === 0" class="stock-badge out-of-stock">
          Out of Stock
        </div>
      </div>
    </div>
    
    <div class="product-info">
      <h3 class="product-name">{{ product.name }}</h3>
      <p class="product-price">${{ formatPrice(product.price) }}</p>
      
      <!-- Cart Controls -->
      <div class="cart-controls" v-if="product.stock > 0">
        <template v-if="!isInCart">
          <button 
            class="add-to-cart-btn"
            :disabled="loading"
            @click="addToCart"
          >
            <i class="fas fa-cart-plus mr-2"></i>
            {{ loading ? 'Adding...' : 'Add to Cart' }}
          </button>
        </template>
        <template v-else>
          <div class="quantity-controls">
            <button 
              class="quantity-btn"
              :disabled="loading || cartItem.quantity <= 1"
              @click="updateQuantity(cartItem.quantity - 1)"
            >
              <i class="fas fa-minus"></i>
            </button>
            
            <span class="quantity">{{ cartItem.quantity }}</span>
            
            <button 
              class="quantity-btn"
              :disabled="loading || cartItem.quantity >= product.stock"
              @click="updateQuantity(cartItem.quantity + 1)"
            >
              <i class="fas fa-plus"></i>
            </button>
          </div>
          <button 
            class="remove-btn"
            :disabled="loading"
            @click="removeFromCart"
          >
            <i class="fas fa-trash"></i>
          </button>
        </template>
      </div>
      <div v-else class="out-of-stock-message">
        Out of Stock
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useCartStore } from '@/stores/cartStore'
import { storeToRefs } from 'pinia'

const props = defineProps({
  product: {
    type: Object,
    required: true
  }
})

const cartStore = useCartStore()
const { items } = storeToRefs(cartStore)
const loading = ref(false)
const message = ref('')
const messageType = ref('')

const cartItem = computed(() => 
  items.value.find(item => item.product.id === props.product.id)
)

const isInCart = computed(() => !!cartItem.value)

const handleImageError = (e) => {
  e.target.src = '/images/placeholder.png' // Fallback image
}

const formatPrice = (price) => {
  return Number(price).toFixed(2)
}

const showMessage = (text, type = 'success') => {
  message.value = text
  messageType.value = type
  setTimeout(() => {
    message.value = ''
    messageType.value = ''
  }, 3000)
}

async function addToCart() {
  if (loading.value) return
  loading.value = true
  try {
    await cartStore.addItem(props.product.id, 1)
    showMessage('Product added to cart')
  } catch (error) {
    showMessage(error || 'Failed to add item to cart', 'error')
  } finally {
    loading.value = false
  }
}

async function updateQuantity(newQuantity) {
  if (loading.value) return
  loading.value = true
  try {
    await cartStore.updateItemQuantity(props.product.id, newQuantity)
    showMessage('Cart updated')
  } catch (error) {
    showMessage(error || 'Failed to update quantity', 'error')
  } finally {
    loading.value = false
  }
}

async function removeFromCart() {
  if (loading.value) return
  loading.value = true
  try {
    await cartStore.removeItem(props.product.id)
    showMessage('Product removed from cart')
  } catch (error) {
    showMessage(error || 'Failed to remove item', 'error')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.product-card {
  @apply bg-white rounded-lg shadow-md overflow-hidden transition-transform duration-300;
}

.product-image-wrapper {
  @apply relative w-full pb-[100%] overflow-hidden;
}

.product-image {
  @apply absolute inset-0 w-full h-full;
}

.product-image img {
  @apply w-full h-full object-cover;
}

.stock-badge {
  @apply absolute top-2 right-2 px-2 py-1 rounded text-sm font-medium;
}

.low-stock {
  @apply bg-yellow-500 text-white;
}

.out-of-stock {
  @apply bg-red-500 text-white;
}

.product-info {
  @apply p-4;
}

.product-name {
  @apply text-lg font-semibold text-gray-800 mb-2 line-clamp-2;
}

.product-price {
  @apply text-xl font-bold text-blue-600 mb-4;
}

.cart-controls {
  @apply flex items-center justify-between;
}

.add-to-cart-btn {
  @apply w-full bg-blue-600 text-white px-4 py-2 rounded-lg
         hover:bg-blue-700 transition-colors duration-200
         disabled:opacity-50 disabled:cursor-not-allowed
         flex items-center justify-center;
}

.quantity-controls {
  @apply flex items-center space-x-3;
}

.quantity-btn {
  @apply w-8 h-8 flex items-center justify-center rounded-full
         bg-gray-100 text-gray-600 hover:bg-gray-200
         disabled:opacity-50 disabled:cursor-not-allowed
         transition-colors duration-200;
}

.quantity {
  @apply text-lg font-medium text-gray-800 min-w-[24px] text-center;
}

.remove-btn {
  @apply text-red-500 hover:text-red-600 transition-colors duration-200
         disabled:opacity-50 disabled:cursor-not-allowed
         w-8 h-8 flex items-center justify-center;
}

.out-of-stock-message {
  @apply text-red-500 font-medium text-center mt-2;
}

.notification {
  @apply text-sm font-medium transition-all duration-300 transform;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
