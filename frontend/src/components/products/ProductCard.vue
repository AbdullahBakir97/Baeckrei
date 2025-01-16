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
               backdrop-blur-md bg-black/30 text-white hover:bg-black/50 
               transition-all duration-200 z-10 opacity-0 group-hover:opacity-100"
      >
        <font-awesome-icon icon="fa-solid fa-eye" />
      </button>

      <!-- Quick Preview Popup -->
      <Transition name="preview">
        <div v-if="showQuickPreview"
             @mouseenter="showQuickPreview = true"
             @mouseleave="showQuickPreview = false"
             class="absolute inset-0 bg-gray-900/95 rounded-lg 
                    shadow-xl border border-white/10 z-50">
          <div class="p-4 h-full flex flex-col">
            <div class="flex-1">
              <h3 class="text-lg font-bold mb-2 bg-gradient-to-r from-red-400 
                         to-red-600 bg-clip-text text-transparent">
                {{ product.name }}
              </h3>
              <div class="flex justify-between items-center mb-3">
                <span class="text-xl font-bold text-red-500">
                  ${{ formatPrice(product.price) }}
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
              <button @click="addToCart"
                      :disabled="!product.available"
                      class="flex-1 py-1.5 px-3 rounded-lg bg-gradient-to-r 
                             from-red-500 to-red-600 text-white text-sm
                             hover:from-red-600 hover:to-red-700
                             disabled:opacity-50 disabled:cursor-not-allowed">
                Add to Cart
              </button>
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
      <h3 class="product-name">{{ product.name }}</h3>
      <p class="product-price">${{ formatPrice(product.price) }}</p>
      
      <!-- Cart Controls -->
      <div v-if="product.stock > 0">
        <div class="cart-controls">
          <template v-if="!isInCart">
            <button 
              ref="addToCartBtn"
              class="add-to-cart-btn"
              :disabled="loading"
              @click="addToCart"
            >
              <font-awesome-icon icon="fa-solid fa-cart-plus" />
              <span>{{ loading ? 'Adding...' : 'Add to Cart' }}</span>
            </button>
          </template>
          <template v-else>
            <div class="cart-actions">
              <div class="quantity-controls">
                <button 
                  ref="el => quantityBtns.push(el)"
                  class="quantity-btn"
                  :disabled="loading || cartItem.quantity <= 1"
                  @click="updateQuantity(cartItem.quantity - 1)"
                >
                  <font-awesome-icon icon="fa-solid fa-minus" />
                </button>
                
                <input 
                  class="quantity"
                  type="number"
                  :value="cartItem.quantity"
                  @input="updateQuantity($event.target.valueAsNumber)"
                />
                
                <button 
                  ref="el => quantityBtns.push(el)"
                  class="quantity-btn"
                  :disabled="loading || cartItem.quantity >= product.stock"
                  @click="updateQuantity(cartItem.quantity + 1)"
                >
                  <font-awesome-icon icon="fa-solid fa-plus" />
                </button>
              </div>
              <button 
                ref="removeBtn"
                class="remove-btn"
                :disabled="loading"
                @click="removeFromCart"
              >
                <font-awesome-icon icon="fa-solid fa-trash-can" />
                <span>Remove</span>
              </button>
            </div>
          </template>
        </div>
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useCartStore } from '@/stores/cartStore'
import { storeToRefs } from 'pinia'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { library } from '@fortawesome/fontawesome-svg-core'
import { 
  faCartPlus,
  faPlus,
  faMinus,
  faTrashCan,
  faEye
} from '@fortawesome/free-solid-svg-icons'
import { useToast } from '@/composables/useToast'
import QuickViewModal from './QuickViewModal.vue'

library.add(faCartPlus, faPlus, faMinus, faTrashCan, faEye)

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

const cartStore = useCartStore()
const { state } = storeToRefs(cartStore)
const { showToast } = useToast()
const loading = ref(false)
const message = ref('')
const messageType = ref('')
const quantity = ref(1)
const showQuickView = ref(false)
const showQuickPreview = ref(false)

const cartItem = computed(() => 
  state.value?.items?.find(item => item.product.id === props.product.id)
)

const isInCart = computed(() => !!cartItem.value)

const addToCartBtn = ref(null)
const quantityBtns = ref([])
const removeBtn = ref(null)

const handleImageError = (e) => {
  e.target.src = '/images/placeholder.png' // Fallback image
}

const formatPrice = (price) => {
  return Number(price).toFixed(2)
}

const updateQuantity = async (newQuantity) => {
  try {
    if (newQuantity < 1) return
    await cartStore.updateQuantity(props.product.id, newQuantity)
    showToast('Cart updated successfully')
  } catch (error) {
    console.error('Error updating quantity:', error)
    showToast('Failed to update cart', 'error')
  }
}

const addToCart = async () => {
  try {
    await cartStore.addItem(props.product.id, quantity.value)
    showToast('Product added to cart')
    quantity.value = 1 // Reset quantity after adding
  } catch (error) {
    console.error('Error adding to cart:', error)
    showToast('Failed to add to cart', 'error')
  }
}

const removeFromCart = async () => {
  try {
    await cartStore.removeItem(props.product.id)
    showToast('Product removed from cart')
  } catch (error) {
    console.error('Error removing from cart:', error)
    showToast('Failed to remove from cart', 'error')
  }
}

const handleMouseMove = (e, button) => {
  if (!button) return
  
  const rect = button.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  
  const centerX = rect.width / 2
  const centerY = rect.height / 2
  
  const rotateX = (y - centerY) / 8
  const rotateY = (centerX - x) / 8
  
  button.style.transform = `
    perspective(1000px)
    rotateX(${rotateX}deg)
    rotateY(${rotateY}deg)
    translateZ(10px)
  `
}

const resetButtonTransform = (button) => {
  if (!button) return
  button.style.transform = `
    perspective(1000px)
    rotateX(0deg)
    rotateY(0deg)
    translateZ(0px)
  `
}

onMounted(() => {
  // Add event listeners for mouse movement
  if (addToCartBtn.value) {
    addToCartBtn.value.addEventListener('mousemove', (e) => handleMouseMove(e, addToCartBtn.value))
    addToCartBtn.value.addEventListener('mouseleave', () => resetButtonTransform(addToCartBtn.value))
  }
  
  quantityBtns.value.forEach(btn => {
    btn.addEventListener('mousemove', (e) => handleMouseMove(e, btn))
    btn.addEventListener('mouseleave', () => resetButtonTransform(btn))
  })
  
  if (removeBtn.value) {
    removeBtn.value.addEventListener('mousemove', (e) => handleMouseMove(e, removeBtn.value))
    removeBtn.value.addEventListener('mouseleave', () => resetButtonTransform(removeBtn.value))
  }
})

onUnmounted(() => {
  // Clean up event listeners
  if (addToCartBtn.value) {
    addToCartBtn.value.removeEventListener('mousemove', handleMouseMove)
    addToCartBtn.value.removeEventListener('mouseleave', resetButtonTransform)
  }
  
  quantityBtns.value.forEach(btn => {
    btn.removeEventListener('mousemove', handleMouseMove)
    btn.removeEventListener('mouseleave', resetButtonTransform)
  })
  
  if (removeBtn.value) {
    removeBtn.value.removeEventListener('mousemove', handleMouseMove)
    removeBtn.value.removeEventListener('mouseleave', resetButtonTransform)
  }
})
</script>

<style scoped>
.product-card {
  @apply relative rounded-lg overflow-hidden transition-all duration-500;
  min-height: 400px;
  perspective: 2000px;
  transform-style: preserve-3d;
  background: linear-gradient(
    to bottom,
    rgba(17, 17, 17, 0.95) 0%,
    rgba(17, 17, 17, 0.85) 100%
  );
  backdrop-filter: blur(10px);
  border: 1px solid rgba(239, 68, 68, 0.1);
  box-shadow: 
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06),
    0 0 20px rgba(239, 68, 68, 0.1);
}

.product-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: 
    linear-gradient(to bottom right, rgba(239, 68, 68, 0.2) 0%, transparent 30%),
    linear-gradient(to top left, rgba(239, 68, 68, 0.2) 0%, transparent 30%);
  opacity: 0;
  transition: opacity 0.5s ease;
}

.product-card:hover {
  transform: translateY(-8px) rotateX(5deg) rotateY(-5deg);
  box-shadow: 
    20px 20px 60px rgba(0, 0, 0, 0.5),
    -20px -20px 60px rgba(239, 68, 68, 0.05);
  border-color: rgba(239, 68, 68, 0.3);
}

.product-card:hover::before {
  opacity: 1;
}

.strip-container {
  display: none;
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
  background: linear-gradient(
    to top,
    rgba(17, 17, 17, 0.8) 0%,
    transparent 100%
  );
}

.product-name {
  @apply text-xl font-bold mb-2 text-gray-200;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.product-price {
  @apply text-xl font-bold;
  color: #ef4444;
}

.product-card:hover .product-info {
  transform: translateZ(10px);
}

.cart-controls {
  @apply flex flex-col items-center gap-2 relative w-full;
  transform-style: preserve-3d;
}

.cart-actions {
  @apply flex flex-col items-center gap-3 w-full;
  transform-style: preserve-3d;
}

.quantity-controls {
  @apply flex items-center justify-center gap-1 w-auto;
  transform-style: preserve-3d;
  background: rgba(17, 17, 17, 0.7);
  border-radius: 0.5rem;
  padding: 0.25rem;
  backdrop-filter: blur(4px);
}

.quantity-btn {
  @apply w-7 h-7 rounded-md flex items-center justify-center relative;
  background: rgba(23, 23, 23, 0.7);
  border: 1px solid rgba(255, 107, 107, 0.2);
  transform-style: preserve-3d;
  transition: all 0.15s ease;
  transform-origin: center center;
  will-change: transform;
}

.quantity-btn svg {
  color: #ef4444;
  transition: all 0.3s ease;
}

.quantity-btn:hover {
  border-color: rgba(255, 107, 107, 0.4);
  box-shadow: 0 0 15px rgba(255, 107, 107, 0.2);
}

.quantity {
  @apply text-lg font-semibold text-center rounded-md text-gray-200;
  background: rgba(23, 23, 23, 0.7);
  border: 1px solid rgba(255, 107, 107, 0.2);
  width: 2.5rem;
  height: 1.75rem;
  outline: none;
  -moz-appearance: textfield;
  transition: all 0.15s ease;
  backdrop-filter: blur(4px);
}

.quantity:hover,
.quantity:focus {
  background: rgba(23, 23, 23, 0.9);
  border-color: rgba(255, 107, 107, 0.4);
  box-shadow: 
    0 0 0 2px rgba(255, 107, 107, 0.1),
    0 0 20px rgba(255, 107, 107, 0.2);
}

.add-to-cart-btn {
  @apply w-full py-2 px-4 text-white rounded-lg
         flex items-center justify-center gap-2
         transition-all duration-200
         disabled:opacity-50 disabled:cursor-not-allowed;
  background-color: #ef4444;
}

.add-to-cart-btn:hover {
  background-color: #dc2626;
  box-shadow: 0 0 20px rgba(255, 107, 107, 0.2);
}

.remove-btn {
  @apply w-full py-2 px-4 rounded-lg flex items-center justify-center gap-2 
         text-base font-semibold relative;
  background: transparent;
  border: 1px solid rgba(239, 68, 68, 0.3);
  transform-style: preserve-3d;
  transition: all 0.15s ease;
  transform-origin: center center;
  will-change: transform;
}

.remove-btn span,
.remove-btn svg {
  color: #ef4444;
  transition: all 0.3s ease;
}

.remove-btn:hover {
  border-color: rgba(239, 68, 68, 0.8);
  box-shadow: 0 0 15px rgba(239, 68, 68, 0.2);
}

button:not(:disabled):active {
  transform: perspective(1000px) translateZ(-10px);
}

button:disabled {
  @apply opacity-50 cursor-not-allowed;
  transform: none !important;
}

button:disabled span,
button:disabled svg {
  opacity: 0.5;
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

