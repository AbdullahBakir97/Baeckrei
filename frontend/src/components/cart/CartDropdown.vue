<template>
  <div class="cart-dropdown" @mouseleave="closeDropdown">
    <button 
      id="cart-dropdown-button"
      class="cart-button" 
      @mouseenter="openDropdown"
      @click="navigateToCart"
      aria-label="Shopping Cart"
      aria-expanded="isOpen"
      aria-controls="cart-dropdown-menu"
    >
      <div class="cart-icon">
        <font-awesome-icon icon="fa-solid fa-shopping-cart" aria-hidden="true" />
        <span v-if="cartItemCount > 0" class="cart-badge" aria-label="Cart items count">
          {{ cartItemCount }}
        </span>
      </div>
      <span class="cart-total" aria-label="Cart total">{{ formatPrice(cartTotal) }} €</span>
    </button>

    <div 
      id="cart-dropdown-menu"
      v-if="isOpen" 
      class="dropdown-menu"
      @mouseleave="closeDropdown"
      role="dialog"
      aria-label="Shopping Cart Details"
    >
      <div class="dropdown-header">
        <h3 id="cart-dropdown-title">Cart Summary</h3>
        <button 
          id="cart-close-button"
          @click="closeDropdown" 
          class="close-button"
          aria-label="Close cart"
        >
          <font-awesome-icon icon="fa-solid fa-times" aria-hidden="true" />
        </button>
      </div>

      <div v-if="isLoading" class="p-4 text-center" aria-live="polite">
        <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-600 mx-auto" aria-label="Loading cart contents"></div>
      </div>

      <template v-else>
        <div v-if="items.length > 0" class="cart-items">
          <div 
            v-for="(item, index) in displayedItems" 
            :key="item.product.id" 
            class="cart-item"
            :id="'cart-item-' + item.product.id"
          >
            <div class="item-image">
              <img 
                :src="item.product.image" 
                :alt="item.product.name"
                @error="$event.target.src = '/images/placeholder.png'"
                :id="'cart-item-image-' + item.product.id"
              />
            </div>
            <div class="item-details">
              <span class="item-name text-gray-900">{{ item.product.name }}</span>
              <div class="item-info">
                <span class="item-quantity text-gray-700" :id="'cart-item-quantity-' + item.product.id">
                  x{{ item.quantity }}
                </span>
                <span class="item-price text-gray-900" :id="'cart-item-price-' + item.product.id">
                  {{ formatPrice(item.product?.price) }} € each
                </span>
                <span class="item-subtotal text-gray-900">
                  Subtotal: {{ formatPrice(item.total_price) }} €
                </span>
              </div>
            </div>
          </div>

          <div v-if="cartItemCount > 3" class="more-items text-gray-700">
            and {{ cartItemCount - 3 }} more item(s)
          </div>
        </div>
        
        <div v-else class="empty-cart" aria-live="polite">
          <font-awesome-icon icon="fa-solid fa-shopping-basket" class="empty-icon text-gray-600" aria-hidden="true" />
          <p class="text-gray-700">Your cart is empty</p>
        </div>

        <div v-if="items.length > 0" class="cart-summary">
          <div class="cart-total">
            <span class="total-label text-gray-900">Total:</span>
            <span class="total-amount text-gray-900" id="cart-total-amount">
              {{ formatPrice(cartTotal) }} €
            </span>
          </div>

          <div class="cart-actions">
            <button 
              id="view-cart-button"
              class="view-cart-btn bg-gray-600 hover:bg-gray-700 text-white"
              @click="navigateToCart"
            >
              View Cart
            </button>
            <button 
              id="checkout-button"
              class="checkout-btn bg-blue-600 hover:bg-blue-700 text-white"
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
import { computed, onMounted } from 'vue'
import { useCartStore } from '@/stores/cartStore'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { library } from '@fortawesome/fontawesome-svg-core'
import { 
  faShoppingCart,
  faShoppingBasket,
  faTimes
} from '@fortawesome/free-solid-svg-icons'

library.add(faShoppingCart, faShoppingBasket, faTimes)

const router = useRouter()
const cartStore = useCartStore()

const { items, loading, total, total_items, dropdownVisible } = storeToRefs(cartStore)

// Computed properties from store state
const cartItemCount = computed(() => total_items.value || 0)
const cartTotal = computed(() => Number(total.value || 0))
const displayedItems = computed(() => items.value?.slice(0, 3) || [])
const isOpen = computed(() => dropdownVisible.value)
const isLoading = computed(() => loading.value)

const formatPrice = (price) => {
  return Number(price || 0).toFixed(2)
}


const openDropdown = async () => {
  await cartStore.fetchCart()
  cartStore.showDropdown()
}

const closeDropdown = () => {
  cartStore.hideDropdown()
}

const navigateToCart = () => {
  router.push('/cart')
  closeDropdown()
}

const navigateToCheckout = () => {
  router.push('/checkout')
  closeDropdown()
}

onMounted(async () => {
  await cartStore.fetchCart()
})
</script>

<style scoped>
.cart-dropdown {
  @apply relative inline-block;
}

.cart-button {
  @apply flex items-center space-x-2 px-4 py-2 text-gray-900 hover:text-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500;
}

.cart-icon {
  @apply relative;
}

.cart-badge {
  @apply absolute -top-2 -right-2 bg-blue-600 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center;
}

.dropdown-menu {
  @apply absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg z-50 border border-gray-200;
}

.dropdown-header {
  @apply flex justify-between items-center p-4 border-b border-gray-200;
}

.dropdown-header h3 {
  @apply text-lg font-semibold text-gray-900;
}

.close-button {
  @apply p-2 text-gray-500 hover:text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500;
}

.cart-items {
  @apply max-h-96 overflow-y-auto;
}

.cart-item {
  @apply flex items-center p-4 border-b border-gray-200;
}

.item-image {
  @apply w-16 h-16 flex-shrink-0;
}

.item-image img {
  @apply w-full h-full object-cover rounded;
}

.item-info {
  @apply flex flex-col space-y-1 mt-1 w-full;
}

.item-details {
  @apply ml-4 flex-1 min-w-0; /* Added min-w-0 to prevent text overflow */
}

.item-name {
  @apply block font-medium text-sm truncate mb-1; /* Added truncate for long names */
}

.item-quantity {
  @apply text-sm text-gray-600;
}

.item-price {
  @apply text-sm text-gray-600;
}

.item-subtotal {
  @apply text-sm font-semibold text-gray-900;
}

/* Update dropdown width */
.dropdown-menu {
  @apply absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-lg z-50 border border-gray-200;
}

/* Update cart item spacing */
.cart-item {
  @apply flex items-start p-4 hover:bg-gray-50 transition-colors duration-150;
}

/* Update image size and style */
.item-image {
  @apply w-20 h-20 flex-shrink-0 rounded-md overflow-hidden border border-gray-200;
}

/* Update cart summary section */
.cart-summary {
  @apply p-4 bg-gray-50 rounded-b-lg border-t border-gray-200;
}

.cart-actions {
  @apply grid grid-cols-2 gap-3 mt-4;
}

.view-cart-btn, .checkout-btn {
  @apply px-4 py-2.5 rounded-lg text-sm font-medium transition-colors duration-200;
}

/* Update more items section */
.more-items {
  @apply p-3 text-center text-sm bg-gray-50 border-t border-gray-200;
}

.empty-cart {
  @apply p-8 text-center;
}

.empty-icon {
  @apply text-4xl mb-2;
}

.cart-summary {
  @apply p-4 bg-gray-50 rounded-b-lg;
}

.cart-total {
  @apply flex justify-between items-center mb-4;
}

.total-label {
  @apply font-semibold;
}

.total-amount {
  @apply font-bold;
}

.cart-actions {
  @apply grid grid-cols-2 gap-2;
}

.view-cart-btn, .checkout-btn {
  @apply px-4 py-2 rounded-lg font-medium focus:outline-none focus:ring-2 focus:ring-offset-2;
}

.more-items {
  @apply p-2 text-center text-sm;
}
</style>
