<template>
  <div class="space-y-6">
    <!-- Filters -->
    <form class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 bg-white rounded-lg shadow p-4" @submit.prevent="fetchOrders">
      <div class="lg:col-span-2">
        <label for="order-search" class="block text-sm font-medium text-gray-700">Search</label>
        <input id="order-search" v-model.trim="filters.search" type="search" placeholder="Order number, name or email"
               class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm text-gray-900 bg-white" />
      </div>
      <div>
        <label for="order-status" class="block text-sm font-medium text-gray-700">Status</label>
        <select id="order-status" v-model="filters.status"
                class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm text-gray-900 bg-white">
          <option value="">All</option>
          <option v-for="s in statuses" :key="s" :value="s">{{ s }}</option>
        </select>
      </div>
      <div>
        <label for="order-fulfillment" class="block text-sm font-medium text-gray-700">Pickup / delivery</label>
        <select id="order-fulfillment" v-model="filters.fulfillment_method"
                class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm text-gray-900 bg-white">
          <option value="">All</option>
          <option value="pickup">Pickup</option>
          <option value="delivery">Delivery</option>
        </select>
      </div>
      <div class="flex items-end gap-2">
        <button type="submit" class="px-4 py-2 text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700">Filter</button>
        <button type="button" class="px-4 py-2 text-sm font-medium rounded-md text-gray-700 bg-gray-100 hover:bg-gray-200" @click="resetFilters">Reset</button>
      </div>
      <div>
        <label for="order-from" class="block text-sm font-medium text-gray-700">From</label>
        <input id="order-from" v-model="filters.start_date" type="date"
               class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm sm:text-sm text-gray-900 bg-white" />
      </div>
      <div>
        <label for="order-to" class="block text-sm font-medium text-gray-700">To</label>
        <input id="order-to" v-model="filters.end_date" type="date"
               class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm sm:text-sm text-gray-900 bg-white" />
      </div>
    </form>

    <p v-if="error" class="rounded-md bg-red-50 p-3 text-sm text-red-700" role="alert">{{ error }}</p>

    <!-- Orders table -->
    <div class="bg-white rounded-lg shadow overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200 admin-table">
        <thead class="bg-gray-50">
          <tr>
            <th scope="col">Order</th>
            <th scope="col">Customer</th>
            <th scope="col">Placed</th>
            <th scope="col">Pickup / delivery</th>
            <th scope="col">Status</th>
            <th scope="col" class="text-right">Total</th>
            <th scope="col"><span class="sr-only">Actions</span></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-if="loading"><td colspan="7" class="text-center text-gray-500">Loading orders…</td></tr>
          <tr v-else-if="!orders.length"><td colspan="7" class="text-center text-gray-500">No orders match these filters.</td></tr>
          <tr v-for="order in orders" v-else :key="order.id">
            <td class="font-medium text-gray-900">{{ order.order_number }}</td>
            <td>{{ order.customer_name || '—' }}</td>
            <td>{{ formatDateTime(order.created_at) }}</td>
            <td>
              {{ order.fulfillment_method === 'pickup' ? 'Pickup' : 'Delivery' }}
              <span v-if="order.requested_time" class="block text-xs text-gray-500">for {{ formatDateTime(order.requested_time) }}</span>
            </td>
            <td><span class="px-2 py-1 text-xs font-medium rounded-full" :class="statusClass(order.status)">{{ order.status }}</span></td>
            <td class="text-right tabular-nums">{{ formatPrice(order.total_price) }} €</td>
            <td class="text-right">
              <button type="button" class="text-indigo-600 hover:text-indigo-900 bg-transparent font-medium" @click="openOrder(order.id)">Details</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Detail drawer -->
    <div v-if="selected" class="fixed inset-0 z-50 flex justify-end bg-gray-900/50" @click.self="closeOrder">
      <aside class="h-full w-full max-w-xl overflow-y-auto bg-white p-6 shadow-xl text-gray-800" role="dialog" aria-modal="true" :aria-label="`Order ${selected.order_number}`">
        <div class="flex items-start justify-between gap-4">
          <div>
            <h2 class="text-xl font-semibold text-gray-900">{{ selected.order_number }}</h2>
            <p class="text-sm text-gray-500">Placed {{ formatDateTime(selected.created_at) }}</p>
          </div>
          <button type="button" class="rounded p-1 text-gray-500 hover:text-gray-700 bg-transparent" aria-label="Close" @click="closeOrder">✕</button>
        </div>

        <span class="mt-3 inline-block px-2 py-1 text-xs font-medium rounded-full" :class="statusClass(selected.status)">{{ selected.status }}</span>

        <dl class="mt-6 grid grid-cols-2 gap-4 text-sm">
          <div>
            <dt class="font-medium text-gray-500">Customer</dt>
            <dd>{{ selected.customer_name || '—' }}</dd>
            <dd v-if="selected.contact_phone">{{ selected.contact_phone }}</dd>
          </div>
          <div>
            <dt class="font-medium text-gray-500">{{ selected.fulfillment_method === 'pickup' ? 'Pickup' : 'Delivery to' }}</dt>
            <dd v-if="selected.fulfillment_method === 'pickup'">In store</dd>
            <dd v-else-if="selected.address">
              {{ selected.address.address_line_1 }}<br>
              <template v-if="selected.address.address_line_2">{{ selected.address.address_line_2 }}<br></template>
              {{ selected.address.postal_code }} {{ selected.address.city }}
            </dd>
            <dd v-if="selected.requested_time" class="text-gray-500">Requested {{ formatDateTime(selected.requested_time) }}</dd>
          </div>
          <div>
            <dt class="font-medium text-gray-500">Payment</dt>
            <dd>{{ selected.payment?.payment_method_display || '—' }}</dd>
            <dd class="text-gray-500">{{ selected.payment?.status_display || '' }}</dd>
          </div>
          <div v-if="selected.notes">
            <dt class="font-medium text-gray-500">Notes</dt>
            <dd>{{ selected.notes }}</dd>
          </div>
        </dl>

        <ul class="mt-6 divide-y divide-gray-200 border-y border-gray-200">
          <li v-for="item in selected.items" :key="item.id" class="flex justify-between py-2 text-sm">
            <span>{{ item.quantity }} × {{ item.product_name }}</span>
            <span class="tabular-nums">{{ formatPrice(item.subtotal) }} €</span>
          </li>
          <li v-if="Number(selected.delivery_fee) > 0" class="flex justify-between py-2 text-sm">
            <span>Delivery fee</span><span class="tabular-nums">{{ formatPrice(selected.delivery_fee) }} €</span>
          </li>
          <li class="flex justify-between py-2 font-semibold">
            <span>Total</span><span class="tabular-nums">{{ formatPrice(selected.total_price) }} €</span>
          </li>
        </ul>

        <div v-if="selected.fulfillment_method === 'delivery' && selected.is_cancelable" class="mt-6">
          <label for="tracking" class="block text-sm font-medium text-gray-700">Tracking or driver note <span class="text-gray-400">(optional)</span></label>
          <div class="mt-1 flex gap-2">
            <input id="tracking" v-model.trim="tracking" class="block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm sm:text-sm text-gray-900 bg-white" />
            <button type="button" class="px-3 py-2 text-sm rounded-md text-gray-700 bg-gray-100 hover:bg-gray-200" :disabled="!tracking || busy" @click="saveTracking">Save</button>
          </div>
        </div>

        <p v-if="actionError" class="mt-4 rounded-md bg-red-50 p-3 text-sm text-red-700" role="alert">{{ actionError }}</p>

        <div class="mt-6 flex flex-wrap gap-3">
          <button v-for="action in nextActions" :key="action.status" type="button" :disabled="busy"
                  class="px-4 py-2 text-sm font-medium rounded-md"
                  :class="action.status === 'Canceled' ? 'text-red-700 bg-red-50 hover:bg-red-100' : 'text-white bg-indigo-600 hover:bg-indigo-700'"
                  @click="setStatus(action.status)">
            {{ action.label }}
          </button>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '@/plugins/axios'

const API = '/api/orders/orders/'
const statuses = ['Pending', 'Processing', 'Completed', 'Canceled']
// Mirrors OrderService.ALLOWED_STATUS_TRANSITIONS on the backend.
const transitions = {
  Pending: [{ status: 'Processing', label: 'Start preparing' }, { status: 'Canceled', label: 'Cancel order' }],
  Processing: [{ status: 'Completed', label: 'Mark as handed over' }, { status: 'Canceled', label: 'Cancel order' }],
  Completed: [],
  Canceled: []
}

const route = useRoute()
const router = useRouter()
const orders = ref([])
const loading = ref(false)
const error = ref('')
const selected = ref(null)
const tracking = ref('')
const busy = ref(false)
const actionError = ref('')

const emptyFilters = { search: '', status: '', fulfillment_method: '', start_date: '', end_date: '' }
const filters = reactive({ ...emptyFilters })

const nextActions = computed(() => (selected.value ? transitions[selected.value.status] || [] : []))

const formatPrice = (value) => Number(value || 0).toFixed(2)
const formatDateTime = (value) => new Date(value).toLocaleString('de-DE', {
  day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit'
})
const statusClass = (status) => ({
  Pending: 'bg-yellow-100 text-yellow-800',
  Processing: 'bg-blue-100 text-blue-800',
  Completed: 'bg-green-100 text-green-800',
  Canceled: 'bg-red-100 text-red-800'
}[status] || 'bg-gray-100 text-gray-800')

async function fetchOrders() {
  loading.value = true
  error.value = ''
  try {
    const params = Object.fromEntries(Object.entries(filters).filter(([, v]) => v))
    const response = await axios.get(API, { params })
    orders.value = Array.isArray(response.data) ? response.data : response.data.results || []
  } catch (err) {
    error.value = 'Orders could not be loaded.'
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  Object.assign(filters, emptyFilters)
  fetchOrders()
}

async function openOrder(id) {
  actionError.value = ''
  try {
    const response = await axios.get(`${API}${id}/`)
    selected.value = response.data
    tracking.value = response.data.shipping_tracking_number || ''
  } catch (err) {
    error.value = 'That order could not be loaded.'
  }
}

function closeOrder() {
  selected.value = null
  if (route.query.order) router.replace({ query: {} })
}

function replaceOrder(order) {
  selected.value = order
  const index = orders.value.findIndex(o => o.id === order.id)
  if (index !== -1) orders.value[index] = order
}

async function setStatus(status) {
  busy.value = true
  actionError.value = ''
  try {
    const response = await axios.post(`${API}${selected.value.id}/update_status/`, { status })
    replaceOrder(response.data)
  } catch (err) {
    actionError.value = err.response?.data?.error || 'The status could not be changed.'
  } finally {
    busy.value = false
  }
}

async function saveTracking() {
  busy.value = true
  actionError.value = ''
  try {
    const response = await axios.post(`${API}${selected.value.id}/add_tracking/`, { tracking_number: tracking.value })
    replaceOrder(response.data)
  } catch (err) {
    actionError.value = err.response?.data?.error || 'The note could not be saved.'
  } finally {
    busy.value = false
  }
}

onMounted(async () => {
  await fetchOrders()
  if (route.query.order) openOrder(route.query.order)
})
</script>

<style scoped>
.admin-table {
  background: white;
}

.admin-table th {
  @apply px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-600 bg-gray-50;
  border-color: #e5e7eb;
}

.admin-table td {
  @apply px-4 py-3 text-sm text-gray-700 whitespace-nowrap;
  background: white;
  border-color: #e5e7eb;
}
</style>
