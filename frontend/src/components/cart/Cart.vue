<template>
  <div class="min-h-screen bg-[rgba(255,255,255,0.02)] backdrop-blur-md py-12 px-4">
    <div class="max-w-7xl mx-auto">
      <!-- Cart Header -->
      <div class="mb-8">
        <h1 class="text-4xl font-extrabold text-white flex items-center gap-3">
          <font-awesome-icon icon="shopping-cart" class="text-amber-500/90" />
          Shopping Cart
        </h1>
        <p class="mt-2 text-gray-400">Your items are listed below</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-white/20"></div>
      </div>

      <!-- Empty Cart -->
      <div v-else-if="!cartStore.itemCount" 
           class="bg-[rgba(255,255,255,0.05)] backdrop-blur-xl shadow-xl rounded-2xl p-12 text-center
                  border border-[rgba(255,255,255,0.1)]">
        <font-awesome-icon icon="shopping-cart" class="text-6xl text-gray-600 mb-4" />
        <h2 class="text-2xl font-bold text-white mb-2">Your cart is empty</h2>
        <p class="text-gray-400 mb-8">Start adding some items to your cart!</p>
        <router-link to="/products"
                     class="inline-flex items-center px-8 py-3 rounded-xl text-white font-medium
                            bg-gradient-to-r from-amber-500/90 to-amber-600/90
                            hover:from-amber-500 hover:to-amber-600
                            transform hover:-translate-y-0.5 transition-all duration-300
                            shadow-lg hover:shadow-amber-500/25">
          Continue Shopping
        </router-link>
      </div>

      <!-- Cart Items -->
      <div v-else class="grid lg:grid-cols-12 gap-8">
        <!-- Cart Items List -->
        <div class="lg:col-span-8 space-y-4">
          <div v-for="item in cartStore.items" 
               :key="item.id"
               class="bg-[rgba(255,255,255,0.05)] backdrop-blur-xl shadow-xl rounded-2xl p-6 
                      border border-[rgba(255,255,255,0.1)] hover:border-amber-500/30
                      transition-all duration-500 ease-in-out group
                      hover:shadow-amber-500/10 hover:bg-[rgba(255,255,255,0.07)]">
            <div class="flex items-center gap-6">
              <!-- Product Image -->
              <div class="w-32 h-32 rounded-xl overflow-hidden bg-[rgba(255,255,255,0.03)] 
                          backdrop-blur-sm shadow-inner group-hover:shadow-amber-500/5
                          transition-all duration-500 ease-in-out">
                <img :src="item.product.image"
                     :alt="item.product.name"
                     class="w-full h-full object-cover transform group-hover:scale-110 
                            transition-transform duration-700 ease-in-out"
                     @error="$event.target.src = '/images/placeholder.png'" />
              </div>

              <!-- Product Info -->
              <div class="flex-1">
                <h3 class="text-xl font-bold text-white mb-2 group-hover:text-amber-500/90
                           transition-colors duration-300">
                  {{ item.product.name }}
                </h3>
                <p class="text-gray-400 text-sm mb-4">
                  {{ item.product.description }}
                </p>
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-4 bg-[rgba(255,255,255,0.02)] p-2 rounded-xl">
                    <button @click="updateQuantity(item, item.quantity - 1)"
                            class="w-8 h-8 rounded-lg bg-[rgba(255,255,255,0.05)] 
                                   hover:bg-amber-500/20 active:bg-amber-500/30
                                   flex items-center justify-center 
                                   transition-all duration-300 ease-in-out
                                   group/btn">
                      <font-awesome-icon icon="minus" 
                                       class="text-gray-400 group-hover/btn:text-white 
                                              transition-colors duration-300" />
                    </button>
                    <span class="text-white font-medium w-6 text-center">{{ item.quantity }}</span>
                    <button @click="updateQuantity(item, item.quantity + 1)"
                            class="w-8 h-8 rounded-lg bg-[rgba(255,255,255,0.05)]
                                   hover:bg-amber-500/20 active:bg-amber-500/30
                                   flex items-center justify-center
                                   transition-all duration-300 ease-in-out
                                   group/btn">
                      <font-awesome-icon icon="plus"
                                       class="text-gray-400 group-hover/btn:text-white
                                              transition-colors duration-300" />
                    </button>
                  </div>
                  <div class="flex items-center gap-6">
                    <span class="text-lg font-bold text-white group-hover:text-amber-500/90
                                 transition-colors duration-300">
                      {{ formatPrice(item.product.price * item.quantity) }}
                    </span>
                    <button @click="removeItem(item)"
                            class="w-8 h-8 rounded-lg bg-[rgba(255,255,255,0.05)]
                                   hover:bg-red-500/20 active:bg-red-500/30
                                   flex items-center justify-center
                                   transition-all duration-300 ease-in-out
                                   group/trash">
                      <font-awesome-icon icon="trash"
                                       class="text-gray-400 group-hover/trash:text-red-400
                                              transition-colors duration-300" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Order Summary -->
        <div class="lg:col-span-4">
          <div class="sticky top-4">
            <div class="bg-[rgba(255,255,255,0.05)] backdrop-blur-xl shadow-xl rounded-2xl p-8 
                      border border-[rgba(255,255,255,0.1)]">
              <h2 class="text-xl font-bold text-white mb-6">
                Order Summary
              </h2>
              <div class="space-y-4">
                <div class="flex justify-between text-gray-400">
                  <span>Subtotal</span>
                  <span>{{ formatPrice(cartStore.subtotal) }}</span>
                </div>
                <div class="flex justify-between text-gray-400">
                  <span>Shipping</span>
                  <span>{{ formatPrice(cartStore.shippingCost) }}</span>
                </div>
                <div class="flex justify-between text-gray-400">
                  <span>Tax</span>
                  <span>{{ formatPrice(cartStore.tax) }}</span>
                </div>
                <div class="h-px bg-[rgba(255,255,255,0.1)] my-4"></div>
                <div class="flex justify-between text-lg font-bold text-white">
                  <span>Total</span>
                  <span>{{ formatPrice(cartStore.total) }}</span>
                </div>
              </div>
              <button @click="checkout"
                      class="w-full mt-8 px-8 py-4 rounded-xl text-white font-medium
                             bg-gradient-to-r from-amber-500/90 to-amber-600/90
                             hover:from-amber-500 hover:to-amber-600
                             transform hover:-translate-y-0.5 transition-all duration-300
                             shadow-lg hover:shadow-amber-500/25">
                Proceed to Checkout
              </button>
            </div>
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
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

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
    await cartStore.updateQuantity(item.product.id, newQuantity)
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
