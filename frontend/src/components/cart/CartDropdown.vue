<template>
  <div class="cart-dropdown relative" @mouseleave="closeDropdown">
    <button 
      id="cart-dropdown-button"
      class="cart-button flex items-center space-x-2 px-4 py-2" 
      @mouseenter="openDropdown"
      @click="navigateToCart"
      aria-label="Shopping Cart"
      :aria-expanded="isOpen"
      aria-controls="cart-dropdown-menu"
    >
      <div class="cart-icon relative">
        <font-awesome-icon icon="fa-solid fa-shopping-cart" class="h-6 w-6" aria-hidden="true" />
        <span 
          v-if="cartItemCount > 0" 
          class="cart-badge absolute -top-2 -right-2 bg-red-600 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center"
          aria-label="Cart items count"
        >
          {{ cartItemCount }}
        </span>
      </div>
      <span class="cart-total text-gray-200" aria-label="Cart total">${{ formatPrice(cartTotal) }}</span>
    </button>

    <div 
      id="cart-dropdown-menu"
      v-if="isOpen" 
      class="dropdown-menu fixed right-4 mt-2 w-80 bg-white/10 backdrop-blur-md shadow-xl rounded-lg border border-white/20 z-[1000]"
      role="dialog"
      aria-label="Shopping Cart Details"
    >
      <div class="dropdown-header flex justify-between items-center p-4 border-b border-white/20">
        <h3 id="cart-dropdown-title" class="text-lg font-semibold text-gray-200">Cart Summary</h3>
        <button 
          id="cart-close-button"
          @click="closeDropdown" 
          class="close-button text-gray-400 hover:text-gray-200"
          aria-label="Close cart"
        >
          <font-awesome-icon icon="fa-solid fa-times" aria-hidden="true" />
        </button>
      </div>

      <div v-if="isLoading || isUpdating" class="p-4 text-center" aria-live="polite">
        <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-red-600 mx-auto"></div>
      </div>

      <template v-else>
        <div v-if="items.length > 0" class="cart-items max-h-96 overflow-y-auto">
          <div 
            v-for="item in displayedItems" 
            :key="item.product.id" 
            class="cart-item flex items-center p-4 border-b border-white/20 hover:bg-white/5"
          >
            <div class="item-image w-16 h-16 flex-shrink-0">
              <img 
                :src="item.product.image" 
                :alt="item.product.name"
                @error="$event.target.src = '/images/placeholder.png'"
                class="w-full h-full object-cover rounded"
              >
            </div>
            <div class="item-details ml-4 flex-1">
              <span class="item-name block font-medium text-gray-200">{{ item.product.name }}</span>
              <div class="item-info flex justify-between mt-1">
                <div class="quantity-controls flex items-center space-x-2">
                  <button 
                    @click.stop="updateQuantity(item.product.id, item.quantity, false)"
                    class="p-1 text-gray-400 hover:text-gray-200"
                    :disabled="isUpdating"
                  >
                    <font-awesome-icon icon="fa-solid fa-minus" class="h-3 w-3" />
                  </button>
                  <span class="quantity text-gray-400">{{ item.quantity }}</span>
                  <button 
                    @click.stop="updateQuantity(item.product.id, item.quantity, true)"
                    class="p-1 text-gray-400 hover:text-gray-200"
                    :disabled="isUpdating || item.quantity >= item.product.stock"
                  >
                    <font-awesome-icon icon="fa-solid fa-plus" class="h-3 w-3" />
                  </button>
                </div>
                <div class="flex items-center space-x-4">
                  <span class="item-price text-gray-200">${{ formatPrice(item.total_price) }}</span>
                  <button 
                    @click.stop="removeItem(item.product.id)"
                    class="text-gray-400 hover:text-red-500"
                    :disabled="isUpdating"
                  >
                    <font-awesome-icon icon="fa-solid fa-trash" class="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div v-if="cartItemCount > 3" class="more-items p-2 text-center text-gray-400 text-sm">
            and {{ cartItemCount - 3 }} more item(s)
          </div>
        </div>
        
        <div v-else class="empty-cart p-8 text-center">
          <font-awesome-icon icon="fa-solid fa-shopping-basket" class="text-4xl text-gray-400 mb-2" />
          <p class="text-gray-400">Your cart is empty</p>
        </div>

        <div v-if="items.length > 0" class="cart-summary p-4 border-t border-white/20">
          <div class="cart-total flex justify-between items-center mb-4">
            <span class="total-label font-semibold text-gray-200">Total:</span>
            <span class="total-amount font-bold text-gray-200">${{ formatPrice(cartTotal) }}</span>
          </div>

          <div class="cart-actions grid grid-cols-2 gap-2">
            <button 
              class="view-cart-btn px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-medium transition-colors"
              @click="navigateToCart"
            >
              View Cart
            </button>
            <button 
              class="checkout-btn px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-colors"
              @click="navigateToCheckout"
            >
              Checkout
            </button>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useCartStore } from '@/stores/cartStore'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { library } from '@fortawesome/fontawesome-svg-core'
import { 
  faShoppingCart,
  faShoppingBasket,
  faTimes,
  faTrash,
  faPlus,
  faMinus
} from '@fortawesome/free-solid-svg-icons'

library.add(faShoppingCart, faShoppingBasket, faTimes, faTrash, faPlus, faMinus)

const router = useRouter()
const cartStore = useCartStore()
const { showToast } = useToast()
const { state } = storeToRefs(cartStore)
const isOpen = ref(false)
const isUpdating = ref(false)

// Computed properties from store state
const cartItemCount = computed(() => state.value.total_items || 0)
const cartTotal = computed(() => Number(state.value.total || 0))
const items = computed(() => state.value.items || [])
const displayedItems = computed(() => items.value.slice(0, 3))
const isLoading = computed(() => state.value.loading)

const formatPrice = (price) => {
  return Number(price || 0).toFixed(2)
}

const openDropdown = async () => {
  isOpen.value = true
  try {
    await cartStore.fetchCart()
  } catch (error) {
    showToast('Failed to load cart', 'error')
    console.error('Error fetching cart:', error)
  }
}

const closeDropdown = () => {
  isOpen.value = false
}

const navigateToCart = () => {
  router.push('/cart')
  closeDropdown()
}

const navigateToCheckout = () => {
  router.push('/checkout')
  closeDropdown()
}

const updateQuantity = async (productId, currentQuantity, increment) => {
  if (isUpdating.value) return
  
  isUpdating.value = true
  const newQuantity = increment ? currentQuantity + 1 : currentQuantity - 1
  
  try {
    if (newQuantity <= 0) {
      await cartStore.removeItem(productId)
      showToast('Item removed from cart')
      
      // Close dropdown if cart becomes empty
      if (cartItemCount.value === 0) {
        closeDropdown()
      }
    } else {
      await cartStore.updateQuantity(productId, newQuantity)
      showToast('Cart updated')
    }
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.response?.data?.error || 'Failed to update cart'
    showToast(errorMessage, 'error')
    
    // Revert the quantity change in the UI
    if (error.response?.status === 400 && error.response?.data?.error === 'Insufficient stock') {
      showToast('Not enough stock available', 'error')
    }
  } finally {
    isUpdating.value = false
  }
}

const removeItem = async (productId) => {
  if (isUpdating.value) return
  
  isUpdating.value = true
  try {
    await cartStore.removeItem(productId)
    showToast('Item removed from cart')
    
    // Close dropdown if cart becomes empty
    if (cartItemCount.value === 0) {
      closeDropdown()
    }
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.response?.data?.error || 'Failed to remove item'
    showToast(errorMessage, 'error')
  } finally {
    isUpdating.value = false
  }
}

// Watch for cart changes
watch(() => cartStore.state.value, () => {
  if (cartStore.error) {
    showToast(cartStore.error, 'error')
  }
}, { deep: true })

// Watch for cart total items to close dropdown if cart becomes empty
watch(() => cartItemCount.value, (newCount) => {
  if (newCount === 0 && isOpen.value) {
    closeDropdown()
  }
})

onMounted(async () => {
  try {
    await cartStore.fetchCart()
  } catch (error) {
    showToast('Failed to load cart', 'error')
    console.error('Error initializing cart:', error)
  }
})
</script>

<style scoped>
.cart-dropdown {
  @apply relative inline-block;
}

.cart-button {
  @apply flex items-center space-x-2 px-4 py-2 text-gray-200 hover:text-gray-100 focus:outline-none focus:ring-2 focus:ring-red-500;
}

.dropdown-menu {
  max-height: calc(100vh - 5rem);
  overflow-y: auto;
}

.quantity-controls button:disabled {
  @apply opacity-50 cursor-not-allowed;
}

/* Custom scrollbar for the dropdown menu */
.dropdown-menu::-webkit-scrollbar {
  width: 6px;
}

.dropdown-menu::-webkit-scrollbar-track {
  @apply bg-transparent;
}

.dropdown-menu::-webkit-scrollbar-thumb {
  @apply bg-white/20 rounded-full;
}

.dropdown-menu::-webkit-scrollbar-thumb:hover {
  @apply bg-white/30;
}
</style>
