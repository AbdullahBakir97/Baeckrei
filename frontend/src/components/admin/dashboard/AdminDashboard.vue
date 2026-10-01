<template>
  <div class="space-y-8">
    <p v-if="loadError" class="rounded-2xl bg-red-400/10 p-3 text-sm text-red-300" role="alert">{{ loadError }}</p>

    <!-- Greeting -->
    <section class="dash-hero admin-panel">
      <div>
        <p class="eyebrow">{{ greeting }}</p>
        <i18n-t keypath="admin.dashboard.headline" tag="h2" class="display-title text-4xl sm:text-5xl mt-2" scope="global">
          <template #orders>{{ $t('admin.dashboard.ordersToday', stats.todayOrders || 0) }}</template>
          <template #revenue><em class="text-crust">{{ formatEuro(stats.todayRevenue) }}</em></template>
        </i18n-t>
        <p class="mt-2 text-cream-muted">{{ $t('admin.dashboard.openAttention', stats.openOrders || 0) }}</p>
      </div>
      <div class="flex flex-wrap gap-2">
        <router-link :to="{ name: 'admin-orders' }" class="btn-amber !py-2.5 !px-5">{{ $t('admin.dashboard.openOrders') }} <font-awesome-icon icon="arrow-right" /></router-link>
        <router-link :to="{ name: 'admin-products' }" class="btn-ghost !py-2.5 !px-5">{{ $t('admin.nav.products') }}</router-link>
      </div>
    </section>

    <!-- KPIs -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div v-for="kpi in kpis" :key="kpi.label" class="kpi admin-panel">
        <div class="flex items-center justify-between">
          <p class="text-sm text-cream-muted">{{ kpi.label }}</p>
          <span class="kpi-icon"><font-awesome-icon :icon="kpi.icon" /></span>
        </div>
        <p class="kpi-value">{{ kpi.value }}</p>
        <p class="text-xs text-cream-faint">{{ kpi.note }}</p>
      </div>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
      <!-- Recent orders -->
      <section class="admin-panel overflow-hidden">
        <header class="dash-head">
          <h2 class="display-title text-3xl">{{ $t('admin.dashboard.recentOrders') }}</h2>
          <router-link :to="{ name: 'admin-orders' }" class="text-sm text-crust hover:text-crust-light">{{ $t('admin.dashboard.allOrders') }}</router-link>
        </header>
        <p v-if="!recentOrders.length" class="p-6 text-center text-cream-faint">{{ $t('admin.dashboard.noOrders') }}</p>
        <ul v-else>
          <li v-for="order in recentOrders" :key="order.id">
            <router-link :to="{ name: 'admin-orders', query: { order: order.id } }" class="dash-row">
              <span class="dash-avatar">{{ (order.customer_email || '?').charAt(0).toUpperCase() }}</span>
              <span class="min-w-0 flex-1">
                <span class="block truncate font-medium text-cream">{{ order.order_number }}</span>
                <span class="block truncate text-sm text-cream-faint">
                  {{ order.customer_email || $t('admin.dashboard.guest') }} · {{ order.fulfillment_method === 'pickup' ? $t('common.pickup') : $t('common.delivery') }}
                </span>
              </span>
              <span class="text-right">
                <span class="block font-semibold text-cream tabular-nums">{{ formatEuro(order.total) }}</span>
                <span class="status" :class="`is-${order.status.toLowerCase()}`">{{ $t(`common.status.${order.status.toLowerCase()}`) }}</span>
              </span>
            </router-link>
          </li>
        </ul>
      </section>

      <!-- Low stock -->
      <section class="admin-panel overflow-hidden">
        <header class="dash-head">
          <h2 class="display-title text-3xl">{{ $t('admin.dashboard.runningLow') }}</h2>
          <span class="text-sm text-cream-faint">{{ $t('common.products', lowStockProducts.length) }}</span>
        </header>
        <p v-if="!lowStockProducts.length" class="p-6 text-center text-cream-faint">{{ $t('admin.dashboard.wellStocked') }}</p>
        <ul v-else>
          <li v-for="product in lowStockProducts" :key="product.id" class="dash-row">
            <span class="dash-thumb">
              <img v-if="product.image" :src="product.image" :alt="product.name" @error="applyImageFallback" />
              <font-awesome-icon v-else icon="box-open" class="text-cream-faint" />
            </span>
            <span class="min-w-0 flex-1">
              <span class="block truncate font-medium text-cream">{{ product.name }}</span>
              <span class="stock-bar"><span :style="{ width: `${Math.min(100, product.stock * 20)}%` }"></span></span>
              <span class="block text-xs" :class="product.stock ? 'text-crust-light' : 'text-red-300'">
                {{ product.stock ? $t('admin.dashboard.left', { n: product.stock }) : $t('admin.dashboard.soldOut') }}
              </span>
            </span>
            <router-link :to="`/admin/products/${product.id}`" class="btn-ghost !py-2 !px-4 !text-sm">{{ $t('admin.dashboard.restock') }}</router-link>
          </li>
        </ul>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from '@/plugins/axios'
import { formatEuro } from '@/utils/money'
import { applyImageFallback } from '@/utils/imageFallback'

const { t } = useI18n()
const stats = ref({})
const recentOrders = ref([])
const lowStockProducts = ref([])

const hour = new Date().getHours()
const greeting = t(`admin.dashboard.${hour < 12 ? 'morning' : hour < 18 ? 'afternoon' : 'evening'}`)

const kpis = computed(() => [
  { label: t('admin.dashboard.revenue'), value: formatEuro(stats.value.totalRevenue), note: t('admin.dashboard.revenueNote'), icon: 'euro-sign' },
  { label: t('admin.dashboard.orders'), value: stats.value.totalOrders || 0, note: t('admin.dashboard.openCount', { n: stats.value.openOrders || 0 }), icon: 'receipt' },
  { label: t('admin.dashboard.products'), value: stats.value.totalProducts || 0, note: t('admin.dashboard.lowStockCount', { n: stats.value.lowStockCount || 0 }), icon: 'box-open' },
  { label: t('admin.dashboard.customers'), value: stats.value.totalUsers || 0, note: t('admin.dashboard.joinedToday', { n: stats.value.todayUsers || 0 }), icon: 'users' }
])

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
  loadError.value = failed ? t('admin.dashboard.loadError') : ''
}

onMounted(() => {
  fetchDashboardData()
})
</script>

<style scoped>
.dash-hero {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1.5rem;
  padding: 2rem;
  background:
    radial-gradient(60% 120% at 100% 0%, rgba(230, 161, 90, 0.16), transparent 70%),
    linear-gradient(180deg, rgba(30, 25, 20, 0.9), rgba(21, 18, 15, 0.9));
}

.kpi {
  padding: 1.25rem 1.4rem;
}

.kpi-icon {
  display: grid;
  place-items: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 9999px;
  color: #e6a15a;
  background: rgba(230, 161, 90, 0.12);
  font-size: 0.85rem;
}

.kpi-value {
  margin: 0.75rem 0 0.2rem;
  font-family: 'Instrument Serif', Georgia, serif;
  font-size: 2.6rem;
  line-height: 1;
  color: #f4ece1;
  font-variant-numeric: tabular-nums;
}

.dash-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  padding: 1.4rem 1.5rem 1rem;
  border-bottom: 1px solid rgba(244, 236, 225, 0.07);
}

.dash-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.9rem 1.5rem;
  border-bottom: 1px solid rgba(244, 236, 225, 0.05);
  transition: background 0.2s;
}

.dash-row:hover {
  background: rgba(244, 236, 225, 0.03);
}

.dash-avatar,
.dash-thumb {
  display: grid;
  place-items: center;
  flex-shrink: 0;
  width: 2.6rem;
  height: 2.6rem;
  border-radius: 9999px;
  background: rgba(244, 236, 225, 0.06);
  color: #f2c48d;
  font-weight: 700;
}

.dash-thumb {
  border-radius: 0.8rem;
}

.dash-thumb img {
  width: 85%;
  height: 85%;
  object-fit: contain;
}

.stock-bar {
  display: block;
  height: 4px;
  margin: 0.35rem 0 0.25rem;
  max-width: 10rem;
  border-radius: 9999px;
  background: rgba(244, 236, 225, 0.08);
  overflow: hidden;
}

.stock-bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #d2603f, #e6a15a);
}

.status {
  display: inline-block;
  margin-top: 0.2rem;
  padding: 0.1rem 0.55rem;
  border-radius: 9999px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: capitalize;
  color: #b9ab98;
  background: rgba(244, 236, 225, 0.06);
}

.status.is-pending { color: #f2c48d; background: rgba(242, 196, 141, 0.12); }
.status.is-processing { color: #9cc3f0; background: rgba(120, 170, 230, 0.12); }
.status.is-completed { color: #9fd49a; background: rgba(159, 212, 154, 0.12); }
.status.is-canceled { color: #f08f79; background: rgba(240, 143, 121, 0.12); }
</style>
