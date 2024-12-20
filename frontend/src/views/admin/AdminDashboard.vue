<template>
  <div>
    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div
        v-for="stat in stats"
        :key="stat.name"
        class="bg-white rounded-lg shadow p-6"
      >
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <component
              :is="stat.icon"
              class="h-6 w-6 text-indigo-600"
              aria-hidden="true"
            />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">{{ stat.name }}</p>
            <p class="mt-1 text-2xl font-semibold text-gray-900">
              {{ stat.value }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Orders -->
    <div class="bg-white rounded-lg shadow">
      <div class="px-6 py-4 border-b border-gray-200">
        <h2 class="text-lg font-medium text-gray-900">Recent Orders</h2>
      </div>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th
                v-for="header in tableHeaders"
                :key="header"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                {{ header }}
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="order in recentOrders" :key="order.id">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">#{{ order.id }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ order.customer }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ order.date }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">${{ order.total }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  class="px-2 py-1 text-xs font-medium rounded-full"
                  :class="{
                    'bg-green-100 text-green-800': order.status === 'Completed',
                    'bg-yellow-100 text-yellow-800': order.status === 'Pending',
                    'bg-blue-100 text-blue-800': order.status === 'Processing'
                  }"
                >
                  {{ order.status }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <router-link
                  :to="{ name: 'admin-orders', params: { id: order.id }}"
                  class="text-indigo-600 hover:text-indigo-900"
                >
                  View Details
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const stats = ref([
  {
    name: 'Total Orders',
    value: '156',
    icon: 'ShoppingCartIcon',
  },
  {
    name: 'Total Products',
    value: '48',
    icon: 'ShoppingBagIcon',
  },
  {
    name: 'Active Users',
    value: '2,345',
    icon: 'UsersIcon',
  },
  {
    name: 'Total Revenue',
    value: '$45,678',
    icon: 'CurrencyDollarIcon',
  },
])

const tableHeaders = [
  'Order ID',
  'Customer',
  'Date',
  'Total',
  'Status',
  'Actions'
]

const recentOrders = ref([
  {
    id: '1234',
    customer: 'John Doe',
    date: '2024-12-19',
    total: '125.00',
    status: 'Completed',
  },
  {
    id: '1235',
    customer: 'Jane Smith',
    date: '2024-12-19',
    total: '89.99',
    status: 'Processing',
  },
  {
    id: '1236',
    customer: 'Bob Johnson',
    date: '2024-12-18',
    total: '245.50',
    status: 'Pending',
  },
])
</script>
