<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 py-12 px-4">
    <div class="max-w-7xl mx-auto">
      <!-- Cart Header -->
      <div class="mb-8">
        <h1 class="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-red-600">
          Shopping Cart
        </h1>
        <p class="mt-2 text-gray-400">Your items are listed below</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center h-96">
        <div class="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-red-500"></div>
      </div>

      <!-- Empty Cart -->
      <div v-else-if="!cartStore.itemCount" 
           class="bg-gray-800/40 backdrop-blur-xl shadow-xl rounded-xl p-12 text-center
                  border border-gray-700/50">
        <i class="fas fa-shopping-cart text-6xl text-gray-500 mb-4"></i>
        <h2 class="text-2xl font-bold text-gray-200 mb-2">Your cart is empty</h2>
        <p class="text-gray-400 mb-8">Start adding some items to your cart!</p>
        <router-link to="/products"
                     class="inline-flex items-center px-8 py-3 rounded-lg text-white font-medium
                            bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700
                            transform hover:-translate-y-0.5 transition-all duration-300
                            shadow-lg hover:shadow-red-500/25">
          Continue Shopping
        </router-link>
      </div>

      <!-- Cart Items -->
      <div v-else class="space-y-6">
        <!-- Cart Items List -->
        <div v-for="item in cartStore.items" 
             :key="item.id"
             class="bg-gray-800/40 backdrop-blur-xl shadow-xl rounded-xl p-6 
                    border border-gray-700/50 hover:border-red-500/30 
                    transition-all duration-300 group">
          <div class="flex items-center gap-6">
            <!-- Product Image -->
            <div class="w-32 h-32 rounded-xl overflow-hidden bg-gray-700/50">
              <img :src="item.product.image"
                   :alt="item.product.name"
                   class="w-full h-full object-cover transform group-hover:scale-105 transition duration-500"
                   @error="$event.target.src = '/images/placeholder.png'" />
            </div>

            <!-- Product Info -->
            <div class="flex-1">
              <h3 class="text-xl font-bold text-gray-100">
                <router-link :to="{ name: 'product-detail', params: { id: item.product.id }}"
                           class="hover:text-red-400 transition-colors">
                  {{ item.product.name }}
                </router-link>
              </h3>
              <p class="text-gray-400 text-sm mt-2">{{ item.product.description }}</p>

              <!-- Stock Warning -->
              <p v-if="item.product.stock <= 5" 
                 class="text-yellow-500 text-sm mt-2 flex items-center gap-2">
                <i class="fas fa-exclamation-triangle"></i>
                Only {{ item.product.stock }} left in stock!
              </p>

              <div class="flex items-center justify-between mt-4">
                <div class="flex items-center gap-4">
                  <!-- Quantity Controls -->
                  <div class="flex items-center bg-gray-900/50 rounded-lg backdrop-blur-sm border border-gray-700/50">
                    <button @click="updateQuantity(item, item.quantity - 1)"
                            class="p-2 hover:bg-red-500/20 text-gray-300 hover:text-red-400 
                                   disabled:opacity-50 transition-all duration-300"
                            :disabled="item.quantity <= 1 || loading">
                      <i class="fas fa-minus"></i>
                    </button>
                    <span class="px-4 py-2 text-gray-200 font-medium border-x border-gray-700/50">
                      {{ item.quantity }}
                    </span>
                    <button @click="updateQuantity(item, item.quantity + 1)"
                            class="p-2 hover:bg-red-500/20 text-gray-300 hover:text-red-400 
                                   disabled:opacity-50 transition-all duration-300"
                            :disabled="loading || item.quantity >= item.product.stock">
                      <i class="fas fa-plus"></i>
                    </button>
                  </div>

                  <!-- Remove Button -->
                  <button @click="removeItem(item)"
                          class="text-sm font-medium text-red-400 hover:text-red-300 
                                 disabled:opacity-50 flex items-center gap-2 transition-colors"
                          :disabled="loading">
                    <i class="fas fa-trash"></i>
                    <span>Remove</span>
                  </button>
                </div>

                <!-- Price -->
                <div class="text-right">
                  <div class="text-2xl font-bold text-transparent bg-clip-text 
                              bg-gradient-to-r from-red-400 to-red-600">
                    ${{ formatPrice(item.total_price) }}
                  </div>
                  <div class="text-sm text-gray-400 mt-1">
                    ${{ formatPrice(item.unit_price) }} each
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Order Summary -->
        <div class="bg-gray-800/40 backdrop-blur-xl shadow-xl rounded-xl p-6 
                    border border-gray-700/50">
          <h2 class="text-xl font-bold text-transparent bg-clip-text 
                     bg-gradient-to-r from-red-400 to-red-600 mb-6">
            Order Summary
          </h2>

          <div class="space-y-4">
            <div class="flex justify-between text-sm">
              <span class="text-gray-400">Subtotal</span>
              <span class="font-medium text-gray-200">${{ formatPrice(cartStore.subtotal) }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-gray-400">Tax</span>
              <span class="font-medium text-gray-200">${{ formatPrice(cartStore.tax) }}</span>
            </div>
            <div class="border-t border-gray-700/50 pt-4">
              <div class="flex justify-between">
                <span class="text-lg font-bold text-gray-200">Total</span>
                <span class="text-lg font-bold text-transparent bg-clip-text 
                           bg-gradient-to-r from-red-400 to-red-600">
                  ${{ formatPrice(cartStore.total) }}
                </span>
              </div>
            </div>
          </div>

          <div class="mt-8 space-y-4">
            <button @click="checkout"
                    class="w-full inline-flex justify-center items-center px-6 py-3 rounded-lg
                           text-white font-medium bg-gradient-to-r from-red-500 to-red-600
                           hover:from-red-600 hover:to-red-700 transform hover:-translate-y-0.5
                           transition-all duration-300 shadow-lg hover:shadow-red-500/25"
                    :disabled="loading">
              <span v-if="loading">Processing...</span>
              <span v-else>Proceed to Checkout</span>
            </button>

            <router-link to="/products"
                         class="w-full inline-flex justify-center items-center px-6 py-3 rounded-lg
                                text-gray-300 hover:text-white font-medium bg-gray-800/50 
                                hover:bg-gray-700/50 backdrop-blur-sm border border-gray-700/50 
                                hover:border-gray-600/50 transform hover:-translate-y-0.5 
                                transition-all duration-300">
              Continue Shopping
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useCartStore } from '@/stores/cartStore'
import { useToast } from '@/composables/useToast'

const cartStore = useCartStore()
const loading = ref(false)
const { showToast } = useToast()

const formatPrice = (price) => {
  return Number(price).toFixed(2)
}

const updateQuantity = async (item, newQuantity) => {
  if (newQuantity < 1) return
  if (newQuantity > item.product.stock) {
    showToast(`Only ${item.product.stock} items available`, 'error')
    return
  }
  
  try {
    loading.value = true
    await cartStore.updateItemQuantity(item.product.id, newQuantity)
    showToast('Cart updated successfully')
  } catch (error) {
    const errorMessage = error?.response?.data?.error || error?.message || 'Failed to update quantity'
    showToast(errorMessage, 'error')
  } finally {
    loading.value = false
  }
}

const removeItem = async (item) => {
  try {
    loading.value = true
    await cartStore.removeItem(item.product.id)
    showToast('Item removed from cart')
  } catch (error) {
    const errorMessage = error?.response?.data?.error || error?.message || 'Failed to remove item'
    showToast(errorMessage, 'error')
  } finally {
    loading.value = false
  }
}

const checkout = async () => {
  try {
    loading.value = true
    // TODO: Implement checkout functionality
    showToast('Checkout feature coming soon!', 'info')
  } catch (error) {
    showToast('Failed to process checkout', 'error')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    loading.value = true
    await cartStore.fetchCart()
  } catch (error) {
    showToast('Failed to load cart items', 'error')
  } finally {
    loading.value = false
  }
})
</script>
