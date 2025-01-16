<template>
  <div class="min-h-screen bg-gradient-to-br from-dark-900 via-dark-800 to-dark-900 py-12 px-4">
    <div class="max-w-7xl mx-auto">
      <!-- Cart Header -->
      <div class="mb-16 text-center space-y-4">
        <h1 class="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-red-600">
          Shopping Cart
        </h1>
        <p class="text-dark-400">Your items are listed below</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" 
           class="flex flex-col items-center justify-center py-32 gap-6">
        <div class="relative w-20 h-20">
          <div class="absolute inset-0 rounded-full border-t-2 border-red-500/30 animate-spin"></div>
          <div class="absolute inset-[4px] rounded-full border-t-2 border-red-500/50 animate-spin-slow"></div>
          <div class="absolute inset-[8px] rounded-full border-t-2 border-red-500/70 animate-spin-slower"></div>
        </div>
        <p class="text-dark-400 animate-pulse font-medium">Loading your cart...</p>
      </div>

      <template v-else>
        <!-- Cart Content -->
        <div v-if="cartStore.items.length > 0" class="grid lg:grid-cols-12 gap-8">
          <!-- Cart Items -->
          <div class="lg:col-span-8 space-y-4">
            <div v-for="item in cartStore.items" 
                 :key="item.id"
                 class="group">
              <div class="bg-white/10 backdrop-blur-md shadow-xl rounded-xl p-6 
                         border border-white/20 hover:border-red-500/30 
                         transition-all duration-300">
                <div class="flex items-start gap-6">
                  <!-- Product Image -->
                  <div class="w-32 h-32 rounded-lg overflow-hidden bg-white/5">
                    <img v-if="item.product.image"
                         :src="item.product.image"
                         :alt="item.product.name"
                         class="w-full h-full object-cover transform group-hover:scale-105 transition duration-500"
                         @error="$event.target.src = '/images/placeholder.png'" />
                    <div v-else class="w-full h-full flex items-center justify-center">
                      <i class="fas fa-image text-4xl text-dark-600"></i>
                    </div>
                  </div>

                  <!-- Product Details -->
                  <div class="flex-1 min-w-0">
                    <h3 class="text-xl font-bold text-dark-100">
                      <router-link :to="{ name: 'product-detail', params: { id: item.product.id }}"
                                 class="hover:text-red-400 transition-colors">
                        {{ item.product.name }}
                      </router-link>
                    </h3>
                    
                    <div v-if="item.product.stock <= 5" 
                         class="mt-1 text-sm text-yellow-500 flex items-center gap-2">
                      <i class="fas fa-exclamation-triangle"></i>
                      Only {{ item.product.stock }} left in stock!
                    </div>
                    
                    <p class="mt-2 text-dark-400 text-sm line-clamp-2">{{ item.product.description }}</p>

                    <div class="mt-4 flex items-center justify-between">
                      <div class="flex items-center gap-4">
                        <!-- Quantity Controls -->
                        <div class="flex items-center bg-white/10 backdrop-blur-md shadow-xl rounded-lg 
                                  border border-white/20 hover:border-red-500/30">
                          <button @click="updateQuantity(item.product.id, item.quantity - 1)"
                                  class="px-3 py-2 hover:bg-red-500/20 text-dark-300 hover:text-red-400 
                                         disabled:opacity-50 transition-all duration-300 rounded-l-lg"
                                  :disabled="loading || item.quantity <= 1">
                            <i class="fas fa-minus text-sm"></i>
                          </button>
                          <span class="px-4 py-2 text-dark-200 font-medium border-x border-white/20">
                            {{ item.quantity }}
                          </span>
                          <button @click="updateQuantity(item.product.id, item.quantity + 1)"
                                  class="px-3 py-2 hover:bg-red-500/20 text-dark-300 hover:text-red-400 
                                         disabled:opacity-50 transition-all duration-300 rounded-r-lg"
                                  :disabled="loading || item.quantity >= item.product.stock">
                            <i class="fas fa-plus text-sm"></i>
                          </button>
                        </div>

                        <!-- Remove Button -->
                        <button @click="removeItem(item.product.id)"
                                class="flex items-center gap-2 px-4 py-2 text-sm font-medium
                                       bg-white/10 backdrop-blur-md shadow-xl rounded-lg 
                                       border border-white/20 hover:border-red-500/30
                                       text-dark-300 hover:text-red-400 
                                       disabled:opacity-50 transition-all duration-300"
                                :disabled="loading">
                          <i class="fas fa-trash-alt"></i>
                          <span>Remove</span>
                        </button>
                      </div>

                      <!-- Price -->
                      <div class="text-right">
                        <p class="text-2xl font-bold text-transparent bg-clip-text 
                                 bg-gradient-to-r from-red-400 to-red-600">
                          ${{ formatPrice(item.total_price) }}
                        </p>
                        <p class="text-sm text-dark-400 mt-1">
                          ${{ formatPrice(item.unit_price) }} each
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Order Summary -->
          <div class="lg:col-span-4">
            <div class="sticky top-4">
              <div class="bg-white/10 backdrop-blur-md shadow-xl rounded-xl 
                         border border-white/20">
                <!-- Header -->
                <div class="p-6 border-b border-white/20">
                  <h2 class="text-xl font-bold text-transparent bg-clip-text 
                            bg-gradient-to-r from-red-400 to-red-600">
                    Order Summary
                  </h2>
                </div>
                
                <!-- Content -->
                <div class="p-6 space-y-4">
                  <div class="space-y-3">
                    <div class="flex justify-between text-sm">
                      <span class="text-dark-400">Subtotal</span>
                      <span class="text-dark-200">${{ formatPrice(cartStore.subtotal) }}</span>
                    </div>
                    <div class="flex justify-between text-sm">
                      <span class="text-dark-400">Tax (10%)</span>
                      <span class="text-dark-200">${{ formatPrice(cartStore.tax) }}</span>
                    </div>
                  </div>
                  
                  <!-- Total -->
                  <div class="border-t border-white/20 pt-4">
                    <div class="flex justify-between items-baseline">
                      <span class="text-lg text-dark-200">Total</span>
                      <span class="text-2xl font-bold text-transparent bg-clip-text 
                                 bg-gradient-to-r from-red-400 to-red-600">
                        ${{ formatPrice(cartStore.total) }}
                      </span>
                    </div>
                  </div>

                  <!-- Buttons -->
                  <div class="space-y-3 pt-6">
                    <button @click="checkout"
                            class="w-full inline-flex justify-center items-center px-6 py-3 rounded-lg
                                   text-white font-medium bg-gradient-to-r from-red-500 to-red-600
                                   hover:from-red-600 hover:to-red-700 transform hover:-translate-y-0.5
                                   transition-all duration-300 shadow-lg hover:shadow-red-500/25"
                            :disabled="loading">
                      <span v-if="loading">Processing...</span>
                      <span v-else>Proceed to Checkout</span>
                    </button>
                    
                    <button @click="clearCart"
                            class="w-full px-6 py-3 text-dark-300 hover:text-white font-medium
                                   bg-white/10 backdrop-blur-md shadow-xl rounded-lg 
                                   border border-white/20 hover:border-red-500/30
                                   transition-all duration-300"
                            :disabled="loading">
                      Clear Cart
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty Cart -->
        <div v-else class="max-w-2xl mx-auto">
          <div class="bg-white/10 backdrop-blur-md shadow-xl rounded-xl p-16 text-center
                      border border-white/20">
            <div class="relative mb-8">
              <div class="absolute inset-0 bg-gradient-to-r from-red-500/20 to-red-600/20 blur-3xl opacity-20"></div>
              <i class="fas fa-shopping-cart text-7xl text-dark-600"></i>
            </div>
            <h3 class="text-3xl font-bold text-dark-100 mb-4">Your cart is empty</h3>
            <p class="text-dark-400 text-lg mb-12">Start adding some items to your cart!</p>
            
            <router-link to="/products"
                         class="inline-flex items-center px-8 py-3 rounded-lg text-white font-medium
                                bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700
                                transform hover:-translate-y-0.5 transition-all duration-300
                                shadow-lg hover:shadow-red-500/25">
              Continue Shopping
            </router-link>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cartStore'
import { storeToRefs } from 'pinia'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const cartStore = useCartStore()
const { showToast } = useToast()
const loading = ref(false)
const { state } = storeToRefs(cartStore)

const formatPrice = (price) => {
  return Number(price || 0).toFixed(2)
}

async function updateQuantity(productId, quantity) {
  if (quantity < 1) return
  try {
    loading.value = true
    await cartStore.updateQuantity(productId, quantity)
    await cartStore.fetchCart() // Refresh cart data after update
    showToast('Cart updated successfully')
  } catch (error) {
    const errorMessage = error?.response?.data?.error || error?.message || 'Failed to update quantity'
    showToast(errorMessage, 'error')
    console.error('Error updating quantity:', error)
  } finally {
    loading.value = false
  }
}

async function removeItem(productId) {
  try {
    loading.value = true
    await cartStore.removeItem(productId)
    await cartStore.fetchCart() // Refresh cart data after removal
    showToast('Item removed from cart')
  } catch (error) {
    const errorMessage = error?.response?.data?.error || error?.message || 'Failed to remove item'
    showToast(errorMessage, 'error')
    console.error('Error removing item:', error)
  } finally {
    loading.value = false
  }
}

async function clearCart() {
  try {
    loading.value = true
    await cartStore.clearCart()
    await cartStore.fetchCart() // Refresh cart data after clearing
    showToast('Cart cleared successfully')
  } catch (error) {
    showToast('Failed to clear cart', 'error')
    console.error('Error clearing cart:', error)
  } finally {
    loading.value = false
  }
}

async function checkout() {
  try {
    loading.value = true
    // Add your checkout logic here
    await router.push('/checkout')
  } catch (error) {
    showToast('Failed to proceed to checkout', 'error')
    console.error('Error during checkout:', error)
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
    console.error('Error loading cart:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.animate-spin-slow {
  animation: spin 2s linear infinite;
}
.animate-spin-slower {
  animation: spin 3s linear infinite;
}
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
