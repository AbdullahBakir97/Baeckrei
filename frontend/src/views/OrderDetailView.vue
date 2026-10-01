<template>
  <div class="min-h-screen py-12 px-4">
    <div class="max-w-4xl mx-auto">
      <router-link to="/orders" class="btn-ghost mb-6">
        <font-awesome-icon icon="arrow-left" /> All orders
      </router-link>

      <div v-if="loading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-white/20"></div>
      </div>

      <div v-else-if="notFound" class="glass-panel text-center py-12">
        <p class="text-lg text-white font-medium">We couldn't find this order</p>
        <p class="mt-2 text-gray-400">It may belong to a different account.</p>
      </div>

      <template v-else-if="order">
        <div v-if="justPlaced" class="glass-panel mb-6 flex items-start gap-3 border-green-500/30" role="status">
          <font-awesome-icon icon="circle-check" class="mt-1 text-2xl text-green-400" />
          <div>
            <p class="text-lg font-semibold text-white">Thank you! Your order has been placed.</p>
            <p class="text-gray-400">
              <template v-if="order.fulfillment_method === 'pickup'">
                We'll have it ready at {{ business.name }}, {{ storeAddress }}.
              </template>
              <template v-else>We'll deliver it to the address below.</template>
            </p>
          </div>
        </div>

        <div class="flex flex-wrap items-start justify-between gap-4 mb-6">
          <div>
            <h1 class="text-3xl font-extrabold text-white">Order {{ order.order_number }}</h1>
            <p class="text-gray-400">Placed on {{ formatDateTime(order.created_at) }}</p>
          </div>
          <span class="px-3 py-1 rounded-full text-sm font-medium" :class="statusClass">{{ order.status }}</span>
        </div>

        <!-- Progress -->
        <ol v-if="order.status !== 'Canceled'" class="glass-panel grid grid-cols-3 gap-2 mb-6" aria-label="Order progress">
          <li v-for="(step, index) in steps" :key="step.status" class="flex flex-col items-center text-center gap-2">
            <span class="h-3 w-3 rounded-full" :class="index <= currentStep ? 'bg-amber-400' : 'bg-white/15'"></span>
            <span class="text-sm" :class="index <= currentStep ? 'text-white' : 'text-gray-500'">{{ step.label }}</span>
          </li>
        </ol>
        <p v-else class="glass-panel mb-6 text-red-300">This order was canceled.</p>

        <div class="grid md:grid-cols-2 gap-6 mb-6">
          <section class="glass-panel space-y-2">
            <h2 class="text-lg font-semibold text-white flex items-center gap-2">
              <font-awesome-icon :icon="order.fulfillment_method === 'pickup' ? 'store' : 'truck'" class="text-amber-400" />
              {{ order.fulfillment_method === 'pickup' ? 'Pickup' : 'Delivery' }}
            </h2>
            <p v-if="order.fulfillment_method === 'pickup'" class="text-gray-300">
              {{ business.name }}<br>{{ storeAddress }}<br>
              <span v-if="business.transit" class="text-gray-400">{{ business.transit }}</span>
            </p>
            <p v-else-if="order.address" class="text-gray-300">
              {{ order.address.address_line_1 }}<br>
              <template v-if="order.address.address_line_2">{{ order.address.address_line_2 }}<br></template>
              {{ order.address.postal_code }} {{ order.address.city }}
            </p>
            <p v-if="order.requested_time" class="text-gray-400">
              <font-awesome-icon icon="clock" class="mr-1" /> Requested for {{ formatDateTime(order.requested_time) }}
            </p>
            <p v-if="order.shipping_tracking_number" class="text-gray-400">Tracking number: {{ order.shipping_tracking_number }}</p>
          </section>

          <section class="glass-panel space-y-2">
            <h2 class="text-lg font-semibold text-white flex items-center gap-2">
              <font-awesome-icon icon="credit-card" class="text-amber-400" /> Payment
            </h2>
            <p class="text-gray-300">{{ order.payment?.payment_method_display || '—' }}</p>
            <p class="text-gray-400">Status: {{ order.payment?.status_display || 'Pending' }}</p>
            <p v-if="order.notes" class="text-gray-400">Notes: {{ order.notes }}</p>
          </section>
        </div>

        <section class="glass-panel">
          <h2 class="text-lg font-semibold text-white mb-2">Items</h2>
          <ul class="divide-y divide-white/10">
            <li v-for="item in order.order_items" :key="item.id" class="flex items-center gap-4 py-3">
              <img :src="item.product.image || PLACEHOLDER_IMAGE" :alt="item.product.name"
                   class="h-14 w-14 rounded-lg object-cover bg-white/5" @error="applyImageFallback" />
              <span class="flex-1 min-w-0">
                <router-link :to="{ name: 'product-detail', params: { id: item.product.id } }" class="block text-white hover:text-amber-300 truncate">
                  {{ item.product.name }}
                </router-link>
                <span class="text-sm text-gray-400">{{ item.quantity }} × {{ formatPrice(item.price_per_item) }} €</span>
              </span>
              <span class="text-gray-200 tabular-nums">{{ formatPrice(item.quantity * item.price_per_item) }} €</span>
            </li>
          </ul>
          <dl class="mt-4 space-y-2 text-gray-300">
            <div v-if="Number(order.delivery_fee) > 0" class="flex justify-between">
              <dt>Delivery</dt><dd class="tabular-nums">{{ formatPrice(order.delivery_fee) }} €</dd>
            </div>
            <div class="flex justify-between text-lg font-bold text-white">
              <dt>Total</dt><dd class="tabular-nums text-amber-400">{{ formatPrice(order.total_price) }} €</dd>
            </div>
            <div class="flex justify-between text-sm text-gray-500">
              <dt>incl. VAT</dt><dd class="tabular-nums">{{ formatPrice(order.vat_amount) }} €</dd>
            </div>
          </dl>
        </section>

        <div v-if="order.is_cancelable" class="mt-6 flex flex-wrap items-center gap-3">
          <template v-if="confirmingCancel">
            <span class="text-gray-300">Cancel this order?</span>
            <button type="button" class="btn-ghost text-red-300" :disabled="canceling" @click="cancel">Yes, cancel it</button>
            <button type="button" class="btn-ghost" @click="confirmingCancel = false">Keep order</button>
          </template>
          <button v-else type="button" class="btn-ghost text-red-300" @click="confirmingCancel = true">
            <font-awesome-icon icon="xmark" /> Cancel order
          </button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useOrderStore } from '@/stores/orderStore'
import { useToast } from '@/composables/useToast'
import { business, streetLine, cityLine } from '@/config/business'
import { PLACEHOLDER_IMAGE, applyImageFallback } from '@/utils/imageFallback'

const route = useRoute()
const orderStore = useOrderStore()
const { showToast } = useToast()

const loading = ref(true)
const notFound = ref(false)
const canceling = ref(false)
const confirmingCancel = ref(false)

const order = computed(() => orderStore.currentOrder)
const justPlaced = computed(() => route.query.placed === '1')
const storeAddress = [streetLine(), cityLine()].filter(Boolean).join(', ')

const steps = [
  { status: 'Pending', label: 'Received' },
  { status: 'Processing', label: 'Being prepared' },
  { status: 'Completed', label: 'Done' }
]
const currentStep = computed(() => Math.max(0, steps.findIndex(s => s.status === order.value?.status)))
const statusClass = computed(() => ({
  Completed: 'bg-green-500/20 text-green-300',
  Processing: 'bg-blue-500/20 text-blue-300',
  Canceled: 'bg-red-500/20 text-red-300'
}[order.value?.status] || 'bg-amber-500/20 text-amber-300'))

const formatPrice = (value) => Number(value || 0).toFixed(2)
const formatDateTime = (value) => new Date(value).toLocaleString('de-DE', {
  day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit'
})

async function cancel() {
  canceling.value = true
  try {
    await orderStore.cancelOrder(order.value.id)
    showToast('Your order was canceled')
  } catch (err) {
    showToast(orderStore.error || 'The order could not be canceled', 'error')
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
})
</script>
