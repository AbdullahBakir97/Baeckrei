<template>
  <div class="section pb-10">
    <PageHeader eyebrow="Your order" title="Cart"
                :subtitle="cartStore.items.length ? `${cartStore.itemCount} ${cartStore.itemCount === 1 ? 'item' : 'items'} ready for checkout` : ''" />

    <div v-if="loading && !cartStore.items.length" class="grid gap-4 lg:w-2/3" aria-busy="true">
      <div v-for="n in 3" :key="n" class="skeleton h-28 rounded-3xl"></div>
    </div>

    <!-- Empty -->
    <div v-else-if="!cartStore.items.length" class="empty lux-card">
      <img :src="croissantImg" alt="" class="empty-img" />
      <h2 class="display-title text-5xl">Your cart is empty.</h2>
      <p class="mt-3 text-cream-muted">Everything on the counter is baked fresh today.</p>
      <router-link v-magnetic="0.2" to="/products" class="btn-amber mt-8">
        Shop the oven <font-awesome-icon icon="arrow-right" />
      </router-link>
    </div>

    <div v-else class="cart-grid">
      <!-- Items -->
      <ul class="cart-items">
        <transition-group name="line">
          <li v-for="item in cartStore.items" :key="item.product.id" class="line">
            <router-link :to="{ name: 'product-detail', params: { id: item.product.id } }" class="line-media">
              <img :src="item.product.image || PLACEHOLDER_IMAGE" :alt="item.product.name" @error="applyImageFallback" />
            </router-link>
            <div class="min-w-0 flex-1">
              <router-link :to="{ name: 'product-detail', params: { id: item.product.id } }" class="line-name">
                {{ item.product.name }}
              </router-link>
              <p class="mt-1 text-sm text-cream-faint">{{ formatEuro(item.product.price) }} each</p>
              <div class="mt-4 flex flex-wrap items-center gap-4">
                <div class="stepper" role="group" :aria-label="`Quantity of ${item.product.name}`">
                  <button type="button" :disabled="busy" aria-label="One less" @click="setQuantity(item, item.quantity - 1)">
                    <font-awesome-icon icon="minus" />
                  </button>
                  <span class="tabular-nums" aria-live="polite">{{ item.quantity }}</span>
                  <button type="button" :disabled="busy || item.quantity >= item.product.stock" aria-label="One more"
                          @click="setQuantity(item, item.quantity + 1)">
                    <font-awesome-icon icon="plus" />
                  </button>
                </div>
                <button type="button" class="line-remove" :disabled="busy" @click="remove(item)">Remove</button>
              </div>
              <p v-if="item.quantity >= item.product.stock" class="mt-2 text-xs text-crust-light">
                That's all we have left today.
              </p>
            </div>
            <p class="line-total">{{ formatEuro(item.totalPrice) }}</p>
          </li>
        </transition-group>
      </ul>

      <!-- Summary -->
      <aside class="summary">
        <div class="summary-card lux-card">
          <h2 class="display-title text-4xl">Summary</h2>
          <dl class="summary-rows">
            <div><dt>Subtotal</dt><dd>{{ formatEuro(cartStore.subtotal) }}</dd></div>
            <div class="is-muted"><dt>Included VAT</dt><dd>{{ formatEuro(cartStore.tax) }}</dd></div>
            <div class="is-total"><dt>Total</dt><dd>{{ formatEuro(cartStore.total) }}</dd></div>
          </dl>
          <p class="text-xs text-cream-faint">
            Pickup on {{ business.street }} is free. A delivery fee is shown at checkout if you choose delivery.
          </p>
          <router-link v-magnetic="0.15" to="/checkout" class="btn-amber mt-6 w-full">
            Checkout <font-awesome-icon icon="arrow-right" />
          </router-link>
          <div class="mt-4 flex items-center justify-between text-sm">
            <router-link to="/products" class="text-cream-muted hover:text-cream">Keep shopping</router-link>
            <button type="button" class="text-cream-faint hover:text-red-300" :disabled="busy" @click="clear">Empty cart</button>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useCartStore } from '@/stores/cartStore'
import { useToast } from '@/composables/useToast'
import { formatEuro } from '@/utils/money'
import { business } from '@/config/business'
import { PLACEHOLDER_IMAGE, applyImageFallback } from '@/utils/imageFallback'
import PageHeader from '@/components/common/PageHeader.vue'
import croissantImg from '@/assets/bakery/croissant-chocolate.png'

const cartStore = useCartStore()
const { showToast } = useToast()
const loading = ref(false)
const busy = ref(false)

async function run(action, success) {
  busy.value = true
  try {
    await action()
    if (success) showToast(success)
  } catch {
    showToast(cartStore.error || 'The cart could not be updated.', 'error')
  } finally {
    busy.value = false
  }
}

const setQuantity = (item, quantity) => run(() => cartStore.updateQuantity(item.product.id, quantity))
const remove = (item) => run(() => cartStore.removeItem(item.product.id), `${item.product.name} removed`)
function clear() {
  if (!window.confirm('Remove everything from your cart?')) return
  run(() => cartStore.clearCart(), 'Your cart is empty')
}

onMounted(async () => {
  loading.value = true
  await cartStore.fetchCart()
  loading.value = false
})
</script>

<style scoped>
.cart-grid {
  display: grid;
  gap: 2rem;
}

@media (min-width: 1024px) {
  .cart-grid {
    grid-template-columns: minmax(0, 1fr) 24rem;
    gap: 3rem;
    align-items: start;
  }
}

.cart-items {
  border-top: 1px solid rgba(244, 236, 225, 0.08);
}

.line {
  display: flex;
  gap: 1.25rem;
  align-items: flex-start;
  padding: 1.5rem 0;
  border-bottom: 1px solid rgba(244, 236, 225, 0.08);
}

.line-media {
  display: grid;
  place-items: center;
  flex-shrink: 0;
  width: 6.5rem;
  height: 6.5rem;
  border-radius: 1.25rem;
  background: radial-gradient(circle at 50% 60%, rgba(230, 161, 90, 0.18), transparent 70%), rgba(244, 236, 225, 0.03);
}

.line-media img {
  width: 80%;
  height: 80%;
  object-fit: contain;
  filter: drop-shadow(0 12px 12px rgba(0, 0, 0, 0.45));
}

.line-name {
  font-family: 'Instrument Serif', Georgia, serif;
  font-size: 1.9rem;
  line-height: 1.05;
  color: #f4ece1;
}

.line-name:hover {
  color: #f2c48d;
}

.line-total {
  font-weight: 700;
  color: #f2c48d;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.line-remove {
  font-size: 0.85rem;
  color: #7d7061;
  text-decoration: underline;
  text-underline-offset: 4px;
}

.line-remove:hover {
  color: #f08f79;
}

.stepper {
  display: inline-flex;
  align-items: center;
  gap: 0.9rem;
  padding: 0.25rem;
  border-radius: 9999px;
  border: 1px solid rgba(244, 236, 225, 0.14);
  color: #f4ece1;
  font-weight: 700;
}

.stepper button {
  display: grid;
  place-items: center;
  width: 2.1rem;
  height: 2.1rem;
  border-radius: 9999px;
  background: rgba(244, 236, 225, 0.06);
  font-size: 0.75rem;
}

.stepper button:hover:not(:disabled) {
  background: rgba(230, 161, 90, 0.25);
}

.stepper button:disabled {
  opacity: 0.35;
}

@media (min-width: 1024px) {
  .summary {
    position: sticky;
    top: 6.5rem;
  }
}

.summary-card {
  padding: 2rem;
}

.summary-rows {
  display: grid;
  gap: 0.75rem;
  margin: 1.5rem 0;
}

.summary-rows div {
  display: flex;
  justify-content: space-between;
  color: #d9cfc2;
  font-variant-numeric: tabular-nums;
}

.summary-rows .is-muted {
  font-size: 0.85rem;
  color: #7d7061;
}

.summary-rows .is-total {
  padding-top: 0.9rem;
  border-top: 1px solid rgba(244, 236, 225, 0.1);
  font-size: 1.25rem;
  font-weight: 700;
  color: #f4ece1;
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 4rem 1.5rem 3.5rem;
  text-align: center;
}

.empty-img {
  width: 11rem;
  margin-bottom: 1.5rem;
  filter: drop-shadow(0 25px 25px rgba(0, 0, 0, 0.5));
  animation: float 5s ease-in-out infinite;
}

@keyframes float {
  50% { transform: translateY(-10px) rotate(-3deg); }
}

@media (prefers-reduced-motion: reduce) {
  .empty-img {
    animation: none;
  }
}

.skeleton {
  background: linear-gradient(100deg, rgba(244, 236, 225, 0.04) 30%, rgba(244, 236, 225, 0.09) 50%, rgba(244, 236, 225, 0.04) 70%);
  background-size: 200% 100%;
  animation: shimmer 1.4s linear infinite;
}

@keyframes shimmer {
  to { background-position: -200% 0; }
}

.line-enter-active,
.line-leave-active {
  transition: opacity 0.35s, transform 0.5s var(--ease-out-expo);
}

.line-enter-from,
.line-leave-to {
  opacity: 0;
  transform: translateX(-16px);
}
</style>
