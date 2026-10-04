<template>
  <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
    <div v-for="stat in stats" :key="stat.name" class="admin-panel overflow-hidden">
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
          <div class="ms-5 w-0 flex-1">
            <dl>
              <dt class="text-sm font-medium text-cream-muted truncate">
                {{ stat.name }}
              </dt>
              <dd class="flex items-baseline">
                <div class="text-2xl font-semibold text-cream">
                  {{ stat.value }}
                </div>
                <div
                  v-if="stat.change"
                  :class="[ stat.changeType === 'increase' ? 'text-emerald-300' : 'text-red-300', 'ms-2 flex items-baseline text-sm font-semibold' ]"
                >
                  <component
                    :is="stat.changeType === 'increase' ? 'ArrowUpIcon' : 'ArrowDownIcon'"
                    class="self-center flex-shrink-0 h-5 w-5"
                    aria-hidden="true"
                  />
                  <span class="sr-only">
                    {{ stat.changeType === 'increase' ? $t('admin.stats.increased') : $t('admin.stats.decreased') }}
                  </span>
                  {{ stat.change }}
                </div>
              </dd>
            </dl>
          </div>
        </div>
      </div>
      <div class="bg-cream/[0.03] px-5 py-3">
        <div class="text-sm">
          <a
            href="#"
            class="font-medium text-primary-700 hover:text-primary-900"
            @click.prevent="$emit('view-details', stat.type)"
          >
            {{ $t('admin.products.viewDetails') }}
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from '@/plugins/axios'
import { formatEuro } from '@/utils/money'
import {
  CurrencyDollarIcon,
  ShoppingBagIcon,
  ExclamationCircleIcon,
  CheckCircleIcon,
  ArrowUpIcon,
  ArrowDownIcon
} from '@heroicons/vue/24/outline'

const emit = defineEmits(['view-details'])
const { t } = useI18n()

const stats = ref([
  {
    type: 'total',
    name: t('admin.stats.total'),
    value: 0,
    icon: ShoppingBagIcon,
    iconColor: 'text-crust'
  },
  {
    type: 'active',
    name: t('admin.stats.active'),
    value: 0,
    icon: CheckCircleIcon,
    iconColor: 'text-emerald-300'
  },
  {
    type: 'low_stock',
    name: t('admin.stats.lowStock'),
    value: 0,
    icon: ExclamationCircleIcon,
    iconColor: 'text-crust-light'
  },
  {
    type: 'stock_value',
    name: t('admin.stats.stockValue'),
    value: formatEuro(0),
    icon: CurrencyDollarIcon,
    iconColor: 'text-crust'
  }
])

const loadStats = async () => {
  try {
    const { data } = await axios.get('/api/products/dashboard_stats/')
    const values = {
      total: data.total_products,
      active: data.active_products,
      low_stock: data.low_stock_count,
      stock_value: formatEuro(data.stock_value)
    }
    stats.value = stats.value.map(stat => ({ ...stat, value: values[stat.type] ?? stat.value }))
  } catch (error) {
    console.error('Error loading stats:', error)
  }
}

onMounted(loadStats)
</script>
