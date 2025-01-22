<template>
  <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
    <div v-for="stat in stats" :key="stat.name" class="bg-white overflow-hidden shadow rounded-lg">
      <div class="p-5">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <component
              :is="stat.icon"
              class="h-6 w-6"
              :class="stat.iconColor"
              aria-hidden="true"
            />
          </div>
          <div class="ml-5 w-0 flex-1">
            <dl>
              <dt class="text-sm font-medium text-gray-500 truncate">
                {{ stat.name }}
              </dt>
              <dd class="flex items-baseline">
                <div class="text-2xl font-semibold text-gray-900">
                  {{ stat.value }}
                </div>
                <div
                  v-if="stat.change"
                  :class="[
                    stat.changeType === 'increase' ? 'text-green-600' : 'text-red-600',
                    'ml-2 flex items-baseline text-sm font-semibold'
                  ]"
                >
                  <component
                    :is="stat.changeType === 'increase' ? 'ArrowUpIcon' : 'ArrowDownIcon'"
                    class="self-center flex-shrink-0 h-5 w-5"
                    aria-hidden="true"
                  />
                  <span class="sr-only">
                    {{ stat.changeType === 'increase' ? 'Increased' : 'Decreased' }} by
                  </span>
                  {{ stat.change }}
                </div>
              </dd>
            </dl>
          </div>
        </div>
      </div>
      <div class="bg-gray-50 px-5 py-3">
        <div class="text-sm">
          <a
            href="#"
            class="font-medium text-primary-700 hover:text-primary-900"
            @click.prevent="$emit('view-details', stat.type)"
          >
            View details
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useProductStore } from '@/stores/productStore'
import {
  CurrencyDollarIcon,
  ShoppingBagIcon,
  ExclamationCircleIcon,
  CheckCircleIcon,
  ArrowUpIcon,
  ArrowDownIcon
} from '@heroicons/vue/24/outline'

const productStore = useProductStore()
const emit = defineEmits(['view-details'])

const stats = ref([
  {
    type: 'total',
    name: 'Total Products',
    value: 0,
    icon: ShoppingBagIcon,
    iconColor: 'text-purple-500'
  },
  {
    type: 'active',
    name: 'Active Products',
    value: 0,
    icon: CheckCircleIcon,
    iconColor: 'text-green-500'
  },
  {
    type: 'low_stock',
    name: 'Low Stock Items',
    value: 0,
    icon: ExclamationCircleIcon,
    iconColor: 'text-yellow-500'
  },
  {
    type: 'revenue',
    name: 'Total Revenue',
    value: '$0',
    icon: CurrencyDollarIcon,
    iconColor: 'text-blue-500'
  }
])

const loadStats = async () => {
  try {
    const report = await productStore.fetchReport()
    stats.value = stats.value.map(stat => {
      switch (stat.type) {
        case 'total':
          return { ...stat, value: report.total_products }
        case 'active':
          return { ...stat, value: report.active_products }
        case 'low_stock':
          return { ...stat, value: report.low_stock_items }
        case 'revenue':
          return { ...stat, value: `$${report.total_revenue.toLocaleString()}` }
        default:
          return stat
      }
    })
  } catch (error) {
    console.error('Error loading stats:', error)
  }
}

onMounted(loadStats)
</script>
