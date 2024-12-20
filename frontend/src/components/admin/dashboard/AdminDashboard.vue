<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">Admin Dashboard</h1>
    
    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <!-- Total Products -->
      <div class="card bg-white p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Total Products</p>
            <p class="text-2xl font-semibold text-gray-900">{{ stats.totalProducts || 0 }}</p>
          </div>
          <div class="p-3 bg-primary-100 rounded-full">
            <i class="fas fa-box text-primary-600 text-xl"></i>
          </div>
        </div>
      </div>

      <!-- Total Orders -->
      <div class="card bg-white p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Total Orders</p>
            <p class="text-2xl font-semibold text-gray-900">{{ stats.totalOrders || 0 }}</p>
          </div>
          <div class="p-3 bg-green-100 rounded-full">
            <i class="fas fa-shopping-cart text-green-600 text-xl"></i>
          </div>
        </div>
      </div>

      <!-- Total Users -->
      <div class="card bg-white p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Total Users</p>
            <p class="text-2xl font-semibold text-gray-900">{{ stats.totalUsers || 0 }}</p>
          </div>
          <div class="p-3 bg-blue-100 rounded-full">
            <i class="fas fa-users text-blue-600 text-xl"></i>
          </div>
        </div>
      </div>

      <!-- Total Revenue -->
      <div class="card bg-white p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Total Revenue</p>
            <p class="text-2xl font-semibold text-gray-900">${{ formatPrice(stats.totalRevenue || 0) }}</p>
          </div>
          <div class="p-3 bg-yellow-100 rounded-full">
            <i class="fas fa-dollar-sign text-yellow-600 text-xl"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Recent Orders -->
      <div class="card bg-white p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Recent Orders</h2>
        <div class="space-y-4">
          <div v-if="recentOrders.length === 0" class="text-gray-500 text-center py-4">
            No recent orders
          </div>
          <div v-for="order in recentOrders" :key="order.id" class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <p class="font-medium text-gray-900">Order #{{ order.id }}</p>
              <p class="text-sm text-gray-600">{{ order.customer }}</p>
            </div>
            <div class="text-right">
              <p class="font-medium text-gray-900">${{ formatPrice(order.total) }}</p>
              <p class="text-sm" :class="getStatusColor(order.status)">{{ order.status }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Low Stock Products -->
      <div class="card bg-white p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Low Stock Products</h2>
        <div class="space-y-4">
          <div v-if="lowStockProducts.length === 0" class="text-gray-500 text-center py-4">
            No low stock products
          </div>
          <div v-for="product in lowStockProducts" :key="product.id" class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div class="flex items-center">
              <img :src="product.image" :alt="product.name" class="w-12 h-12 object-cover rounded-md mr-4">
              <div>
                <p class="font-medium text-gray-900">{{ product.name }}</p>
                <p class="text-sm text-gray-600">Stock: {{ product.stock }}</p>
              </div>
            </div>
            <button 
              @click="router.push(`/admin/products/${product.id}`)"
              class="btn btn-secondary btn-sm"
            >
              Update Stock
            </button>
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
    'pending': 'text-yellow-600',
    'processing': 'text-blue-600',
    'completed': 'text-green-600',
    'cancelled': 'text-red-600'
  }
  return colors[status.toLowerCase()] || 'text-gray-600'
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
