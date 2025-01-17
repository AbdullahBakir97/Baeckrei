<template>
  <div class="max-w-2xl mx-auto">
    <div class="empty-cart">
      <div class="relative p-16 text-center">
        <div class="absolute inset-0 bg-gradient-to-r from-amber-500/20 to-amber-600/20 blur-3xl opacity-20"></div>
        <div class="relative mb-8">
          <font-awesome-icon icon="shopping-cart" class="text-7xl text-gray-600" />
        </div>
        <h3 class="text-3xl font-bold text-white mb-4">Your cart is empty</h3>
        <p class="text-gray-400 text-lg mb-12">Start adding some items to your cart!</p>
      
        <router-link to="/products"
                     class="continue-shopping-btn">
          Continue Shopping
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
</script>

<style scoped>
.empty-cart {
  @apply rounded-lg transition-all duration-300;
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.continue-shopping-btn {
  @apply inline-flex items-center px-8 py-3 rounded-lg text-white font-medium
         transform hover:-translate-y-0.5 transition-all duration-300
         shadow-lg hover:shadow-amber-500/25;
  background: linear-gradient(to right, rgba(245, 158, 11, 0.9), rgba(217, 119, 6, 0.9));
}
</style>
