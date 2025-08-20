<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Header Section -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold bg-gradient-to-r from-amber-400 to-amber-600 bg-clip-text text-transparent">
        My Orders
      </h1>
      <p class="text-gray-400 mt-2">Track and manage your orders</p>
    </div>

    <!-- Loading State -->
    <div v-if="orderStore.loading" class="grid place-items-center h-96">
      <div class="text-6xl text-primary-600">
        <font-awesome-icon icon="spinner" class="animate-spin" />
      </div>
      <p class="mt-4 text-gray-400">Loading your orders...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="orderStore.error" class="text-center py-12">
      <font-awesome-icon icon="circle-xmark" class="text-4xl text-red-500 mb-4" />
      <p class="text-lg text-gray-600">{{ orderStore.error }}</p>
      <button @click="loadOrders" class="btn btn-primary mt-4">
        <font-awesome-icon icon="rotate" class="mr-2" />
        Try Again
      </button>
    </div>

    <!-- No Orders State -->
    <div v-else-if="!orderStore.hasOrders" class="text-center py-12 bg-[rgba(23,23,23,0.7)] backdrop-blur-[10px] 
                border border-white/10 rounded-xl p-6">
      <font-awesome-icon icon="shopping-bag" class="text-6xl text-gray-400 mb-4" />
      <h2 class="text-2xl font-semibold text-gray-300 mb-2">No Orders Yet</h2>
      <p class="text-gray-400 mb-6">Start shopping to create your first order</p>
      <router-link to="/products" class="btn btn-primary">
        <font-awesome-icon icon="shopping-cart" class="mr-2" />
        Browse Products
      </router-link>
    </div>

    <!-- Orders List -->
    <div v-else class="space-y-6">
      <div v-for="order in orderStore.orders" :key="order.id" 
           class="bg-[rgba(23,23,23,0.7)] backdrop-blur-[10px] border border-white/10 
                  rounded-xl p-6 transition-all duration-300 hover:border-amber-500/30
                  hover:shadow-lg hover:shadow-amber-500/10">
        <!-- Order Header -->
        <div class="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-white/10">
          <div>
            <h3 class="text-xl font-semibold text-gray-200">
              Order #{{ order.order_number }}
            </h3>
            <p class="text-sm text-gray-400">
              Placed on {{ formatDate(order.created_at) }}
            </p>
          </div>
          <div class="flex items-center gap-4">
            <span :class="[
              'tag',
              order.status === 'Completed' ? 'bg-green-500/20 text-green-300' :
              order.status === 'Processing' ? 'bg-blue-500/20 text-blue-300' :
              order.status === 'Canceled' ? 'bg-red-500/20 text-red-300' :
              'bg-yellow-500/20 text-yellow-300'
            ]">
              {{ order.status }}
            </span>
            <span class="text-xl font-bold text-transparent bg-clip-text 
                       bg-gradient-to-r from-amber-400 to-amber-600">
              {{ formatPrice(order.total_price) }} €
            </span>
          </div>
        </div>

        <!-- Order Items -->
        <div class="py-4 space-y-4">
          <div v-for="item in order.order_items" :key="item.id"
               class="flex items-center gap-4 p-3 rounded-lg bg-[rgba(255,255,255,0.02)]
                      hover:bg-[rgba(255,255,255,0.05)] transition-all duration-300">
            <!-- Product Image -->
            <div class="w-16 h-16 rounded-lg overflow-hidden bg-[rgba(255,255,255,0.02)]">
              <img :src="getImageUrl(item.product.image)" 
                   :alt="item.product.name"
                   class="w-full h-full object-cover" />
            </div>
            
            <!-- Product Info -->
            <div class="flex-grow">
              <h4 class="text-gray-200 font-medium">{{ item.product.name }}</h4>
              <p class="text-sm text-gray-400">
                Quantity: {{ item.quantity }} × {{ formatPrice(item.price_per_item) }} €
              </p>
            </div>
            
            <!-- Item Total -->
            <div class="text-right">
              <p class="font-medium text-amber-500">
                {{ formatPrice(item.quantity * item.price_per_item) }} €
              </p>
            </div>
          </div>
        </div>

        <!-- Order Footer -->
        <div class="pt-4 border-t border-white/10">
          <div class="flex flex-wrap items-center justify-between gap-4">
            <!-- Shipping Info -->
            <div class="text-sm text-gray-400">
              <p class="flex items-center gap-2">
                <font-awesome-icon icon="truck" />
                {{ order.shipping_tracking_number || 'Tracking number pending' }}
              </p>
              <p class="flex items-center gap-2 mt-1">
                <font-awesome-icon icon="calendar" />
                Estimated delivery: {{ formatDate(order.estimated_delivery_date) }}
              </p>
            </div>
            
            <!-- Actions -->
            <div class="flex items-center gap-3">
              <button v-if="order.status === 'Pending'"
                      @click="cancelOrder(order.id)"
                      class="btn bg-red-500/20 text-red-300 hover:bg-red-500/30">
                <font-awesome-icon icon="times" class="mr-2" />
                Cancel Order
              </button>
              <button @click="trackOrder(order.shipping_tracking_number)"
                      :disabled="!order.shipping_tracking_number"
                      class="btn bg-[rgba(255,255,255,0.05)] text-gray-300 
                             hover:bg-[rgba(255,255,255,0.1)]">
                <font-awesome-icon icon="location-dot" class="mr-2" />
                Track Order
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
import { useToast } from '@/composables/useToast'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { useOrderStore } from '@/stores/orderStore'

// Store
const orderStore = useOrderStore()
const { showToast } = useToast()

// Methods
const loadOrders = async () => {
  try {
    await orderStore.fetchOrders()
  } catch (err) {
    console.error('Error loading orders:', err)
  }
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const formatPrice = (price) => {
  return Number(price).toFixed(2)
}

const getImageUrl = (path) => {
  if (!path) return '/images/placeholder.png'
  if (path.startsWith('http')) return path
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
  return `${API_URL}${path}`
}

const cancelOrder = async (orderId) => {
  try {
    await orderStore.cancelOrder(orderId)
    showToast('Order cancelled successfully', 'success')
  } catch (err) {
    showToast('Failed to cancel order', 'error')
    console.error('Error cancelling order:', err)
  }
}

const trackOrder = (trackingNumber) => {
  if (!trackingNumber) {
    showToast('Tracking number not available yet', 'warning')
    return
  }
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
  window.open(`${API_URL}/track/${trackingNumber}`, '_blank')
}

// Lifecycle
onMounted(() => {
  loadOrders()
})
</script>

<style scoped>
.tag {
  @apply px-3 py-1 rounded-full text-sm font-medium;
}

.btn {
  @apply px-4 py-2 rounded-lg font-medium transition-all duration-300
         flex items-center justify-center gap-2;
}

.btn:disabled {
  @apply opacity-50 cursor-not-allowed;
}

.info-card {
  @apply bg-[rgba(23,23,23,0.7)] backdrop-blur-[10px] 
         border border-white/10 rounded-xl p-6 
         transition-all duration-500 ease-in-out;
  
  box-shadow: 0 0 20px 0 rgba(0, 0, 0, 0.5),
              inset 0 0 0 1px rgba(255, 255, 255, 0.1);

  &:hover {
    @apply border-amber-500/30;
    box-shadow: 
      0 8px 32px rgba(0, 0, 0, 0.1),
      0 4px 8px rgba(245, 158, 11, 0.2);
  }
}
</style>