<template>
  <div class="section max-w-4xl pb-10">
    <router-link to="/orders" class="btn-ghost mb-8">
      <font-awesome-icon icon="arrow-left" /> {{ $t('order.allOrders') }}
    </router-link>

    <div v-if="loading" class="grid gap-4" aria-busy="true">
      <div v-for="n in 3" :key="n" class="skeleton h-32 rounded-3xl"></div>
    </div>

    <div v-else-if="notFound" class="glass-panel text-center py-12">
      <p class="display-title text-4xl">{{ $t('order.notFound') }}</p>
      <p class="mt-2 text-cream-muted">{{ $t('order.notFoundText') }}</p>
    </div>

    <template v-else-if="order">
      <!-- Online payment: waiting for Stripe's confirmation, or still to pay -->
      <div v-if="awaitingPayment" class="placed glass-panel mb-8" role="status" aria-live="polite">
        <span class="placed-check is-waiting" aria-hidden="true">
          <font-awesome-icon :icon="confirming ? 'spinner' : 'lock'" :spin="confirming" />
        </span>
        <div v-if="confirming">
          <p class="display-title text-4xl">{{ $t('order.confirmingPayment') }}</p>
        </div>
        <div v-else>
          <p class="display-title text-4xl">{{ paymentCanceled ? $t('order.payCanceled') : $t('order.payOpen') }}</p>
          <p class="mt-1 text-cream-muted">{{ paymentCanceled ? $t('order.payCanceledText') : $t('order.payOpenText') }}</p>
          <button type="button" class="btn-amber mt-4" :disabled="paying" @click="pay">
            <font-awesome-icon :icon="paying ? 'spinner' : 'lock'" :spin="paying" />
            {{ $t('order.payNow', { total: formatEuro(order.total_price) }) }}
          </button>
        </div>
      </div>

      <div v-else-if="justPlaced && order.status !== 'Canceled'" class="placed glass-panel mb-8" role="status">
        <span class="placed-check" aria-hidden="true"><font-awesome-icon icon="check" /></span>
        <div>
          <p class="display-title text-4xl">{{ justPaid ? $t('order.paidThanks') : $t('order.thanks') }}</p>
          <p class="mt-1 text-cream-muted">
            <template v-if="order.fulfillment_method === 'pickup'">
              {{ $t('order.readyAt', { name: business.name, address: storeAddress }) }}
            </template>
            <template v-else>{{ $t('order.willDeliver') }}</template>
          </p>
          <p v-if="authStore.user?.email" class="text-sm text-cream-faint">{{ $t('order.emailSent', { email: authStore.user.email }) }}</p>
        </div>
      </div>

      <div class="flex flex-wrap items-end justify-between gap-4 mb-8">
        <div>
          <p class="eyebrow">{{ $t('order.eyebrow') }}</p>
          <h1 class="display-title text-5xl sm:text-6xl mt-2">{{ order.order_number }}</h1>
          <p class="mt-2 text-cream-muted">{{ $t('order.placedOn', { date: formatDateTime(order.created_at) }) }}</p>
        </div>
        <span class="status-pill" :class="statusClass">{{ $t(`common.status.${order.status.toLowerCase()}`) }}</span>
      </div>

      <!-- Progress -->
      <ol v-if="order.status !== 'Canceled'" class="progress glass-panel mb-6" :aria-label="$t('order.progress')">
        <li v-for="(step, index) in steps" :key="step.status" :class="{ 'is-done': index <= currentStep }">
          <span class="progress-dot"></span>
          <span>{{ $t(step.label) }}</span>
        </li>
      </ol>
      <p v-else class="glass-panel mb-6 text-red-300">{{ $t('order.canceled') }}</p>

      <div class="grid md:grid-cols-2 gap-6 mb-6">
        <section class="glass-panel space-y-2">
          <h2 class="panel-title">
            <font-awesome-icon :icon="order.fulfillment_method === 'pickup' ? 'store' : 'truck'" class="text-crust" />
            {{ order.fulfillment_method === 'pickup' ? $t('common.pickup') : $t('common.delivery') }}
          </h2>
          <p v-if="order.fulfillment_method === 'pickup'" class="text-cream/80">
            {{ business.name }}<br>{{ storeAddress }}<br>
            <span v-if="business.transit" class="text-cream-muted">{{ business.transit }}</span>
          </p>
          <p v-else-if="order.address" class="text-cream/80">
            {{ order.address.address_line_1 }}<br>
            <template v-if="order.address.address_line_2">{{ order.address.address_line_2 }}<br></template>
            {{ order.address.postal_code }} {{ order.address.city }}
          </p>
          <p v-if="order.requested_time" class="text-cream-muted">
            <font-awesome-icon icon="clock" class="mr-1" /> {{ $t('order.requestedFor', { time: formatDateTime(order.requested_time) }) }}
          </p>
          <p v-if="order.shipping_tracking_number" class="text-cream-muted">{{ $t('order.tracking', { number: order.shipping_tracking_number }) }}</p>
        </section>

        <section class="glass-panel space-y-2">
          <h2 class="panel-title">
            <font-awesome-icon icon="credit-card" class="text-crust" /> {{ $t('order.payment') }}
          </h2>
          <p class="text-cream/80">{{ order.payment ? $t(`checkout.payment.${order.payment.payment_method}`) : '—' }}</p>
          <p class="text-cream-muted">{{ $t('order.paymentStatus', { status: $t(`order.paymentStatuses.${(order.payment?.status || 'Pending').toLowerCase()}`) }) }}</p>
          <p v-if="order.notes" class="text-cream-muted">{{ $t('order.notes', { notes: order.notes }) }}</p>
        </section>
      </div>

      <section class="glass-panel">
        <h2 class="panel-title mb-2">{{ $t('order.items') }}</h2>
        <ul class="divide-y divide-white/10">
          <li v-for="item in order.order_items" :key="item.id" class="flex items-center gap-4 py-3">
            <img :src="item.product.image || PLACEHOLDER_IMAGE" :alt="localized(item.product, 'name')"
                 class="h-14 w-14 rounded-xl object-contain bg-white/5" @error="applyImageFallback" />
            <span class="flex-1 min-w-0">
              <router-link :to="{ name: 'product-detail', params: { id: item.product.id } }" class="block text-cream hover:text-crust-light truncate">
                {{ localized(item.product, 'name') }}
              </router-link>
              <span class="text-sm text-cream-muted">{{ item.quantity }} × {{ formatEuro(item.price_per_item) }}</span>
            </span>
            <span class="text-cream/80 tabular-nums">{{ formatEuro(item.quantity * item.price_per_item) }}</span>
          </li>
        </ul>
        <dl class="mt-4 space-y-2 text-cream/80">
          <div v-if="Number(order.delivery_fee) > 0" class="flex justify-between">
            <dt>{{ $t('common.delivery') }}</dt><dd class="tabular-nums">{{ formatEuro(order.delivery_fee) }}</dd>
          </div>
          <div class="flex justify-between text-lg font-bold text-cream">
            <dt>{{ $t('common.total') }}</dt><dd class="tabular-nums text-crust-light">{{ formatEuro(order.total_price) }}</dd>
          </div>
          <div class="flex justify-between text-sm text-cream-faint">
            <dt>{{ $t('common.vatIncluded') }}</dt><dd class="tabular-nums">{{ formatEuro(order.vat_amount) }}</dd>
          </div>
        </dl>
      </section>

      <div v-if="order.is_cancelable" class="mt-6 flex flex-wrap items-center gap-3">
        <template v-if="confirmingCancel">
          <span class="text-cream/80">{{ $t('order.confirmCancel') }}</span>
          <button type="button" class="btn-ghost text-red-300" :disabled="canceling" @click="cancel">{{ $t('order.yesCancel') }}</button>
          <button type="button" class="btn-ghost" @click="confirmingCancel = false">{{ $t('order.keep') }}</button>
        </template>
        <button v-else type="button" class="btn-ghost text-red-300" @click="confirmingCancel = true">
          <font-awesome-icon icon="xmark" /> {{ $t('order.cancel') }}
        </button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { localized } from '@/i18n/catalog'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useOrderStore } from '@/stores/orderStore'
import { useToast } from '@/composables/useToast'
import { useAuthStore } from '@/stores/authStore'
import { business, streetLine, cityLine } from '@/config/business'
import { PLACEHOLDER_IMAGE, applyImageFallback } from '@/utils/imageFallback'
import { formatEuro, formatDateTime } from '@/utils/money'
import { useI18n } from 'vue-i18n'

const route = useRoute()
const orderStore = useOrderStore()
const authStore = useAuthStore()
const { showToast } = useToast()
const { t } = useI18n()

const loading = ref(true)
const notFound = ref(false)
const canceling = ref(false)
const confirmingCancel = ref(false)

const order = computed(() => orderStore.currentOrder)
const justPlaced = computed(() => route.query.placed === '1')
const paying = ref(false)
const polls = ref(0)

// Online payments are confirmed by Stripe's webhook, usually within seconds
// of the customer coming back; until then the page checks again.
const onlinePending = computed(() =>
  order.value?.payment?.payment_method === 'ST' && order.value.payment.status === 'Pending' && order.value.status === 'Pending')
const returnedPaid = computed(() => route.query.paid === '1')
const confirming = computed(() => onlinePending.value && returnedPaid.value && polls.value < 30)
const awaitingPayment = computed(() => onlinePending.value && (!returnedPaid.value || confirming.value))
const paymentCanceled = computed(() => route.query.payment === 'canceled')
const justPaid = computed(() => returnedPaid.value && order.value?.payment?.status === 'Completed')
let pollTimer = null

function pollPayment() {
  clearTimeout(pollTimer)
  if (!confirming.value) return
  pollTimer = setTimeout(async () => {
    polls.value += 1
    await orderStore.fetchOrderById(route.params.id).catch(() => {})
    pollPayment()
  }, 2000)
}

async function pay() {
  paying.value = true
  try {
    window.location.assign(await orderStore.payOrder(order.value.id))
  } catch (err) {
    showToast(err.response?.data?.error || t('order.payFailed'), 'error')
    paying.value = false
    await orderStore.fetchOrderById(route.params.id).catch(() => {})
  }
}
const storeAddress = computed(() => [streetLine(), cityLine()].filter(Boolean).join(', '))

const steps = [
  { status: 'Pending', label: 'order.steps.received' },
  { status: 'Processing', label: 'order.steps.preparing' },
  { status: 'Completed', label: 'order.steps.done' }
]
const currentStep = computed(() => Math.max(0, steps.findIndex(s => s.status === order.value?.status)))
const statusClass = computed(() => `is-${(order.value?.status || 'pending').toLowerCase()}`)


async function cancel() {
  canceling.value = true
  try {
    await orderStore.cancelOrder(order.value.id)
    showToast(t('order.canceledToast'))
  } catch (err) {
    showToast(orderStore.error || t('order.cancelFailed'), 'error')
  } finally {
    canceling.value = false
    confirmingCancel.value = false
  }
}

onMounted(async () => {
  try {
    if (orderStore.currentOrder?.id !== Number(route.params.id)) {
      await orderStore.fetchOrderById(route.params.id)
    }
  } catch (err) {
    notFound.value = true
  } finally {
    loading.value = false
  }
  pollPayment()
})

onBeforeUnmount(() => clearTimeout(pollTimer))
</script>

<style scoped>
.placed {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  border-color: rgba(159, 212, 154, 0.25);
}

.placed-check {
  display: grid;
  place-items: center;
  flex-shrink: 0;
  width: 3.5rem;
  height: 3.5rem;
  border-radius: 9999px;
  font-size: 1.4rem;
  color: #0e0c0a;
  background: #9fd49a;
  animation: pop-in 0.7s var(--ease-out-expo) both;
}

.placed-check.is-waiting {
  color: #0e0c0a;
  background: #e6a15a;
}

@keyframes pop-in {
  from { transform: scale(0.3) rotate(-30deg); opacity: 0; }
}

.status-pill {
  padding: 0.4rem 1rem;
  border-radius: 9999px;
  font-size: 0.85rem;
  font-weight: 700;
  color: #f2c48d;
  background: rgba(242, 196, 141, 0.12);
}

.status-pill.is-processing { color: #9cc3f0; background: rgba(120, 170, 230, 0.12); }
.status-pill.is-completed { color: #9fd49a; background: rgba(159, 212, 154, 0.12); }
.status-pill.is-canceled { color: #f08f79; background: rgba(240, 143, 121, 0.12); }

.progress {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
}

.progress li {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.6rem;
  text-align: center;
  font-size: 0.9rem;
  color: #7d7061;
}

.progress li.is-done {
  color: #f4ece1;
}

.progress-dot {
  width: 0.8rem;
  height: 0.8rem;
  border-radius: 9999px;
  background: rgba(244, 236, 225, 0.15);
}

.is-done .progress-dot {
  background: #e6a15a;
  box-shadow: 0 0 0 5px rgba(230, 161, 90, 0.18);
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-family: 'Instrument Serif', Georgia, serif;
  font-size: 1.8rem;
  font-weight: 400;
  color: #f4ece1;
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
