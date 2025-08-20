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

      <template v-else>
        <!-- Cart Content -->
        <div v-if="cartStore.items.length > 0" class="grid lg:grid-cols-12 gap-8">
          <!-- Cart Items -->
          <div class="lg:col-span-8 space-y-4">
            <CartItem v-for="item in cartStore.items" 
                     :key="item.id"
                     :product="item.product"
                     :quantity="item.quantity"
                     :unit-price="item.unitPrice"
                     :total-price="item.totalPrice"
                     :loading="loading"
                     @update-quantity="updateQuantity"
                     @remove-item="removeItem"
                     class="bg-[rgba(255,255,255,0.05)] backdrop-blur-xl shadow-xl rounded-2xl p-6 
                            border border-[rgba(255,255,255,0.1)] hover:border-amber-500/30
                            transition-all duration-500 ease-in-out group
                            hover:shadow-amber-500/10 hover:bg-[rgba(255,255,255,0.07)]" />
          </div>

          <!-- Order Summary -->
          <div class="lg:col-span-4">
            <div class="sticky top-4">
              <CartSummary 
                :subtotal="cartStore.subtotal"
                :tax="cartStore.tax"
                :total="cartStore.total"
                :loading="loading"
                @checkout="checkout"
                @clear-cart="clearCart" />
            </div>
          </div>
        </div>

        <!-- Empty Cart -->
        <EmptyCart v-else class="bg-[rgba(255,255,255,0.05)] backdrop-blur-xl shadow-xl rounded-2xl p-12 text-center
                                border border-[rgba(255,255,255,0.1)]" />
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
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import CartItem from '@/components/cart/CartItem.vue'
import CartSummary from '@/components/cart/CartSummary.vue'
import EmptyCart from '@/components/cart/EmptyCart.vue'

const router = useRouter()
const cartStore = useCartStore()
const { showToast } = useToast()
const loading = ref(false)
const { state } = storeToRefs(cartStore)

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
