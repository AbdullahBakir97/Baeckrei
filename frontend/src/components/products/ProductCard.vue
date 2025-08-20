<template>
  <div class="product-card group" :style="{ backgroundColor: cardColor }">
    <!-- Message notification -->
    <div v-if="message" 
         :class="[
           'notification absolute top-2 right-2 p-2 rounded shadow-lg z-50',
           messageType === 'error' ? 'bg-red-500 text-white' : 'bg-green-500 text-white'
         ]"
    >
      {{ message }}
    </div>

    <!-- Strip design from vue-product-card -->
    <div class="strip-container">
      <div class="strip"></div>
      <div class="strip strip-2"></div>
      <div class="strip strip-3"></div>
    </div>

    <div class="relative">
      <!-- Quick Preview Button -->
      <button 
        @mouseenter="showQuickPreview = true"
        @mouseleave="showQuickPreview = false"
        class="quick-view-btn absolute top-2 left-2 p-2 rounded-full 
               bg-[rgba(255,255,255,0.02)] backdrop-blur-[8px] text-white
               hover:bg-[rgba(255,255,255,0.05)] border border-white/5
               hover:border-white/20 hover:shadow-amber-500/10
               transition-all duration-200 z-10 opacity-0 group-hover:opacity-100"
      >
        <font-awesome-icon icon="fa-solid fa-eye" />
      </button>

      <!-- Quick Preview Popup -->
      <Transition name="preview">
        <div v-if="showQuickPreview"
            @mouseenter="showQuickPreview = true"
            @mouseleave="showQuickPreview = false"
            class="absolute top-0 left-0 right-0 bottom-0 w-full h-full 
                   bg-[rgba(255,255,255,0.02)] backdrop-blur-[8px] rounded-lg 
                   border border-white/5 hover:border-white/20 hover:shadow-amber-500/10 
                   transition-all duration-300 z-50">
          <div class="relative w-full h-full p-4 flex flex-col bg-black/60">
            <div class="flex-1">
              <h3 class="text-lg font-bold mb-2 bg-gradient-to-r from-amber-400 
                        to-yellow-600 bg-clip-text text-transparent">
                {{ product.name }}
              </h3>
              <div class="flex justify-between items-center mb-3">
                <span class="product-price">
                  {{ formatPrice(product.price) }} €
                </span>
                <span :class="[
                  'text-sm px-2 py-1 rounded-full',
                  product.stock > 5 ? 'bg-green-500/20 text-green-300' :
                  product.stock > 0 ? 'bg-yellow-500/20 text-yellow-300' :
                  'bg-red-500/20 text-red-300'
                ]">
                  {{ product.stock > 5 ? 'In Stock' :
                     product.stock > 0 ? `Only ${product.stock} left` :
                     'Out of Stock' }}
                </span>
              </div>
              <p class="text-gray-300 text-sm mb-3">{{ product.description }}</p>
              <div class="flex gap-2 flex-wrap mb-3">
                <span v-if="product.is_vegan" 
                      class="text-xs px-2 py-1 rounded-full bg-green-500/20 text-green-300">
                  Vegan
                </span>
                <span v-if="product.is_vegetarian"
                      class="text-xs px-2 py-1 rounded-full bg-green-500/20 text-green-300">
                  Vegetarian
                </span>
                <span v-if="product.is_gluten_free"
                      class="text-xs px-2 py-1 rounded-full bg-yellow-500/20 text-yellow-300">
                  Gluten Free
                </span>
              </div>
            </div>
            <div class="flex gap-2 mt-auto">
              <button @click="showQuickView = true"
                      class="flex-1 py-1.5 px-3 rounded-lg bg-white/10 
                             hover:bg-white/20 text-white text-sm
                             transition-all duration-200">
                View Details
              </button>
              <ProductCardButtons
                :product="product"
                :cart-item="cartItem"
                :is-in-cart="isInCart"
                :loading="loading"
                @add-to-cart="addToCart"
                @update-quantity="updateQuantity"
                @remove-from-cart="removeFromCart"
                class="flex-1"
              />
            </div>
          </div>
        </div>
      </Transition>
    </div>

    <div class="product-image-wrapper">
      <div class="product-image">
        <img :src="product.image" :alt="product.name" @error="handleImageError">
        <div v-if="product.stock <= 5 && product.stock > 0" 
             class="stock-badge low-stock">
          Only {{ product.stock }} left!
        </div>
        <div v-else-if="product.stock === 0" 
             class="stock-badge out-of-stock">
          Out of Stock
        </div>
      </div>
    </div>
    
    <div class="product-info" :style="{ color: textColor }">
      <router-link 
        :to="{ name: 'product-detail', params: { id: product.id }}" 
        class="product-name hover:text-amber-400 transition-colors duration-200"
      >
        {{ product.name }}
      </router-link>
      <p class="product-price">{{ formatPrice(product.price) }} €</p>
      
      <!-- Cart Controls -->
      <div v-if="product.stock > 0 || isInCart">
        <ProductCardButtons
          :product="product"
          :cart-item="cartItem"
          :is-in-cart="isInCart"
          :loading="loading"
          @add-to-cart="addToCart"
          @update-quantity="updateQuantity"
          @remove-from-cart="removeFromCart"
        />
      </div>
      <div v-else class="out-of-stock-message" :style="{ color: textColor }">
        Out of Stock
      </div>
    </div>
  </div>
  <QuickViewModal
    v-if="showQuickView"
    :product="product"
    @close="showQuickView = false"
  />
</template>

<script setup>
import { ref, computed } from 'vue'
import { useCartStore } from '@/stores/cartStore'
import { useAuthStore } from '@/stores/authStore'
import { storeToRefs } from 'pinia'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { library } from '@fortawesome/fontawesome-svg-core'
import { faEye } from '@fortawesome/free-solid-svg-icons'
import { useToast } from '@/composables/useToast'
import QuickViewModal from './QuickViewModal.vue'
import ProductCardButtons from './ProductCardButtons.vue'

library.add(faEye)

const props = defineProps({
  product: {
    type: Object,
    required: true
  },
  cardColor: {
    type: String,
    default: '#313131'
  },
  stripColor: {
    type: String,
    default: '#35AFFB'
  },
  buttonColor: {
    type: String,
    default: '#35AFFB'
  },
  textColor: {
    type: String,
    default: '#ffffff'
  }
})

const emits = defineEmits(['addToCart'])

const cartStore = useCartStore()
const authStore = useAuthStore()
const { showToast } = useToast()
const loading = ref(false)
const message = ref('')
const messageType = ref('')
const showQuickView = ref(false)
const showQuickPreview = ref(false)
const { items } = storeToRefs(cartStore)

const isInCart = computed(() => {
  return cartStore.items.some(item => item.product.id === props.product.id)
})

const cartItem = computed(() => {
  return cartStore.items.find(item => item.product.id === props.product.id)
})

const handleImageError = (e) => {
  e.target.src = '/images/placeholder.png'
}

const formatPrice = (price) => {
  return Number(price).toFixed(2)
}

const updateQuantity = async (newQuantity) => {
  if (!newQuantity || newQuantity < 1) {
    message.value = 'Quantity must be at least 1'
    messageType.value = 'error'
    setTimeout(() => message.value = '', 3000)
    return
  }

  if (newQuantity > props.product.stock) {
    message.value = `Only ${props.product.stock} items available`
    messageType.value = 'error'
    setTimeout(() => message.value = '', 3000)
    return
  }

  try {
    loading.value = true
    await cartStore.updateQuantity(props.product.id, newQuantity)
    message.value = 'Cart updated'
    messageType.value = 'success'
  } catch (error) {
    message.value = error.response?.data?.detail || 'Failed to update cart'
    messageType.value = 'error'
  } finally {
    loading.value = false
    setTimeout(() => message.value = '', 3000)
  }
}

const addToCart = async () => {
  if (!props.product.available) {
    message.value = 'Product is not available'
    messageType.value = 'error'
    setTimeout(() => message.value = '', 3000)
    return
  }

  try {
    loading.value = true
    await cartStore.addItem(props.product.id)
    message.value = 'Added to cart successfully!'
    messageType.value = 'success'
    emits('addToCart')
  } catch (error) {
    message.value = error.response?.data?.detail || 'Failed to add to cart'
    messageType.value = 'error'
  } finally {
    loading.value = false
    setTimeout(() => message.value = '', 3000)
  }
}

const removeFromCart = async () => {
  try {
    loading.value = true
    await cartStore.removeItem(props.product.id)
    message.value = 'Removed from cart'
    messageType.value = 'success'
  } catch (error) {
    message.value = error.response?.data?.detail || 'Failed to remove from cart'
    messageType.value = 'error'
  } finally {
    loading.value = false
    setTimeout(() => message.value = '', 3000)
  }
}
</script>

<style scoped>
.product-card {
  @apply relative rounded-lg overflow-hidden;
  min-height: 400px;
  perspective: 2000px;
  transform-style: preserve-3d;
  background: rgba(255, 255, 255, 0.03) !important;
  backdrop-filter: blur(8px) !important;
  -webkit-backdrop-filter: blur(8px) !important;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06),
    0 0 20px rgba(245, 158, 11, 0.1);
  transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
  will-change: transform, box-shadow, border-color;
}

.product-card::before,
.product-card::after {
  content: '';
  position: absolute;
  inset: 0;
  transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
  pointer-events: none;
}

.product-card::before {
  background: 
    linear-gradient(120deg, 
      rgba(245, 158, 11, 0) 0%,
      rgba(245, 158, 11, 0.2) 40%,
      rgba(245, 158, 11, 0.2) 60%,
      rgba(245, 158, 11, 0) 100%
    );
  opacity: 0;
  transform: translateX(-100%);
}

.product-card::after {
  background: 
    linear-gradient(to bottom right, rgba(245, 158, 11, 0.2) 0%, transparent 30%),
    linear-gradient(to top left, rgba(245, 158, 11, 0.2) 0%, transparent 30%);
  opacity: 0;
  transition-delay: 0.2s;
}

.product-card:hover {
  background: rgba(255, 255, 255, 0.05) !important;
  transform: translateY(-5px) scale(1.02) rotateX(2deg);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.3),
    0 4px 8px rgba(245, 158, 11, 0.2);
  border-color: rgba(245, 158, 11, 0.3);
}

.product-card:hover::before {
  opacity: 1;
  transform: translateX(100%);
}

.product-card:hover::after {
  opacity: 1;
}

.product-image-wrapper {
  @apply p-4;
  transform-style: preserve-3d;
}

.product-image {
  @apply relative w-full rounded-lg overflow-hidden;
  padding-bottom: 100%;
  transform-style: preserve-3d;
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.product-image::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to bottom,
    transparent 0%,
    rgba(17, 17, 17, 0.4) 100%
  );
  opacity: 0;
  transition: opacity 0.5s ease;
}

.product-card:hover .product-image::after {
  opacity: 1;
}

.product-image img {
  @apply absolute inset-0 w-full h-full object-cover;
  transition: all 0.7s cubic-bezier(0.4, 0, 0.2, 1);
  filter: brightness(0.9) contrast(1.1);
}

.product-card:hover .product-image img {
  transform: scale(1.1) translateZ(20px);
  filter: brightness(1.1) contrast(1.2);
}

.stock-badge {
  @apply absolute top-2 right-2 px-3 py-1 text-sm font-semibold z-10;
  backdrop-filter: blur(8px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  transform: translateZ(30px);
  transition: all 0.3s ease;
}

.product-card:hover .stock-badge {
  transform: translateZ(40px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.low-stock {
  background: linear-gradient(
    45deg,
    rgba(245, 158, 11, 0.9) 0%,
    rgba(217, 119, 6, 0.9) 100%
  );
}

.out-of-stock {
  background: linear-gradient(
    45deg,
    rgba(239, 68, 68, 0.9) 0%,
    rgba(220, 38, 38, 0.9) 100%
  );
}

.product-info {
  @apply p-4 text-center relative;
  background: rgba(255, 255, 255, 0.02) !important;
  backdrop-filter: blur(5px) !important;
  -webkit-backdrop-filter: blur(5px) !important;
}

.product-name {
  @apply text-xl font-bold mb-2 text-gray-200;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.product-card:hover .product-info {
  transform: translateZ(10px);
}

.preview-enter-active,
.preview-leave-active {
  transition: all 0.2s ease-out;
}

.preview-enter-from,
.preview-leave-to {
  opacity: 0;
  transform: scale(0.95) translateX(-10px);
}
</style>
