<template>
  <div class="min-h-screen py-12 px-4">
    <div class="max-w-6xl mx-auto">
      <PageHeader title="Checkout" subtitle="Choose how you get your order and how you pay" icon="shopping-bag" />

      <div v-if="loadingPage" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-white/20"></div>
      </div>

      <div v-else-if="!cartStore.items.length" class="glass-panel text-center py-12">
        <p class="text-lg text-white font-medium">Your cart is empty</p>
        <p class="mt-2 text-gray-400">Add something from the shop before checking out.</p>
        <router-link to="/products" class="btn-amber mt-6">Browse products</router-link>
      </div>

      <form v-else class="grid lg:grid-cols-12 gap-8" @submit.prevent="submit" novalidate>
        <div class="lg:col-span-7 space-y-6">
          <!-- Fulfilment -->
          <section class="glass-panel space-y-4">
            <h2 class="text-lg font-semibold text-white">1. Pickup or delivery</h2>
            <div class="grid sm:grid-cols-2 gap-3">
              <button
                v-for="method in fulfillmentMethods"
                :key="method.code"
                type="button"
                class="choice-card"
                :class="{ 'is-selected': form.fulfillment_method === method.code }"
                :aria-pressed="form.fulfillment_method === method.code"
                @click="form.fulfillment_method = method.code"
              >
                <font-awesome-icon :icon="method.code === 'pickup' ? 'store' : 'truck'" class="mt-1 text-amber-400" />
                <span>
                  <span class="block font-medium text-white">{{ method.label }}</span>
                  <span class="block text-sm text-gray-400">
                    <template v-if="method.code === 'pickup'">{{ business.name }}, {{ storeAddress }}</template>
                    <template v-else>{{ formatPrice(method.fee) }} € delivery fee</template>
                  </span>
                </span>
              </button>
            </div>

            <div v-if="isDelivery && addressStore.addresses.length" class="grid gap-3 pt-2">
              <p class="field-label">Deliver to</p>
              <button
                v-for="address in addressStore.addresses"
                :key="address.id"
                type="button"
                class="choice-card"
                :class="{ 'is-selected': selectedAddressId === address.id }"
                :aria-pressed="selectedAddressId === address.id"
                @click="selectedAddressId = address.id"
              >
                <font-awesome-icon icon="location-dot" class="mt-1 text-amber-400" />
                <span class="text-gray-200">{{ address.address_line_1 }}, {{ address.postal_code }} {{ address.city }}</span>
              </button>
              <button
                type="button"
                class="choice-card"
                :class="{ 'is-selected': selectedAddressId === null }"
                :aria-pressed="selectedAddressId === null"
                @click="selectedAddressId = null"
              >
                <font-awesome-icon icon="plus" class="mt-1 text-amber-400" />
                <span class="text-gray-200">A new address</span>
              </button>
            </div>

            <div v-if="isDelivery && selectedAddressId === null" class="grid sm:grid-cols-6 gap-4 pt-2">
              <div class="sm:col-span-6">
                <label for="address_line_1" class="field-label">Street and house number</label>
                <input id="address_line_1" v-model.trim="form.address.address_line_1" class="field-input" autocomplete="address-line1" required />
                <p v-if="errors.address_line_1" class="field-error">{{ errors.address_line_1 }}</p>
              </div>
              <div class="sm:col-span-6">
                <label for="address_line_2" class="field-label">Address line 2 <span class="text-gray-500">(optional)</span></label>
                <input id="address_line_2" v-model.trim="form.address.address_line_2" class="field-input" autocomplete="address-line2" />
              </div>
              <div class="sm:col-span-2">
                <label for="postal_code" class="field-label">Postal code</label>
                <input id="postal_code" v-model.trim="form.address.postal_code" class="field-input" autocomplete="postal-code" inputmode="numeric" required />
                <p v-if="errors.postal_code" class="field-error">{{ errors.postal_code }}</p>
              </div>
              <div class="sm:col-span-4">
                <label for="city" class="field-label">City</label>
                <input id="city" v-model.trim="form.address.city" class="field-input" autocomplete="address-level2" required />
                <p v-if="errors.city" class="field-error">{{ errors.city }}</p>
              </div>
              <label class="sm:col-span-6 flex items-center gap-2 text-gray-300">
                <input v-model="form.save_address" type="checkbox" class="rounded border-white/20 bg-white/5 text-amber-500" />
                Save this address for next time
              </label>
            </div>
          </section>

          <!-- Time and contact -->
          <section class="glass-panel space-y-4">
            <h2 class="text-lg font-semibold text-white">2. When and how to reach you</h2>
            <div class="grid sm:grid-cols-2 gap-4">
              <div>
                <label for="requested_time" class="field-label">
                  {{ isDelivery ? 'Preferred delivery time' : 'Pickup time' }} <span class="text-gray-500">(optional)</span>
                </label>
                <input id="requested_time" v-model="form.requested_time" type="datetime-local" :min="minTime" class="field-input" />
                <p v-if="errors.requested_time" class="field-error">{{ errors.requested_time }}</p>
              </div>
              <div>
                <label for="contact_phone" class="field-label">Phone <span class="text-gray-500">(optional)</span></label>
                <input id="contact_phone" v-model.trim="form.contact_phone" type="tel" class="field-input" autocomplete="tel" />
              </div>
            </div>
            <div>
              <label for="notes" class="field-label">Notes for the bakery <span class="text-gray-500">(optional)</span></label>
              <textarea id="notes" v-model.trim="form.notes" rows="3" maxlength="1000" class="field-input"
                        placeholder="e.g. please slice the bread"></textarea>
            </div>
          </section>

          <!-- Payment -->
          <section class="glass-panel space-y-4">
            <h2 class="text-lg font-semibold text-white">3. Payment</h2>
            <div class="grid gap-3">
              <button
                v-for="method in paymentMethods"
                :key="method.code"
                type="button"
                class="choice-card"
                :class="{ 'is-selected': form.payment_method === method.code, 'is-disabled': !method.available }"
                :disabled="!method.available"
                :aria-pressed="form.payment_method === method.code"
                @click="form.payment_method = method.code"
              >
                <font-awesome-icon :icon="paymentIcon(method.code)" class="mt-1 text-amber-400" />
                <span>
                  <span class="block font-medium text-white">{{ method.label }}</span>
                  <span class="block text-sm text-gray-400">
                    {{ method.available ? paymentHint(method.code) : 'Coming soon' }}
                  </span>
                </span>
              </button>
            </div>
            <p v-if="errors.payment_method" class="field-error">{{ errors.payment_method }}</p>
          </section>
        </div>

        <!-- Summary -->
        <aside class="lg:col-span-5">
          <div class="glass-panel sticky top-4 space-y-4">
            <h2 class="text-lg font-semibold text-white">Your order</h2>
            <ul class="divide-y divide-white/10">
              <li v-for="item in cartStore.items" :key="item.id" class="flex items-center gap-3 py-3">
                <img :src="item.product.image || PLACEHOLDER_IMAGE" :alt="item.product.name"
                     class="h-12 w-12 rounded-lg object-cover bg-white/5" @error="applyImageFallback" />
                <span class="flex-1 min-w-0">
                  <span class="block text-white truncate">{{ item.product.name }}</span>
                  <span class="block text-sm text-gray-400">{{ item.quantity }} × {{ formatPrice(item.unitPrice) }} €</span>
                </span>
                <span class="text-gray-200 tabular-nums">{{ formatPrice(item.totalPrice) }} €</span>
              </li>
            </ul>
            <dl class="space-y-2 text-gray-300">
              <div class="flex justify-between"><dt>Subtotal</dt><dd class="tabular-nums">{{ formatPrice(subtotal) }} €</dd></div>
              <div class="flex justify-between">
                <dt>{{ isDelivery ? 'Delivery' : 'Pickup' }}</dt>
                <dd class="tabular-nums">{{ deliveryFee > 0 ? `${formatPrice(deliveryFee)} €` : 'Free' }}</dd>
              </div>
              <div class="h-px bg-white/10 my-2"></div>
              <div class="flex justify-between text-lg font-bold text-white">
                <dt>Total</dt><dd class="tabular-nums text-amber-400">{{ formatPrice(total) }} €</dd>
              </div>
              <div class="flex justify-between text-sm text-gray-500">
                <dt>incl. {{ vatPercent }}% VAT</dt><dd class="tabular-nums">{{ formatPrice(vat) }} €</dd>
              </div>
            </dl>

            <p v-if="orderStore.error" class="rounded-lg bg-red-500/10 border border-red-500/30 p-3 text-sm text-red-300" role="alert">
              {{ orderStore.error }}
            </p>

            <button type="submit" class="btn-amber w-full" :disabled="submitting">
              <font-awesome-icon v-if="submitting" icon="spinner" spin />
              {{ submitting ? 'Placing order…' : `Place order · ${formatPrice(total)} €` }}
            </button>
            <p class="text-xs text-gray-500">
              By placing the order you accept our <router-link to="/terms" class="underline hover:text-gray-300">terms</router-link>
              and <router-link to="/privacy" class="underline hover:text-gray-300">privacy policy</router-link>.
            </p>
          </div>
        </aside>
      </form>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import PageHeader from '@/components/common/PageHeader.vue'
import { useCartStore } from '@/stores/cartStore'
import { useOrderStore } from '@/stores/orderStore'
import { useAddressStore } from '@/stores/addressStore'
import { business, streetLine, cityLine } from '@/config/business'
import { PLACEHOLDER_IMAGE, applyImageFallback } from '@/utils/imageFallback'

const router = useRouter()
const cartStore = useCartStore()
const orderStore = useOrderStore()
const addressStore = useAddressStore()
const selectedAddressId = ref(null)

const loadingPage = ref(true)
const submitting = ref(false)
const errors = reactive({})
const options = ref({ vat_rate: '0.19', fulfillment_methods: [], payment_methods: [] })

const form = reactive({
  fulfillment_method: 'pickup',
  payment_method: 'CA',
  address: { address_line_1: '', address_line_2: '', postal_code: '', city: 'Berlin' },
  requested_time: '',
  contact_phone: '',
  notes: '',
  save_address: true
})

const storeAddress = [streetLine(), cityLine()].filter(Boolean).join(', ')
const fulfillmentMethods = computed(() => options.value.fulfillment_methods)
const paymentMethods = computed(() => options.value.payment_methods)
const isDelivery = computed(() => form.fulfillment_method === 'delivery')

const subtotal = computed(() => Number(cartStore.subtotal) || 0)
const deliveryFee = computed(() => {
  if (!isDelivery.value) return 0
  const method = fulfillmentMethods.value.find(m => m.code === 'delivery')
  return Number(method?.fee) || 0
})
const total = computed(() => subtotal.value + deliveryFee.value)
const vatRate = computed(() => Number(options.value.vat_rate) || 0)
const vatPercent = computed(() => Math.round(vatRate.value * 100))
const vat = computed(() => total.value - total.value / (1 + vatRate.value))

// Earliest selectable time: one hour from now, in the local timezone.
const minTime = (() => {
  const d = new Date(Date.now() + 60 * 60 * 1000)
  d.setMinutes(d.getMinutes() - d.getTimezoneOffset())
  return d.toISOString().slice(0, 16)
})()

const formatPrice = (value) => Number(value || 0).toFixed(2)
const paymentIcon = (code) => ({ CA: 'money-bill', CC: 'credit-card', PP: 'lock' }[code] || 'credit-card')
const paymentHint = (code) => ({
  CA: 'Pay in cash when you pick up or receive your order',
  CC: 'Pay by EC or credit card at pickup or delivery',
  PP: 'Pay securely online'
}[code] || '')

// Clear a field's error as soon as it has a value again.
watch(() => ({ ...form.address }), (address) => {
  for (const key of ['address_line_1', 'postal_code', 'city']) {
    if (address[key]) delete errors[key]
  }
})
watch(() => form.payment_method, () => delete errors.payment_method)
watch(() => form.requested_time, () => delete errors.requested_time)

function validate() {
  Object.keys(errors).forEach(key => delete errors[key])
  if (isDelivery.value && selectedAddressId.value === null) {
    if (!form.address.address_line_1) errors.address_line_1 = 'Enter your street and house number.'
    if (!form.address.postal_code) errors.postal_code = 'Enter your postal code.'
    if (!form.address.city) errors.city = 'Enter your city.'
  }
  const method = paymentMethods.value.find(m => m.code === form.payment_method)
  if (!method?.available) errors.payment_method = 'Choose a payment method.'
  return Object.keys(errors).length === 0
}

async function submit() {
  if (submitting.value || !validate()) return
  submitting.value = true
  const payload = {
    fulfillment_method: form.fulfillment_method,
    payment_method: form.payment_method,
    contact_phone: form.contact_phone,
    notes: form.notes,
    requested_time: form.requested_time ? new Date(form.requested_time).toISOString() : null
  }
  if (isDelivery.value) {
    if (selectedAddressId.value !== null) {
      payload.address_id = selectedAddressId.value
    } else {
      payload.address = { ...form.address, country: 'DE' }
      payload.save_address = form.save_address
    }
  }
  try {
    const order = await orderStore.placeOrder(payload)
    await cartStore.fetchCart({ silent: true })
    router.push({ name: 'order-detail', params: { id: order.id }, query: { placed: '1' } })
  } catch (err) {
    const fieldErrors = err.fieldErrors || {}
    const address = fieldErrors.address || {}
    for (const key of ['address_line_1', 'postal_code', 'city']) {
      if (address[key]) errors[key] = [].concat(address[key])[0]
    }
    if (typeof address === 'string' || Array.isArray(address)) errors.address_line_1 = [].concat(address)[0]
    for (const key of ['payment_method', 'requested_time']) {
      if (fieldErrors[key]) errors[key] = [].concat(fieldErrors[key])[0]
    }
    // Stock may have changed; show the current cart.
    await cartStore.fetchCart({ silent: true })
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  orderStore.error = null
  try {
    const [opts, addresses] = await Promise.all([
      orderStore.fetchCheckoutOptions(),
      addressStore.fetchAddresses().catch(() => []),
      cartStore.fetchCart({ silent: true })
    ])
    if (addresses.length) selectedAddressId.value = addresses[0].id
    options.value = opts
    const firstAvailable = opts.payment_methods.find(m => m.available)
    if (firstAvailable) form.payment_method = firstAvailable.code
  } catch (err) {
    orderStore.error = 'Checkout is unavailable right now. Please try again in a moment.'
  } finally {
    loadingPage.value = false
  }
})
</script>
