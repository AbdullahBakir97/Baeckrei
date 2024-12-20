<template>
  <div class="p-6">
    <div class="sm:flex sm:items-center">
      <div class="sm:flex-auto">
        <h1 class="text-2xl font-semibold text-gray-900">Orders</h1>
        <p class="mt-2 text-sm text-gray-700">A list of all orders placed in your store.</p>
      </div>
    </div>

    <!-- Order Filters -->
    <div class="mt-4 grid grid-cols-1 sm:grid-cols-4 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700">Status</label>
        <select
          v-model="filters.status"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
        >
          <option value="">All</option>
          <option value="pending">Pending</option>
          <option value="processing">Processing</option>
          <option value="shipped">Shipped</option>
          <option value="delivered">Delivered</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700">Date Range</label>
        <input
          type="date"
          v-model="filters.startDate"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
        >
      </div>
      <div class="pt-6">
        <input
          type="date"
          v-model="filters.endDate"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
        >
      </div>
      <div class="pt-6">
        <button
          @click="fetchOrders"
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          Apply Filters
        </button>
      </div>
    </div>

    <!-- Orders Table -->
    <div class="mt-8 flex flex-col">
      <div class="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
        <div class="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8">
          <div class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
            <table class="min-w-full divide-y divide-gray-300">
              <thead class="bg-gray-50">
                <tr>
                  <th scope="col" class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">Order ID</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Customer</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Date</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Status</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Total</th>
                  <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-6">
                    <span class="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 bg-white">
                <tr v-for="order in orders" :key="order.id">
                  <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">
                    #{{ order.id }}
                  </td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                    {{ order.customer_name }}
                  </td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                    {{ new Date(order.created_at).toLocaleDateString() }}
                  </td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm">
                    <span
                      :class="{
                        'px-2 py-1 text-xs font-medium rounded-full': true,
                        'bg-yellow-100 text-yellow-800': order.status === 'pending',
                        'bg-blue-100 text-blue-800': order.status === 'processing',
                        'bg-purple-100 text-purple-800': order.status === 'shipped',
                        'bg-green-100 text-green-800': order.status === 'delivered',
                        'bg-red-100 text-red-800': order.status === 'cancelled'
                      }"
                    >
                      {{ order.status }}
                    </span>
                  </td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                    ${{ order.total.toFixed(2) }}
                  </td>
                  <td class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                    <button
                      @click="openOrderDetails(order)"
                      class="text-indigo-600 hover:text-indigo-900"
                    >
                      View details
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Order Details Modal -->
    <div v-if="selectedOrder" class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center">
      <div class="bg-white rounded-lg p-6 max-w-2xl w-full">
        <div class="flex justify-between items-start">
          <h2 class="text-lg font-medium">Order #{{ selectedOrder.id }}</h2>
          <button
            @click="selectedOrder = null"
            class="text-gray-400 hover:text-gray-500"
          >
            <span class="sr-only">Close</span>
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="mt-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <h3 class="text-sm font-medium text-gray-500">Customer Information</h3>
              <p class="mt-1">{{ selectedOrder.customer_name }}</p>
              <p class="mt-1">{{ selectedOrder.email }}</p>
              <p class="mt-1">{{ selectedOrder.phone }}</p>
            </div>
            <div>
              <h3 class="text-sm font-medium text-gray-500">Shipping Address</h3>
              <p class="mt-1">{{ selectedOrder.shipping_address }}</p>
            </div>
          </div>

          <div class="mt-6">
            <h3 class="text-sm font-medium text-gray-500">Order Items</h3>
            <ul class="mt-2 divide-y divide-gray-200">
              <li v-for="item in selectedOrder.items" :key="item.id" class="py-2 flex justify-between">
                <div>
                  <p class="text-sm font-medium text-gray-900">{{ item.product_name }}</p>
                  <p class="text-sm text-gray-500">Quantity: {{ item.quantity }}</p>
                </div>
                <p class="text-sm font-medium text-gray-900">${{ item.total.toFixed(2) }}</p>
              </li>
            </ul>
          </div>

          <div class="mt-6">
            <h3 class="text-sm font-medium text-gray-500">Update Status</h3>
            <div class="mt-2 flex items-center space-x-4">
              <select
                v-model="selectedOrder.status"
                class="rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              >
                <option value="pending">Pending</option>
                <option value="processing">Processing</option>
                <option value="shipped">Shipped</option>
                <option value="delivered">Delivered</option>
                <option value="cancelled">Cancelled</option>
              </select>
              <button
                @click="updateOrderStatus"
                class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Update
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
import axios from '@/plugins/axios'

const orders = ref([])
const selectedOrder = ref(null)
const filters = ref({
  status: '',
  startDate: '',
  endDate: ''
})

const fetchOrders = async () => {
  try {
    const params = {}
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.startDate) params.start_date = filters.value.startDate
    if (filters.value.endDate) params.end_date = filters.value.endDate

    const response = await axios.get('/orders/', { params })
    orders.value = response.data
  } catch (error) {
    console.error('Error fetching orders:', error)
  }
}

const openOrderDetails = async (order) => {
  try {
    const response = await axios.get(`/orders/${order.id}/`)
    selectedOrder.value = response.data
  } catch (error) {
    console.error('Error fetching order details:', error)
  }
}

const updateOrderStatus = async () => {
  try {
    await axios.patch(`/orders/${selectedOrder.value.id}/`, {
      status: selectedOrder.value.status
    })
    await fetchOrders()
    selectedOrder.value = null
  } catch (error) {
    console.error('Error updating order status:', error)
  }
}

onMounted(() => {
  fetchOrders()
})
</script>
