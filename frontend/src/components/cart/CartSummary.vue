<template>
  <div class="bg-[rgba(255,255,255,0.05)] backdrop-blur-xl shadow-xl rounded-2xl p-8 
              border border-[rgba(255,255,255,0.1)]">
    <h2 class="text-xl font-bold text-white mb-6">
      Order Summary
    </h2>
    <div class="space-y-4">
      <div class="flex justify-between">
        <span class="text-gray-400">Subtotal</span>
        <span class="text-gray-400">
          {{ formatPrice(cartStore.subtotal) }} €
        </span>
      </div>
      <div class="flex justify-between">
        <span class="text-gray-400">Shipping</span>
        <span class="text-gray-400">
          {{ formatPrice(cartStore.shipping || 0) }} €
        </span>
      </div>
      <div class="flex justify-between">
        <span class="text-gray-400">Tax</span>
        <span class="text-gray-400">
          {{ formatPrice(cartStore.tax) }} €
        </span>
      </div>
      <div class="h-px bg-[rgba(255,255,255,0.1)] my-4"></div>
      <div class="flex justify-between text-lg font-bold">
        <span class="text-white">Total</span>
        <span class="text-2xl text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-amber-600">
          {{ formatPrice(cartStore.total) }} €
        </span>
      </div>
    </div>
    <button @click="$emit('checkout')"
            :disabled="cartStore.loading"
            class="w-full mt-8 px-8 py-4 rounded-xl text-white font-medium
                   bg-gradient-to-r from-amber-500/90 to-amber-600/90
                   hover:from-amber-500 hover:to-amber-600
                   transform hover:-translate-y-0.5 transition-all duration-300
                   shadow-lg hover:shadow-amber-500/25
                   disabled:opacity-50 disabled:cursor-not-allowed">
      Proceed to Checkout
    </button>
    <button @click="$emit('clear-cart')"
            :disabled="cartStore.loading"
            class="w-full mt-4 px-6 py-3 text-gray-400 hover:text-white font-medium rounded-lg
                   transition-all duration-300
                   bg-[rgba(255,255,255,0.03)] backdrop-blur-sm
                   border border-[rgba(255,255,255,0.1)]
                   hover:border-amber-500/30
                   disabled:opacity-50 disabled:cursor-not-allowed">
      Clear Cart
    </button>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useCartStore } from '@/stores/cartStore'

const cartStore = useCartStore()

function formatPrice(price) {
  return Number(price || 0).toFixed(2)
}

onMounted(async () => {
  try {
    await cartStore.fetchCart()
  } catch (error) {
    console.error('Error fetching cart:', error)
  }
})
</script>
