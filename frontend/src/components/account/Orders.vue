<template>
  <div class="section max-w-4xl pb-10">
    <PageHeader :eyebrow="$t('account.eyebrow')" :title="$t('orders.title')" :subtitle="$t('orders.subtitle')" />

    <div v-if="orderStore.loading && !orderStore.orders.length" class="grid gap-4" aria-busy="true">
      <div v-for="n in 3" :key="n" class="skeleton h-40 rounded-3xl"></div>
    </div>

    <div v-else-if="orderStore.error" class="glass-panel text-center py-12">
      <p class="display-title text-4xl">{{ $t('orders.loadError') }}</p>
      <button type="button" class="btn-ghost mt-6" @click="loadOrders">
        <font-awesome-icon icon="rotate" /> {{ $t('common.tryAgain') }}
      </button>
    </div>

    <div v-else-if="!orderStore.orders.length" class="empty lux-card">
      <span class="empty-icon" aria-hidden="true"><font-awesome-icon icon="shopping-bag" /></span>
      <h2 class="display-title text-5xl">{{ $t('orders.emptyTitle') }}</h2>
      <p class="mt-3 text-cream-muted">{{ $t('orders.emptyText') }}</p>
      <router-link to="/products" class="btn-amber mt-8">{{ $t('common.shopNow') }} <font-awesome-icon icon="arrow-right" /></router-link>
    </div>

    <ul v-else v-reveal.stagger class="grid gap-5">
      <li v-for="order in orderStore.orders" :key="order.id" class="order lux-card">
        <div class="order-head">
          <div class="min-w-0">
            <router-link :to="{ name: 'order-detail', params: { id: order.id } }" class="order-number">
              {{ order.order_number }}
            </router-link>
            <p class="text-sm text-cream-faint">{{ $t('order.placedOn', { date: formatDate(order.created_at) }) }}</p>
          </div>
          <div class="flex items-center gap-3">
            <span class="status" :class="`is-${order.status.toLowerCase()}`">{{ $t(`common.status.${order.status.toLowerCase()}`) }}</span>
            <span class="order-total">{{ formatEuro(order.total_price) }}</span>
          </div>
        </div>

        <ul class="order-items">
          <li v-for="item in order.order_items" :key="item.id" class="order-item">
            <img :src="imageUrl(item.product.image)" :alt="localized(item.product, 'name')" @error="applyImageFallback" />
            <span class="min-w-0 flex-1">
              <span class="block truncate text-cream">{{ localized(item.product, 'name') }}</span>
              <span class="text-sm text-cream-faint">{{ item.quantity }} × {{ formatEuro(item.price_per_item) }}</span>
            </span>
            <span class="tabular-nums text-cream/80">{{ formatEuro(item.quantity * item.price_per_item) }}</span>
          </li>
        </ul>

        <div class="order-foot">
          <p class="flex items-center gap-2 text-sm text-cream-muted">
            <font-awesome-icon :icon="order.fulfillment_method === 'pickup' ? 'store' : 'truck'" class="text-crust" />
            {{ order.fulfillment_method === 'pickup' ? $t('common.pickup') : $t('common.delivery') }}
            <template v-if="order.requested_time"> · {{ $t('order.requestedFor', { time: formatDateTime(order.requested_time) }) }}</template>
          </p>
          <div class="flex flex-wrap gap-2">
            <button v-if="order.is_cancelable" type="button" class="btn-ghost !py-2 !px-4 text-red-300" @click="cancelOrder(order.id)">
              <font-awesome-icon icon="xmark" /> {{ $t('order.cancel') }}
            </button>
            <router-link :to="{ name: 'order-detail', params: { id: order.id } }" class="btn-ghost !py-2 !px-4">
              {{ $t('orders.details') }} <font-awesome-icon icon="arrow-right" />
            </router-link>
          </div>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { localized } from '@/i18n/catalog'
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import PageHeader from '@/components/common/PageHeader.vue'
import { PLACEHOLDER_IMAGE, applyImageFallback } from '@/utils/imageFallback'
import { formatDate, formatDateTime, formatEuro } from '@/utils/money'
import { useToast } from '@/composables/useToast'
import { useOrderStore } from '@/stores/orderStore'
import { API_URL } from '@/config/api'

const orderStore = useOrderStore()
const { showToast } = useToast()
const { t } = useI18n()

const loadOrders = () => orderStore.fetchOrders().catch(() => {})

const imageUrl = (path) => {
  if (!path) return PLACEHOLDER_IMAGE
  if (path.startsWith('http')) return path
  return `${API_URL}${path}`
}

async function cancelOrder(orderId) {
  if (!window.confirm(t('order.confirmCancel'))) return
  try {
    await orderStore.cancelOrder(orderId)
    showToast(t('order.canceledToast'))
  } catch {
    showToast(t('order.cancelFailed'), 'error')
  }
}

onMounted(loadOrders)
</script>

<style scoped>
.order {
  padding: 1.5rem;
}

.order-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(244, 236, 225, 0.08);
}

.order-number {
  font-family: 'Instrument Serif', Georgia, serif;
  font-size: 1.9rem;
  line-height: 1.1;
  color: #f4ece1;
}

.order-number:hover {
  color: #f2c48d;
}

.order-total {
  font-size: 1.2rem;
  font-weight: 700;
  color: #f2c48d;
  font-variant-numeric: tabular-nums;
}

.order-items {
  display: grid;
  gap: 0.5rem;
  padding: 1rem 0;
}

.order-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.order-item img {
  width: 3.25rem;
  height: 3.25rem;
  border-radius: 0.9rem;
  object-fit: contain;
  background: rgba(244, 236, 225, 0.04);
}

.order-foot {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(244, 236, 225, 0.08);
}

.status {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 700;
  color: #f2c48d;
  background: rgba(242, 196, 141, 0.12);
}

.status.is-processing { color: #9cc3f0; background: rgba(120, 170, 230, 0.12); }
.status.is-completed { color: #9fd49a; background: rgba(159, 212, 154, 0.12); }
.status.is-canceled { color: #f08f79; background: rgba(240, 143, 121, 0.12); }

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 4rem 1.5rem 3.5rem;
  text-align: center;
}

.empty-icon {
  display: grid;
  place-items: center;
  width: 5rem;
  height: 5rem;
  margin-bottom: 1.5rem;
  border-radius: 9999px;
  font-size: 1.8rem;
  color: #e6a15a;
  background: rgba(230, 161, 90, 0.12);
}

.skeleton {
  background: linear-gradient(100deg, rgba(244, 236, 225, 0.04) 30%, rgba(244, 236, 225, 0.09) 50%, rgba(244, 236, 225, 0.04) 70%);
  background-size: 200% 100%;
  animation: shimmer 1.4s linear infinite;
}

@keyframes shimmer {
  to { background-position: -200% 0; }
}
</style>
