<template>
  <article v-tilt="{ max: 7 }" class="pcard lux-card" :class="{ 'is-soldout': soldOut }">
    <router-link :to="detailLink" class="pcard-media" :aria-label="name">
      <span class="pcard-halo" aria-hidden="true"></span>
      <img :src="product.image_url || product.image || PLACEHOLDER_IMAGE" :alt="name"
           class="pcard-img" data-depth="60" loading="lazy" @error="applyImageFallback" />
      <span class="pcard-badges" data-depth="35">
        <span v-if="product.is_seasonal" class="pcard-badge is-seasonal">{{ $t('common.seasonal') }}</span>
        <span v-if="product.is_vegan" class="pcard-badge">{{ $t('common.vegan') }}</span>
        <span v-else-if="product.is_vegetarian" class="pcard-badge">{{ $t('common.vegetarian') }}</span>
        <span v-if="product.is_gluten_free" class="pcard-badge">{{ $t('common.glutenFree') }}</span>
      </span>
      <span v-if="soldOut" class="pcard-stock" data-depth="35">{{ $t('common.soldOut') }}</span>
      <span v-else-if="product.stock <= 5" class="pcard-stock is-low" data-depth="35">{{ $t('common.onlyLeft', { count: product.stock }) }}</span>
    </router-link>

    <div class="pcard-body" data-depth="25">
      <p class="eyebrow !text-[0.65rem]">{{ categoryName(product.category) || business.name }}</p>
      <h3 class="pcard-title">
        <router-link :to="detailLink">{{ name }}</router-link>
      </h3>
      <div class="pcard-row">
        <span class="pcard-price">{{ price }}</span>

        <div v-if="cartItem" class="pcard-stepper" role="group" :aria-label="$t('card.inCart', { name })">
          <button type="button" :disabled="busy" :aria-label="$t('common.oneLess')" @click="setQuantity(cartItem.quantity - 1)">
            <font-awesome-icon icon="minus" />
          </button>
          <span class="tabular-nums" aria-live="polite">{{ cartItem.quantity }}</span>
          <button type="button" :disabled="busy || cartItem.quantity >= product.stock" :aria-label="$t('common.oneMore')" @click="setQuantity(cartItem.quantity + 1)">
            <font-awesome-icon icon="plus" />
          </button>
        </div>
        <button v-else type="button" class="pcard-add" :disabled="busy || soldOut"
                :aria-label="$t('card.add', { name })" @click="add">
          <font-awesome-icon :icon="busy ? 'spinner' : 'plus'" :spin="busy" />
        </button>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useCartStore } from '@/stores/cartStore'
import { useToast } from '@/composables/useToast'
import { PLACEHOLDER_IMAGE, applyImageFallback } from '@/utils/imageFallback'
import { formatEuro } from '@/utils/money'
import { useI18n } from 'vue-i18n'
import { business } from '@/config/business'
import { categoryName, localized } from '@/i18n/catalog'

const props = defineProps({
  product: { type: Object, required: true }
})
const emit = defineEmits(['add-to-cart'])

const cartStore = useCartStore()
const { showToast } = useToast()
const busy = ref(false)
const { t } = useI18n()
const name = computed(() => localized(props.product, 'name'))

const detailLink = computed(() => ({ name: 'product-detail', params: { id: props.product.id } }))
const soldOut = computed(() => !props.product.available || props.product.stock <= 0)
const cartItem = computed(() => cartStore.items.find(item => item.product?.id === props.product.id))
const price = computed(() => formatEuro(props.product.price))

async function run(action, success) {
  busy.value = true
  try {
    await action()
    if (success) showToast(success)
  } catch (error) {
    showToast(t('common.cartError'), 'error')
  } finally {
    busy.value = false
  }
}

const add = () => run(async () => {
  await cartStore.addItem(props.product.id, 1)
  emit('add-to-cart', props.product)
}, t('common.addedToCart', { name: name.value }))

const setQuantity = (quantity) => run(() => cartStore.updateQuantity(props.product.id, quantity))
</script>

<style scoped>
.pcard {
  position: relative;
  /* Visible overflow keeps the layers in 3D while the card tilts. */
  overflow: visible;
  display: flex;
  flex-direction: column;
  padding: 0.75rem;
  transform-style: preserve-3d;
}

.pcard-media {
  position: relative;
  display: grid;
  place-items: center;
  aspect-ratio: 1;
  border-radius: 1.1rem;
  background:
    radial-gradient(circle at 50% 60%, rgba(230, 161, 90, 0.16), transparent 62%),
    rgba(244, 236, 225, 0.03);
  transform-style: preserve-3d;
}

.pcard-halo {
  position: absolute;
  inset: 18% 18% 10%;
  border-radius: 50%;
  background: radial-gradient(closest-side, rgba(242, 196, 141, 0.28), transparent);
  filter: blur(18px);
  opacity: 0;
  transition: opacity 0.5s var(--ease-out-expo);
}

.pcard-img {
  position: relative;
  width: 78%;
  height: 78%;
  object-fit: contain;
  filter: drop-shadow(0 24px 22px rgba(0, 0, 0, 0.45));
  transition: scale 0.7s var(--ease-out-expo), rotate 0.7s var(--ease-out-expo);
}

.pcard:hover .pcard-img {
  scale: 1.08;
  rotate: -4deg;
}

.pcard:hover .pcard-halo {
  opacity: 1;
}

.pcard-badges {
  position: absolute;
  top: 0.75rem;
  left: 0.75rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.pcard-badge,
.pcard-stock {
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: #f4ece1;
  background: rgba(14, 12, 10, 0.55);
  border: 1px solid rgba(244, 236, 225, 0.12);
  backdrop-filter: blur(8px);
}

.pcard-badge.is-seasonal {
  color: #0e0c0a;
  background: #f2c48d;
  border-color: transparent;
}

.pcard-stock {
  position: absolute;
  right: 0.75rem;
  bottom: 0.75rem;
}

.pcard-stock.is-low {
  color: #f2c48d;
}

.pcard-body {
  padding: 1rem 0.5rem 0.4rem;
}

.pcard-title {
  margin-top: 0.3rem;
  font-family: 'Instrument Serif', Georgia, serif;
  font-size: 1.65rem;
  font-weight: 400;
  line-height: 1.05;
  color: #f4ece1;
}

.pcard-title a {
  color: inherit;
}

.pcard-title a::after {
  /* The whole card is clickable; buttons sit above this layer. */
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
}

.pcard-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 0.9rem;
}

.pcard-price {
  font-size: 1.05rem;
  font-weight: 700;
  color: #f2c48d;
  font-variant-numeric: tabular-nums;
}

.pcard-add,
.pcard-stepper {
  position: relative;
  z-index: 1;
}

.pcard-add {
  display: grid;
  place-items: center;
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 9999px;
  color: #0e0c0a;
  background: #e6a15a;
  box-shadow: 0 10px 30px -10px rgba(230, 161, 90, 0.8);
  transition: transform 0.4s var(--ease-out-expo), background 0.3s;
}

.pcard-add:hover:not(:disabled) {
  transform: rotate(90deg) scale(1.08);
  background: #f2c48d;
}

.pcard-add:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.pcard-stepper {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.25rem;
  border-radius: 9999px;
  border: 1px solid rgba(244, 236, 225, 0.14);
  color: #f4ece1;
}

.pcard-stepper button {
  display: grid;
  place-items: center;
  width: 2rem;
  height: 2rem;
  border-radius: 9999px;
  background: rgba(244, 236, 225, 0.06);
  font-size: 0.75rem;
}

.pcard-stepper button:hover:not(:disabled) {
  background: rgba(230, 161, 90, 0.25);
}

.pcard-stepper button:disabled {
  opacity: 0.35;
}

.is-soldout .pcard-img {
  filter: grayscale(0.6) drop-shadow(0 24px 22px rgba(0, 0, 0, 0.45));
  opacity: 0.7;
}
</style>
