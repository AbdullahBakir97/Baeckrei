<template>
  <div class="relative">
    <router-link to="/cart" class="p-2 text-gray-600 hover:text-blue-600 relative">
      <span class="sr-only">Shopping cart</span>
      <svg
        class="h-6 w-6"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"
        />
      </svg>
      <span
        v-if="cartStore.itemCount > 0"
        class="absolute -top-1 -right-1 bg-blue-600 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center"
      >
        {{ cartStore.itemCount }}
      </span>
    </router-link>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useCartStore } from '@/stores/cartStore'

const cartStore = useCartStore()

onMounted(async () => {
  try {
    await cartStore.fetchCart()
  } catch (error) {
    console.error('Error fetching cart:', error)
  }
})
</script>
