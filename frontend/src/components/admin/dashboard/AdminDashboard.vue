<template>
  <div class="space-y-8">
    <p v-if="loadError" class="rounded-lg bg-red-50 p-3 text-sm text-red-700" role="alert">{{ loadError }}</p>
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
            <font-awesome-icon icon="box-open" class="text-red-500 text-2xl" />
          </div>
        </div>
      </div>

      <!-- Total Orders -->
      <div class="bg-[#131B2F] rounded-xl p-6 border border-white/5">
        <div class="flex items-center justify-between">
          <div class="space-y-1">
            <p class="text-sm font-medium text-gray-400">Total Orders</p>
            <p class="text-3xl font-bold text-white">{{ stats.totalOrders || 0 }}</p>
            <p class="text-xs text-gray-400">{{ stats.openOrders || 0 }} open</p>
          </div>
          <div class="p-4 bg-emerald-500/10 rounded-xl">
            <font-awesome-icon icon="shopping-cart" class="text-emerald-500 text-2xl" />
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
            <font-awesome-icon icon="user" class="text-blue-500 text-2xl" />
          </div>
        </div>
      </div>

      <!-- Total Revenue -->
      <div class="bg-[#131B2F] rounded-xl p-6 border border-white/5">
        <div class="flex items-center justify-between">
          <div class="space-y-1">
            <p class="text-sm font-medium text-gray-400">Total Revenue</p>
            <p class="text-3xl font-bold text-white">{{ formatPrice(stats.totalRevenue || 0) }} €</p>
            <p class="text-xs text-gray-400">Completed orders</p>
          </div>
          <div class="p-4 bg-amber-500/10 rounded-xl">
            <font-awesome-icon icon="money-bill" class="text-amber-500 text-2xl" />
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
            <router-link v-for="order in recentOrders"
                 :key="order.id"
                 :to="{ name: 'admin-orders', query: { order: order.id } }"
                 class="flex items-center justify-between p-4 bg-[#1A2642] rounded-xl hover:bg-[#1E2A4A] transition-colors">
              <div class="min-w-0">
                <p class="font-medium text-white truncate">{{ order.order_number }}</p>
                <p class="text-sm text-gray-400 truncate">{{ order.customer_email }} · {{ order.fulfillment_method === 'pickup' ? 'Pickup' : 'Delivery' }}</p>
              </div>
              <div class="text-right ml-4">
                <p class="font-medium text-white">{{ formatPrice(order.total) }} €</p>
                <p class="text-sm" :class="getStatusColor(order.status)">{{ order.status }}</p>
              </div>
            </router-link>
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
                    <font-awesome-icon icon="box-open" class="text-gray-600" />
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
                Update stock
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
    'canceled': 'text-red-500'
  }
  return colors[status.toLowerCase()] || 'text-gray-400'
}

const loadError = ref('')

// Each panel loads on its own, so one failing endpoint doesn't blank the page.
const fetchDashboardData = async () => {
  const [productsStats, ordersStats, usersStats, recentOrdersData, lowStockData] = await Promise.allSettled([
    axios.get('/api/products/dashboard_stats/'),
    axios.get('/api/orders/orders/dashboard_stats/'),
    axios.get('/api/accounts/users/dashboard_stats/'),
    axios.get('/api/orders/orders/recent_orders/'),
    axios.get('/api/products/low_stock/')
  ])
  const data = (result) => (result.status === 'fulfilled' ? result.value.data : null)
  const products = data(productsStats) || {}
  const orders = data(ordersStats) || {}
  const users = data(usersStats) || {}

  stats.value = {
    totalProducts: products.total_products,
    lowStockCount: products.low_stock_count,
    totalOrders: orders.total_orders,
    openOrders: orders.open_orders,
    totalRevenue: orders.total_revenue,
    todayOrders: orders.today_orders,
    todayRevenue: orders.today_revenue,
    totalUsers: users.total_users,
    todayUsers: users.today_users
  }
  recentOrders.value = data(recentOrdersData) || []
  lowStockProducts.value = data(lowStockData) || []

  const failed = [productsStats, ordersStats, usersStats, recentOrdersData, lowStockData]
    .filter(r => r.status === 'rejected').length
  loadError.value = failed ? 'Some dashboard figures could not be loaded.' : ''
}

onMounted(() => {
  fetchDashboardData()
})
</script>
