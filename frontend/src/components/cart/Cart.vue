<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">Shopping Cart</h1>

    <!-- Loading State -->
    <div v-if="cartStore.loading" class="grid place-items-center h-96">
      <div class="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
    </div>

    <!-- Empty Cart -->
    <div v-else-if="!cartStore.totalItems" class="text-center py-16">
      <i class="fas fa-shopping-cart text-6xl text-gray-300 mb-4"></i>
      <h2 class="text-2xl font-semibold text-gray-600 mb-4">Your cart is empty</h2>
      <router-link
        to="/products"
        class="btn btn-primary"
      >
        Continue Shopping
      </router-link>
    </div>

    <!-- Cart Items -->
    <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Cart Items List -->
      <div class="lg:col-span-2">
        <div class="space-y-4">
          <div
            v-for="item in cartStore.items"
            :key="item.id"
            class="bg-white rounded-lg shadow p-4"
          >
            <div class="flex items-center gap-4">
              <!-- Product Image -->
              <img
                :src="item.product.image"
                :alt="item.product.name"
                class="w-24 h-24 object-cover rounded"
              >
              
              <!-- Product Info -->
              <div class="flex-grow">
                <h3 class="text-lg font-semibold">
                  <router-link
                    :to="{ name: 'product-detail', params: { id: item.product.id }}"
                    class="hover:text-blue-600"
                  >
                    {{ item.product.name }}
                  </router-link>
                </h3>
                <p class="text-gray-600">{{ item.product.description }}</p>
                <div class="flex items-center justify-between mt-2">
                  <div class="flex items-center gap-4">
                    <!-- Quantity Controls -->
                    <div class="flex items-center border rounded">
                      <button
                        @click="updateQuantity(item, item.quantity - 1)"
                        class="px-3 py-1 hover:bg-gray-100"
                        :disabled="item.quantity <= 1 || loading"
                      >
                        <i class="fas fa-minus"></i>
                      </button>
                      <span class="px-4 py-1 border-x">{{ item.quantity }}</span>
                      <button
                        @click="updateQuantity(item, item.quantity + 1)"
                        class="px-3 py-1 hover:bg-gray-100"
                        :disabled="loading"
                      >
                        <i class="fas fa-plus"></i>
                      </button>
                    </div>
                    <!-- Remove Button -->
                    <button
                      @click="removeItem(item)"
                      class="text-red-500 hover:text-red-600"
                      :disabled="loading"
                    >
                      <i class="fas fa-trash"></i>
                    </button>
                  </div>
                  <div class="text-right">
                    <div class="text-lg font-semibold">
                      ${{ formatPrice(item.total_price) }}
                    </div>
                    <div class="text-sm text-gray-500">
                      ${{ formatPrice(item.unit_price) }} each
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Order Summary -->
      <div class="lg:col-span-1">
        <div class="bg-white rounded-lg shadow p-6 sticky top-4">
          <h2 class="text-xl font-semibold mb-4">Order Summary</h2>
          <div class="space-y-2 mb-4">
            <div class="flex justify-between">
              <span>Subtotal</span>
              <span>${{ formatPrice(cartStore.subtotal) }}</span>
            </div>
            <div class="flex justify-between">
              <span>Tax</span>
              <span>${{ formatPrice(cartStore.tax) }}</span>
            </div>
            <div class="border-t pt-2 mt-2">
              <div class="flex justify-between font-semibold text-lg">
                <span>Total</span>
                <span>${{ formatPrice(cartStore.total) }}</span>
              </div>
            </div>
          </div>
          <button
            @click="checkout"
            class="btn btn-primary w-full"
            :disabled="loading"
          >
            Proceed to Checkout
          </button>
          <router-link
            to="/products"
            class="btn btn-secondary w-full mt-2"
          >
            Continue Shopping
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useCartStore } from '@/stores/cartStore'

const cartStore = useCartStore()
const loading = ref(false)

const formatPrice = (price) => {
  return price.toFixed(2)
}

const updateQuantity = async (item, newQuantity) => {
  if (newQuantity < 1) return
  
  try {
    loading.value = true
    await cartStore.updateQuantity(item.product.id, newQuantity)
  } catch (error) {
    console.error('Failed to update quantity:', error)
    // Handle error (show error toast, etc.)
  } finally {
    loading.value = false
  }
}

const removeItem = async (item) => {
  try {
    loading.value = true
    await cartStore.removeFromCart(item.product.id)
  } catch (error) {
    console.error('Failed to remove item:', error)
    // Handle error (show error toast, etc.)
  } finally {
    loading.value = false
  }
}

const checkout = () => {
  // TODO: Implement checkout functionality
  console.log('Proceeding to checkout...')
}

onMounted(() => {
  cartStore.fetchCart()
})
</script>

<style scoped>
.btn {
  @apply px-4 py-2 rounded-lg font-medium transition-colors;
}

.btn-primary {
  @apply bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50;
}

.btn-secondary {
  @apply bg-gray-100 text-gray-800 hover:bg-gray-200;
}
</style>
