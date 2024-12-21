<template>
  <div class="min-h-screen bg-[#0B1120] py-12 px-4">
    <div class="max-w-7xl mx-auto relative">
      <!-- Header -->
      <div class="mb-16 text-center space-y-4">
        <h1 class="text-5xl font-bold text-red-500">
          Shopping Cart
        </h1>
        <p class="text-gray-400">Your items are listed below</p>
      </div>

      <!-- Loading State -->
      <div v-if="cartStore.isLoading" 
           class="flex flex-col items-center justify-center py-32 gap-6">
        <div class="relative w-20 h-20">
          <div class="absolute inset-0 rounded-full border-t-2 border-red-500/30 animate-spin"></div>
          <div class="absolute inset-[4px] rounded-full border-t-2 border-red-500/50 animate-spin-slow"></div>
          <div class="absolute inset-[8px] rounded-full border-t-2 border-red-500/70 animate-spin-slower"></div>
        </div>
        <p class="text-gray-400 animate-pulse font-medium">Loading your cart...</p>
      </div>

      <template v-else>
        <!-- Cart Content -->
        <div v-if="!cartStore.cartIsEmpty" class="grid lg:grid-cols-12 gap-8">
          <!-- Cart Items -->
          <div class="lg:col-span-8 space-y-4">
            <div v-for="item in cartStore.items" 
                 :key="item.id"
                 class="group">
              <div class="bg-[#131B2F] rounded-xl p-6 transition duration-300">
                <div class="flex items-start gap-6">
                  <!-- Product Image -->
                  <div class="w-32 h-32 rounded-lg overflow-hidden bg-[#0B1120]">
                    <img v-if="item.product.image"
                         :src="item.product.image"
                         :alt="item.product.name"
                         class="w-full h-full object-cover transform group-hover:scale-105 transition duration-500" />
                    <div v-else class="w-full h-full flex items-center justify-center">
                      <i class="fas fa-image text-4xl text-gray-700"></i>
                    </div>
                  </div>

                  <!-- Product Details -->
                  <div class="flex-1 min-w-0">
                    <h3 class="text-xl font-medium">
                      <router-link :to="{ name: 'product-detail', params: { id: item.product.id }}"
                                 class="text-white hover:text-red-500 transition-colors">
                        {{ item.product.name }}
                      </router-link>
                    </h3>
                    <div v-if="item.product.stock > 0" class="mt-1 text-sm text-yellow-500">
                      Only {{ item.product.stock }} left in stock!
                    </div>
                    <p class="mt-2 text-gray-400 text-sm line-clamp-2">{{ item.product.description }}</p>

                    <div class="mt-4 flex items-center justify-between">
                      <div class="flex items-center gap-4">
                        <!-- Quantity Controls -->
                        <div class="flex items-center bg-[#0B1120] rounded-lg">
                          <button @click="updateQuantity(item.product.id, item.quantity - 1)"
                                  class="p-2 text-gray-400 hover:text-red-500 disabled:opacity-50 transition-colors"
                                  :disabled="cartStore.isLoading || item.quantity <= 1">
                            <i class="fas fa-minus"></i>
                          </button>
                          <span class="w-12 text-center py-2 text-white">
                            {{ item.quantity }}
                          </span>
                          <button @click="updateQuantity(item.product.id, item.quantity + 1)"
                                  class="p-2 text-gray-400 hover:text-red-500 disabled:opacity-50 transition-colors"
                                  :disabled="cartStore.isLoading">
                            <i class="fas fa-plus"></i>
                          </button>
                        </div>

                        <!-- Remove Button -->
                        <button @click="removeItem(item.product.id)"
                                class="flex items-center gap-2 px-3 py-2 text-sm
                                       text-red-500 hover:text-red-400 transition-colors"
                                :disabled="cartStore.isLoading">
                          <i class="fas fa-trash"></i>
                          <span>Remove</span>
                        </button>
                      </div>

                      <!-- Price -->
                      <div class="text-right">
                        <p class="text-2xl font-bold text-red-500">
                          ${{ formatPrice(item.quantity * item.unit_price) }}
                        </p>
                        <p class="text-sm text-gray-400">
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
              <div class="bg-[#131B2F] rounded-xl overflow-hidden">
                <!-- Header -->
                <div class="px-6 py-4 border-b border-gray-700">
                  <h2 class="text-xl font-bold text-white">
                    Order Summary
                  </h2>
                </div>
                
                <!-- Content -->
                <div class="p-6 space-y-4">
                  <div class="space-y-3">
                    <div class="flex justify-between text-sm">
                      <span class="text-gray-400">Subtotal</span>
                      <span class="text-white">${{ formatPrice(cartStore.subtotal) }}</span>
                    </div>
                    <div class="flex justify-between text-sm">
                      <span class="text-gray-400">Tax (10%)</span>
                      <span class="text-white">${{ formatPrice(cartStore.tax) }}</span>
                    </div>
                  </div>
                  
                  <!-- Total -->
                  <div class="border-t border-gray-700 pt-4">
                    <div class="flex justify-between items-baseline">
                      <span class="text-lg text-white">Total</span>
                      <span class="text-2xl font-bold text-red-500">
                        ${{ formatPrice(cartStore.total) }}
                      </span>
                    </div>
                  </div>

                  <!-- Buttons -->
                  <div class="space-y-3 pt-6">
                    <router-link to="/checkout"
                                class="block w-full px-6 py-3 text-center text-white font-medium
                                       bg-red-500 hover:bg-red-600 rounded-lg transition-colors">
                      Proceed to Checkout
                    </router-link>
                    
                    <button @click="clearCart"
                            class="w-full px-6 py-3 text-gray-400 font-medium
                                   bg-[#0B1120] hover:bg-[#1A2642] rounded-lg
                                   transition-colors"
                            :disabled="cartStore.isLoading">
                      Clear Cart
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty Cart -->
        <div v-else
             class="max-w-2xl mx-auto">
          <div class="bg-[#131B2F] rounded-xl p-16 text-center">
            <div class="relative mb-8">
              <div class="absolute inset-0 bg-gradient-to-r from-red-500/20 to-red-600/20 blur-3xl opacity-20"></div>
              <i class="fas fa-shopping-cart text-7xl text-gray-700 relative"></i>
            </div>
            <h3 class="text-3xl font-bold text-white mb-4">Your cart is empty</h3>
            <p class="text-gray-400 text-lg mb-12">Start adding some items to your cart!</p>
            
            <router-link to="/products"
                         class="inline-block px-8 py-3 text-white font-medium
                                bg-red-500 hover:bg-red-600 rounded-lg transition-colors">
              Continue Shopping
            </router-link>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useCartStore } from '@/stores/cartStore'

const cartStore = useCartStore()

const formatPrice = (price) => {
  return Number(price || 0).toFixed(2)
}

const updateQuantity = async (productId, quantity) => {
  if (quantity < 1) return
  try {
    await cartStore.updateQuantity(productId, quantity)
  } catch (error) {
    console.error('Error updating quantity:', error)
  }
}

const removeItem = async (productId) => {
  try {
    await cartStore.removeItem(productId)
  } catch (error) {
    console.error('Error removing item:', error)
  }
}

const clearCart = async () => {
  try {
    await cartStore.clearCart()
  } catch (error) {
    console.error('Error clearing cart:', error)
  }
}

onMounted(async () => {
  try {
    await cartStore.fetchCart()
  } catch (error) {
    console.error('Error fetching cart:', error)
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
