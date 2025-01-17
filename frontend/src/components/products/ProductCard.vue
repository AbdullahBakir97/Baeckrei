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
              <button @click="addToCart"
                      :disabled="!product.available"
                      class="flex-1 py-1.5 px-3 rounded-lg text-sm
                             bg-transparent border border-amber-500/30
                             hover:border-amber-500/80 hover:shadow-[0_0_15px_rgba(245,158,11,0.2)]
                             disabled:opacity-50 disabled:cursor-not-allowed">
                <span class="text-amber-400">Add to Cart</span>
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
      <router-link 
        :to="{ name: 'product-detail', params: { id: product.id }}" 
        class="product-name hover:text-amber-400 transition-colors duration-200"
      >
        {{ product.name }}
      </router-link>
      <p class="product-price">{{ formatPrice(product.price) }} €</p>
      
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

defineEmits(['addToCart'])

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
  background: rgba(255, 255, 255, 0.03);
  border-radius: 0.5rem;
  padding: 0.25rem;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.quantity-btn {
  @apply w-7 h-7 rounded-md flex items-center justify-center relative;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(245, 158, 11, 0.2);
  transform-style: preserve-3d;
  transition: all 0.15s ease;
  transform-origin: center center;
  will-change: transform;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.quantity-btn svg {
  color: #f59e0b;
  transition: all 0.3s ease;
}

.quantity-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(245, 158, 11, 0.4);
  box-shadow: 0 0 15px rgba(245, 158, 11, 0.2);
}

.quantity {
  @apply text-lg font-semibold text-center rounded-md text-gray-200;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(245, 158, 11, 0.2);
  width: 2.5rem;
  height: 1.75rem;
  outline: none;
  -moz-appearance: textfield;
  transition: all 0.15s ease;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.quantity:hover,
.quantity:focus {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(245, 158, 11, 0.4);
  box-shadow: 
    0 0 0 2px rgba(245, 158, 11, 0.1),
    0 0 20px rgba(245, 158, 11, 0.2);
}

.add-to-cart-btn {
  @apply w-full py-2 px-4 rounded-lg flex items-center justify-center gap-2 
         text-base font-semibold relative;
  background: transparent;
  border: 1px solid rgba(245, 158, 11, 0.3);
  transform-style: preserve-3d;
  transition: all 0.15s ease;
  transform-origin: center center;
  will-change: transform;
}

.add-to-cart-btn span,
.add-to-cart-btn svg {
  color: #f59e0b;
  transition: all 0.3s ease;
}

.add-to-cart-btn:hover {
  border-color: rgba(245, 158, 11, 0.8);
  box-shadow: 0 0 15px rgba(245, 158, 11, 0.2);
}

.add-to-cart-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  border-color: rgba(245, 158, 11, 0.1);
  box-shadow: none;
}

.remove-btn {
  @apply w-full py-2 px-4 rounded-lg flex items-center justify-center gap-2 
         text-base font-semibold relative;
  background: transparent;
  border: 1px solid rgba(245, 158, 11, 0.3);
  transform-style: preserve-3d;
  transition: all 0.15s ease;
  transform-origin: center center;
  will-change: transform;
}

.remove-btn span,
.remove-btn svg {
  color: #f59e0b;
  transition: all 0.3s ease;
}

.remove-btn:hover {
  border-color: rgba(245, 158, 11, 0.8);
  box-shadow: 0 0 15px rgba(245, 158, 11, 0.2);
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
