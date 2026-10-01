<template>
  <div class="min-h-screen py-12 px-4">
    <div class="max-w-6xl mx-auto">
      <PageHeader :eyebrow="$t('checkout.eyebrow')" :title="$t('checkout.title')" :subtitle="$t('checkout.subtitle')" icon="shopping-bag" />

      <div v-if="loadingPage" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-white/20"></div>
      </div>

      <div v-else-if="!cartStore.items.length" class="glass-panel text-center py-12">
        <p class="text-lg text-white font-medium">{{ $t('cart.emptyTitle') }}</p>
        <p class="mt-2 text-gray-400">{{ $t('checkout.emptyText') }}</p>
        <router-link to="/products" class="btn-amber mt-6">{{ $t('common.browseProducts') }}</router-link>
      </div>

      <form v-else class="grid lg:grid-cols-12 gap-8" @submit.prevent="submit" novalidate>
        <div class="lg:col-span-7 space-y-6">
          <!-- Fulfilment -->
          <section class="glass-panel space-y-4">
            <h2 class="text-lg font-semibold text-white">{{ $t('checkout.step1') }}</h2>
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
                  <span class="block font-medium text-white">{{ $t(`common.${method.code}`) }}</span>
                  <span class="block text-sm text-gray-400">
                    <template v-if="method.code === 'pickup'">{{ business.name }}, {{ storeAddress }}</template>
                    <template v-else>{{ $t('checkout.deliveryFee', { fee: formatEuro(method.fee) }) }}</template>
                  </span>
                </span>
              </button>
            </div>

            <div v-if="isDelivery && addressStore.addresses.length" class="grid gap-3 pt-2">
              <p class="field-label">{{ $t('checkout.deliverTo') }}</p>
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
                <span class="text-gray-200">{{ $t('checkout.newAddress') }}</span>
              </button>
            </div>

            <div v-if="isDelivery && selectedAddressId === null" class="grid sm:grid-cols-6 gap-4 pt-2">
              <div class="sm:col-span-6">
                <label for="address_line_1" class="field-label">{{ $t('address.street') }}</label>
                <input id="address_line_1" v-model.trim="form.address.address_line_1" class="field-input" autocomplete="address-line1" required />
                <p v-if="errors.address_line_1" class="field-error">{{ errors.address_line_1 }}</p>
              </div>
              <div class="sm:col-span-6">
                <label for="address_line_2" class="field-label">{{ $t('address.line2') }} <span class="text-gray-500">({{ $t('common.optional') }})</span></label>
                <input id="address_line_2" v-model.trim="form.address.address_line_2" class="field-input" autocomplete="address-line2" />
              </div>
              <div class="sm:col-span-2">
                <label for="postal_code" class="field-label">{{ $t('address.postalCode') }}</label>
                <input id="postal_code" v-model.trim="form.address.postal_code" class="field-input" autocomplete="postal-code" inputmode="numeric" required />
                <p v-if="errors.postal_code" class="field-error">{{ errors.postal_code }}</p>
              </div>
              <div class="sm:col-span-4">
                <label for="city" class="field-label">{{ $t('address.city') }}</label>
                <input id="city" v-model.trim="form.address.city" class="field-input" autocomplete="address-level2" required />
                <p v-if="errors.city" class="field-error">{{ errors.city }}</p>
              </div>
              <label class="sm:col-span-6 flex items-center gap-2 text-gray-300">
                <input v-model="form.save_address" type="checkbox" class="rounded border-white/20 bg-white/5 text-amber-500" />
                {{ $t('checkout.saveAddress') }}
              </label>
            </div>
          </section>

          <!-- Time and contact -->
          <section class="glass-panel space-y-4">
            <h2 class="text-lg font-semibold text-white">{{ $t('checkout.step2') }}</h2>
            <div class="grid sm:grid-cols-2 gap-4">
              <div>
                <label for="requested_time" class="field-label">
                  {{ isDelivery ? $t('checkout.deliveryTime') : $t('checkout.pickupTime') }} <span class="text-gray-500">({{ $t('common.optional') }})</span>
                </label>
                <input id="requested_time" v-model="form.requested_time" type="datetime-local" :min="minTime" class="field-input" />
                <p v-if="errors.requested_time" class="field-error">{{ errors.requested_time }}</p>
              </div>
              <div>
                <label for="contact_phone" class="field-label">{{ $t('common.phone') }} <span class="text-gray-500">({{ $t('common.optional') }})</span></label>
                <input id="contact_phone" v-model.trim="form.contact_phone" type="tel" class="field-input" autocomplete="tel" />
              </div>
            </div>
            <div>
              <label for="notes" class="field-label">{{ $t('checkout.notes') }} <span class="text-gray-500">({{ $t('common.optional') }})</span></label>
              <textarea id="notes" v-model.trim="form.notes" rows="3" maxlength="1000" class="field-input"
                        :placeholder="$t('checkout.notesPlaceholder')"></textarea>
            </div>
          </section>

          <!-- Payment -->
          <section class="glass-panel space-y-4">
            <h2 class="text-lg font-semibold text-white">{{ $t('checkout.step3') }}</h2>
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
                  <span class="block font-medium text-white">{{ $t(`checkout.payment.${method.code}`) }}</span>
                  <span class="block text-sm text-gray-400">
                    {{ method.available ? $t(`checkout.paymentHint.${method.code}`) : $t('checkout.comingSoon') }}
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
            <h2 class="text-lg font-semibold text-white">{{ $t('cart.eyebrow') }}</h2>
            <ul class="divide-y divide-white/10">
              <li v-for="item in cartStore.items" :key="item.id" class="flex items-center gap-3 py-3">
                <img :src="item.product.image || PLACEHOLDER_IMAGE" :alt="item.product.name"
                     class="h-12 w-12 rounded-lg object-cover bg-white/5" @error="applyImageFallback" />
                <span class="flex-1 min-w-0">
                  <span class="block text-white truncate">{{ item.product.name }}</span>
                  <span class="block text-sm text-gray-400">{{ item.quantity }} × {{ formatEuro(item.unitPrice) }}</span>
                </span>
                <span class="text-gray-200 tabular-nums">{{ formatEuro(item.totalPrice) }}</span>
              </li>
            </ul>
            <dl class="space-y-2 text-gray-300">
              <div class="flex justify-between"><dt>{{ $t('common.subtotal') }}</dt><dd class="tabular-nums">{{ formatEuro(subtotal) }}</dd></div>
              <div class="flex justify-between">
                <dt>{{ isDelivery ? $t('common.delivery') : $t('common.pickup') }}</dt>
                <dd class="tabular-nums">{{ deliveryFee > 0 ? formatEuro(deliveryFee) : $t('checkout.free') }}</dd>
              </div>
              <div class="h-px bg-white/10 my-2"></div>
              <div class="flex justify-between text-lg font-bold text-white">
                <dt>{{ $t('common.total') }}</dt><dd class="tabular-nums text-amber-400">{{ formatEuro(total) }}</dd>
              </div>
              <div class="flex justify-between text-sm text-gray-500">
                <dt>{{ $t('checkout.inclVat', { percent: vatPercent }) }}</dt><dd class="tabular-nums">{{ formatEuro(vat) }}</dd>
              </div>
            </dl>

            <p v-if="orderStore.error" class="rounded-lg bg-red-500/10 border border-red-500/30 p-3 text-sm text-red-300" role="alert">
              {{ orderStore.error }}
            </p>

            <button type="submit" class="btn-amber w-full" :disabled="submitting">
              <font-awesome-icon v-if="submitting" icon="spinner" spin />
              {{ submitting ? $t('checkout.placing') : $t('checkout.place', { total: formatEuro(total) }) }}
            </button>
            <p class="text-xs text-gray-500">
              <i18n-t keypath="checkout.legal" scope="global">
                <template #terms><router-link to="/terms" class="underline hover:text-gray-300">{{ $t('checkout.terms') }}</router-link></template>
                <template #privacy><router-link to="/privacy" class="underline hover:text-gray-300">{{ $t('footer.privacyPolicy') }}</router-link></template>
              </i18n-t>
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
import { formatEuro } from '@/utils/money'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const { t } = useI18n()
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

const paymentIcon = (code) => ({ CA: 'money-bill', CC: 'credit-card', PP: 'lock' }[code] || 'credit-card')

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
    if (!form.address.address_line_1) errors.address_line_1 = t('address.errors.street')
    if (!form.address.postal_code) errors.postal_code = t('address.errors.postalCode')
    if (!form.address.city) errors.city = t('address.errors.city')
  }
  const method = paymentMethods.value.find(m => m.code === form.payment_method)
  if (!method?.available) errors.payment_method = t('checkout.errors.payment')
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
    orderStore.error = t('checkout.errors.unavailable')
  } finally {
    loadingPage.value = false
  }
})
</script>
