<template>
  <div class="space-y-8">
    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <!-- Total Products -->
      <div class="bg-[#131B2F] rounded-xl p-6 border border-white/5">
        <div class="flex items-center justify-between">
          <div class="space-y-1">
            <p class="text-sm font-medium text-gray-400">Total Products</p>
            <p class="text-3xl font-bold text-white">{{ stats.totalProducts || 0 }}</p>
          </div>
          <div class="p-4 bg-red-500/10 rounded-xl">
            <i class="fas fa-box text-red-500 text-2xl"></i>
          </div>
        </div>
      </div>

      <!-- Total Orders -->
      <div class="bg-[#131B2F] rounded-xl p-6 border border-white/5">
        <div class="flex items-center justify-between">
          <div class="space-y-1">
            <p class="text-sm font-medium text-gray-400">Total Orders</p>
            <p class="text-3xl font-bold text-white">{{ stats.totalOrders || 0 }}</p>
          </div>
          <div class="p-4 bg-emerald-500/10 rounded-xl">
            <i class="fas fa-shopping-cart text-emerald-500 text-2xl"></i>
          </div>
        </div>
      </div>

      <!-- Total Users -->
      <div class="bg-[#131B2F] rounded-xl p-6 border border-white/5">
        <div class="flex items-center justify-between">
          <div class="space-y-1">
            <p class="text-sm font-medium text-gray-400">Total Users</p>
            <p class="text-3xl font-bold text-white">{{ stats.totalUsers || 0 }}</p>
          </div>
          <div class="p-4 bg-blue-500/10 rounded-xl">
            <i class="fas fa-users text-blue-500 text-2xl"></i>
          </div>
        </div>
      </div>

      <!-- Total Revenue -->
      <div class="bg-[#131B2F] rounded-xl p-6 border border-white/5">
        <div class="flex items-center justify-between">
          <div class="space-y-1">
            <p class="text-sm font-medium text-gray-400">Total Revenue</p>
            <p class="text-3xl font-bold text-white">${{ formatPrice(stats.totalRevenue || 0) }}</p>
          </div>
          <div class="p-4 bg-amber-500/10 rounded-xl">
            <i class="fas fa-dollar-sign text-amber-500 text-2xl"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Recent Orders -->
      <div class="bg-[#131B2F] rounded-xl border border-white/5 overflow-hidden">
        <div class="p-6 border-b border-white/5">
          <h2 class="text-lg font-bold text-white">Recent Orders</h2>
        </div>
        <div class="p-6">
          <div class="space-y-4">
            <div v-if="recentOrders.length === 0" class="text-gray-400 text-center py-4">
              No recent orders
            </div>
            <div v-for="order in recentOrders" 
                 :key="order.id" 
                 class="flex items-center justify-between p-4 bg-[#1A2642] rounded-xl hover:bg-[#1E2A4A] transition-colors">
              <div class="min-w-0">
                <p class="font-medium text-white truncate">Order #{{ order.id }}</p>
                <p class="text-sm text-gray-400 truncate">{{ order.customer }}</p>
              </div>
              <div class="text-right ml-4">
                <p class="font-medium text-white">${{ formatPrice(order.total) }}</p>
                <p class="text-sm" :class="getStatusColor(order.status)">{{ order.status }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Low Stock Products -->
      <div class="bg-[#131B2F] rounded-xl border border-white/5 overflow-hidden">
        <div class="p-6 border-b border-white/5">
          <h2 class="text-lg font-bold text-white">Low Stock Products</h2>
        </div>
        <div class="p-6">
          <div class="space-y-4">
            <div v-if="lowStockProducts.length === 0" class="text-gray-400 text-center py-4">
              No low stock products
            </div>
            <div v-for="product in lowStockProducts" 
                 :key="product.id" 
                 class="flex items-center justify-between p-4 bg-[#1A2642] rounded-xl hover:bg-[#1E2A4A] transition-colors">
              <div class="flex items-center min-w-0">
                <div class="w-12 h-12 rounded-lg overflow-hidden bg-[#0B1120] flex-shrink-0">
                  <img v-if="product.image" 
                       :src="product.image" 
                       :alt="product.name" 
                       class="w-full h-full object-cover">
                  <div v-else class="w-full h-full flex items-center justify-center">
                    <i class="fas fa-image text-gray-700"></i>
                  </div>
                </div>
                <div class="ml-4 min-w-0">
                  <p class="font-medium text-white truncate">{{ product.name }}</p>
                  <p class="text-sm text-red-500">Stock: {{ product.stock }}</p>
                </div>
              </div>
              <button 
                @click="router.push(`/admin/products/${product.id}`)"
                class="ml-4 px-4 py-2 text-sm font-medium text-white bg-red-500 hover:bg-red-600 rounded-lg transition-colors"
              >
                Update Stock
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
import { useRouter } from 'vue-router'
import axios from '@/plugins/axios'

const router = useRouter()
const stats = ref({})
const recentOrders = ref([])
const lowStockProducts = ref([])

const formatPrice = (price) => {
  return Number(price).toFixed(2)
}

const getStatusColor = (status) => {
  const colors = {
    'pending': 'text-amber-500',
    'processing': 'text-blue-500',
    'completed': 'text-emerald-500',
    'cancelled': 'text-red-500'
  }
  return colors[status.toLowerCase()] || 'text-gray-400'
}

const fetchDashboardData = async () => {
  try {
    // Fetch dashboard statistics
    const statsResponse = await axios.get('/api/admin/dashboard/stats/')
    stats.value = statsResponse.data

    // Fetch recent orders
    const ordersResponse = await axios.get('/api/admin/dashboard/recent-orders/')
    recentOrders.value = ordersResponse.data

    // Fetch low stock products
    const productsResponse = await axios.get('/api/admin/dashboard/low-stock/')
    lowStockProducts.value = productsResponse.data
  } catch (error) {
    console.error('Error fetching dashboard data:', error)
  }
}

onMounted(() => {
  fetchDashboardData()
})
</script>
