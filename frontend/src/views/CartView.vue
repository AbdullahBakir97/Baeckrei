<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="bg-white shadow-lg rounded-lg">
      <!-- Cart Header -->
      <div class="px-6 py-4 border-b border-gray-200">
        <h2 class="text-2xl font-semibold text-gray-800">Shopping Cart</h2>
      </div>

      <div v-if="cartStore.isLoading" class="p-6 text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading cart...</p>
      </div>

      <template v-else>
        <!-- Cart Items -->
        <template v-if="!cartStore.cartIsEmpty">
          <div class="divide-y divide-gray-200">
            <div
              v-for="item in cartStore.items"
              :key="item.id"
              class="p-6 flex items-center space-x-4"
            >
              <!-- Product Image -->
              <div class="flex-shrink-0 w-24 h-24">
                <img
                  v-if="item.product.image"
                  :src="item.product.image"
                  :alt="item.product.name"
                  class="w-full h-full object-cover rounded-md"
                />
                <div
                  v-else
                  class="w-full h-full bg-gray-200 rounded-md flex items-center justify-center"
                >
                  <span class="text-gray-400">No image</span>
                </div>
              </div>

              <!-- Product Details -->
              <div class="flex-1">
                <h3 class="text-lg font-medium text-gray-900">
                  <router-link
                    :to="{ name: 'product-detail', params: { id: item.product.id }}"
                    class="hover:text-indigo-600"
                  >
                    {{ item.product.name }}
                  </router-link>
                </h3>
                <p class="mt-1 text-sm text-gray-500">
                  Price: ${{ item.unit_price }}
                </p>
              </div>

              <!-- Quantity Controls -->
              <div class="flex items-center space-x-2">
                <button
                  class="text-gray-500 hover:text-indigo-600 disabled:opacity-50"
                  :disabled="cartStore.isLoading"
                  @click="updateQuantity(item.product.id, item.quantity - 1)"
                >
                  <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"/>
                  </svg>
                </button>

                <span class="text-gray-700 w-8 text-center">{{ item.quantity }}</span>

                <button
                  class="text-gray-500 hover:text-indigo-600 disabled:opacity-50"
                  :disabled="cartStore.isLoading"
                  @click="updateQuantity(item.product.id, item.quantity + 1)"
                >
                  <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
                  </svg>
                </button>
              </div>

              <!-- Item Total -->
              <div class="text-right">
                <p class="text-lg font-medium text-gray-900">
                  ${{ (item.quantity * item.unit_price).toFixed(2) }}
                </p>
              </div>

              <!-- Remove Button -->
              <button
                class="text-gray-400 hover:text-red-500 disabled:opacity-50"
                :disabled="cartStore.isLoading"
                @click="removeItem(item.product.id)"
              >
                <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- Cart Summary -->
          <div class="px-6 py-4 bg-gray-50 rounded-b-lg">
            <div class="flex justify-between items-center">
              <div>
                <p class="text-sm text-gray-600">Subtotal: ${{ cartStore.subtotal.toFixed(2) }}</p>
                <p class="text-sm text-gray-600">Tax (10%): ${{ cartStore.tax.toFixed(2) }}</p>
                <p class="text-lg font-semibold text-gray-900 mt-2">
                  Total: ${{ cartStore.total.toFixed(2) }}
                </p>
              </div>
              <div class="space-x-4">
                <button
                  class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50"
                  :disabled="cartStore.isLoading"
                  @click="clearCart"
                >
                  Clear Cart
                </button>
                <router-link
                  to="/checkout"
                  class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 inline-block"
                >
                  Checkout
                </router-link>
              </div>
            </div>
          </div>
        </template>

        <!-- Empty Cart -->
        <div v-else class="p-6 text-center">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"
            />
          </svg>
          <h3 class="mt-2 text-lg font-medium text-gray-900">Your cart is empty</h3>
          <p class="mt-1 text-sm text-gray-500">Start shopping to add items to your cart.</p>
          <div class="mt-6">
            <router-link
              to="/products"
              class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
            >
              Continue Shopping
            </router-link>
          </div>
        </div>
      </template>
    </div>

    <!-- Error Toast -->
    <div
      v-if="cartStore.error"
      class="fixed bottom-4 right-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded"
      role="alert"
    >
      <span class="block sm:inline">{{ cartStore.error }}</span>
      <button
        @click="cartStore.resetError"
        class="absolute top-0 bottom-0 right-0 px-4 py-3"
      >
        <svg
          class="fill-current h-6 w-6 text-red-500"
          role="button"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
        >
          <title>Close</title>
          <path
            d="M14.348 14.849a1.2 1.2 0 0 1-1.697 0L10 11.819l-2.651 3.029a1.2 1.2 0 1 1-1.697-1.697l2.758-3.15-2.759-3.152a1.2 1.2 0 1 1 1.697-1.697L10 8.183l2.651-3.031a1.2 1.2 0 1 1 1.697 1.697l-2.758 3.152 2.758 3.15a1.2 1.2 0 0 1 0 1.698z"
          />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useCartStore } from '@/stores/cartStore'

const cartStore = useCartStore()

const updateQuantity = async (productId, quantity) => {
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
