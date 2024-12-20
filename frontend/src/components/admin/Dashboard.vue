<template>
  <div class="p-6">
    <h1 class="text-2xl font-semibold text-gray-900 mb-6">Dashboard</h1>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- Products Stats -->
      <div class="bg-white p-6 rounded-lg shadow">
        <h3 class="text-lg font-medium text-gray-900">Products</h3>
        <p class="text-3xl font-bold text-indigo-600 mt-2">{{ stats.products }}</p>
        <router-link 
          to="/admin/products"
          class="text-sm text-indigo-600 hover:text-indigo-900 mt-2 inline-block"
        >
          View all products →
        </router-link>
      </div>

      <!-- Categories Stats -->
      <div class="bg-white p-6 rounded-lg shadow">
        <h3 class="text-lg font-medium text-gray-900">Categories</h3>
        <p class="text-3xl font-bold text-indigo-600 mt-2">{{ stats.categories }}</p>
        <router-link 
          to="/admin/categories"
          class="text-sm text-indigo-600 hover:text-indigo-900 mt-2 inline-block"
        >
          View all categories →
        </router-link>
      </div>

      <!-- Orders Stats -->
      <div class="bg-white p-6 rounded-lg shadow">
        <h3 class="text-lg font-medium text-gray-900">Orders</h3>
        <p class="text-3xl font-bold text-indigo-600 mt-2">{{ stats.orders }}</p>
        <router-link 
          to="/admin/orders"
          class="text-sm text-indigo-600 hover:text-indigo-900 mt-2 inline-block"
        >
          View all orders →
        </router-link>
      </div>
    </div>

    <!-- Recent Products -->
    <div class="mt-8">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Recent Products</h2>
      <div class="bg-white shadow overflow-hidden sm:rounded-md">
        <ul class="divide-y divide-gray-200">
          <li v-for="product in recentProducts" :key="product.id">
            <div class="px-4 py-4 sm:px-6">
              <div class="flex items-center justify-between">
                <div class="flex items-center">
                  <img 
                    :src="product.image" 
                    :alt="product.name"
                    class="h-10 w-10 rounded-full object-cover"
                  >
                  <p class="ml-4 text-sm font-medium text-indigo-600">{{ product.name }}</p>
                </div>
                <div class="ml-2 flex-shrink-0">
                  <p class="text-sm text-gray-600">{{ product.price }}</p>
                </div>
              </div>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from '@/plugins/axios'

const stats = ref({
  products: 0,
  categories: 0,
  orders: 0
})

const recentProducts = ref([])

const fetchStats = async () => {
  try {
    const response = await axios.get('/admin/stats/')
    stats.value = response.data
  } catch (error) {
    console.error('Error fetching stats:', error)
  }
}

const fetchRecentProducts = async () => {
  try {
    const response = await axios.get('/products/', {
      params: {
        page: 1,
        page_size: 5,
        sort: '-created_at'
      }
    })
    recentProducts.value = response.data.results
  } catch (error) {
    console.error('Error fetching recent products:', error)
  }
}

onMounted(() => {
  fetchStats()
  fetchRecentProducts()
})
</script>
