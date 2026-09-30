<template>
  <div class="pd pb-24">
    <!-- Loading -->
    <section v-if="!product && productStore.loading" class="section pd-grid" aria-busy="true">
      <div class="pd-stage skeleton"></div>
      <div class="space-y-4 pt-10">
        <div class="skeleton h-4 w-32 rounded-full"></div>
        <div class="skeleton h-16 w-3/4 rounded-2xl"></div>
        <div class="skeleton h-6 w-24 rounded-full"></div>
        <div class="skeleton h-28 w-full rounded-2xl"></div>
      </div>
    </section>

    <!-- Error -->
    <section v-else-if="!product" class="section py-32 text-center">
      <p class="eyebrow justify-center">Something went wrong</p>
      <h1 class="display-title text-5xl mt-4">We couldn't load this product.</h1>
      <button type="button" class="btn-amber mt-8" @click="loadProduct">
        <font-awesome-icon icon="rotate" /> Try again
      </button>
    </section>

    <template v-else>
      <section class="section pd-grid">
        <!-- Stage: 3D view or photo -->
        <div class="pd-stage-col">
          <div class="pd-stage">
            <span class="pd-stage-glow" aria-hidden="true"></span>
            <ProductViewer3D v-if="view === '3d'" :key="product.id" :image="imageUrl" :model="product.model_3d_url || ''"
                             :alt="product.name" @error="view = 'photo'" />
            <img v-else :src="imageUrl" :alt="product.name" class="pd-photo" @error="applyImageFallback" />

            <div class="pd-toggle" role="group" aria-label="View">
              <button type="button" :class="{ 'is-active': view === '3d' }" :aria-pressed="view === '3d'" @click="view = '3d'">
                <font-awesome-icon icon="cube" /> 3D
              </button>
              <button type="button" :class="{ 'is-active': view === 'photo' }" :aria-pressed="view === 'photo'" @click="view = 'photo'">
                <font-awesome-icon icon="image" /> Photo
              </button>
            </div>

            <div class="pd-actions">
              <button type="button" class="pd-icon" :class="{ 'is-on': isInWishlist }"
                      :aria-label="isInWishlist ? 'Remove from wishlist' : 'Save to wishlist'" :aria-pressed="isInWishlist" @click="toggleWishlist">
                <font-awesome-icon :icon="[isInWishlist ? 'fas' : 'far', 'heart']" />
              </button>
              <button type="button" class="pd-icon" :class="{ 'is-on': isInCompare }"
                      :aria-label="isInCompare ? 'Remove from compare' : 'Add to compare'" :aria-pressed="isInCompare" @click="toggleCompare">
                <font-awesome-icon icon="code-compare" />
              </button>
              <button type="button" class="pd-icon" aria-label="Share" @click="shareProduct">
                <font-awesome-icon icon="share-nodes" />
              </button>
            </div>
          </div>
        </div>

        <!-- Info -->
        <div class="pd-info">
          <nav aria-label="Breadcrumb" class="pd-crumbs">
            <router-link to="/">Home</router-link>
            <span aria-hidden="true">/</span>
            <router-link to="/products">Shop</router-link>
            <template v-if="product.category?.slug">
              <span aria-hidden="true">/</span>
              <router-link :to="{ name: 'category', params: { category: product.category.slug } }">{{ product.category.name }}</router-link>
            </template>
          </nav>

          <p class="eyebrow mt-8">
            {{ product.category?.name || 'Backlover' }}
            <span v-if="product.is_seasonal" class="pd-chip is-seasonal">Seasonal</span>
          </p>
          <h1 :key="product.id" v-split.load class="display-title text-6xl sm:text-7xl mt-3">{{ product.name }}</h1>

          <div v-reveal="{ delay: 0.2 }" class="mt-6 flex flex-wrap items-center gap-4">
            <span class="pd-price">{{ formatEuro(product.price) }}</span>
            <span class="pd-stock" :class="stockTone">
              <span class="pd-dot"></span>{{ stockLabel }}
            </span>
          </div>

          <p v-reveal="{ delay: 0.3 }" class="pd-description">{{ product.description }}</p>

          <div v-if="dietary.length" v-reveal="{ delay: 0.35 }" class="mt-5 flex flex-wrap gap-2">
            <span v-for="tag in dietary" :key="tag.label" class="pd-chip">
              <font-awesome-icon :icon="tag.icon" /> {{ tag.label }}
            </span>
          </div>

          <!-- Purchase -->
          <div v-reveal="{ delay: 0.4 }" class="pd-buy">
            <template v-if="cartItem">
              <div class="pd-stepper" role="group" aria-label="Quantity in cart">
                <button type="button" :disabled="busy" aria-label="One less" @click="setCartQuantity(cartItem.quantity - 1)">
                  <font-awesome-icon icon="minus" />
                </button>
                <span class="tabular-nums" aria-live="polite">{{ cartItem.quantity }}</span>
                <button type="button" :disabled="busy || cartItem.quantity >= product.stock" aria-label="One more" @click="setCartQuantity(cartItem.quantity + 1)">
                  <font-awesome-icon icon="plus" />
                </button>
              </div>
              <router-link to="/cart" class="btn-amber flex-1">
                In your cart · Go to cart <font-awesome-icon icon="arrow-right" />
              </router-link>
            </template>
            <template v-else>
              <div class="pd-stepper" role="group" aria-label="Quantity">
                <button type="button" :disabled="quantity <= 1" aria-label="One less" @click="quantity--">
                  <font-awesome-icon icon="minus" />
                </button>
                <span class="tabular-nums" aria-live="polite">{{ quantity }}</span>
                <button type="button" :disabled="quantity >= product.stock" aria-label="One more" @click="quantity++">
                  <font-awesome-icon icon="plus" />
                </button>
              </div>
              <button v-magnetic="0.15" type="button" class="btn-amber flex-1" :disabled="busy || soldOut" @click="addToCart">
                <template v-if="soldOut">Sold out today</template>
                <template v-else>
                  <font-awesome-icon :icon="busy ? 'spinner' : 'cart-plus'" :spin="busy" />
                  Add to cart<span class="hidden sm:inline"> · {{ formatEuro(product.price * quantity) }}</span>
                </template>
              </button>
            </template>
          </div>

          <ul v-reveal.stagger="{ delay: 0.45 }" class="pd-service">
            <li><font-awesome-icon icon="store" /> <span>Pick up at {{ business.street }}, {{ business.city }}<small v-if="business.transit"> · {{ business.transit }}</small></span></li>
            <li><font-awesome-icon icon="truck" /> <span>Delivery across {{ business.city }}</span></li>
            <li><font-awesome-icon icon="credit-card" /> <span>Pay cash or card on pickup or delivery</span></li>
          </ul>

          <!-- Details -->
          <div class="pd-details">
            <details v-if="product.ingredients?.length" open>
              <summary>Ingredients <span>{{ product.ingredients.length }}</span></summary>
              <p class="pd-ingredients">{{ product.ingredients.map(i => i.name).join(', ') }}</p>
            </details>
            <details v-if="product.allergens?.length">
              <summary>Allergens <span>{{ product.allergens.length }}</span></summary>
              <ul class="pd-allergens">
                <li v-for="allergen in product.allergens" :key="allergen.id">
                  <strong>{{ allergen.name }}</strong>
                  <span v-if="allergen.description">{{ allergen.description }}</span>
                </li>
              </ul>
            </details>
            <details v-if="nutrition.length">
              <summary>Nutrition <span>per 100 g</span></summary>
              <dl class="pd-nutrition">
                <div v-for="row in nutrition" :key="row.label">
                  <dt>{{ row.label }}</dt>
                  <dd>{{ row.value }}</dd>
                </div>
              </dl>
            </details>
          </div>
        </div>
      </section>

      <!-- Related -->
      <section v-if="productStore.relatedProducts.length" class="section mt-32">
        <div class="flex items-end justify-between gap-6">
          <div>
            <p v-reveal class="eyebrow">Also from the oven</p>
            <h2 v-split class="display-title text-5xl mt-3">You might also like</h2>
          </div>
          <router-link to="/products" class="btn-ghost hidden sm:inline-flex">
            All products <font-awesome-icon icon="arrow-right" />
          </router-link>
        </div>
        <div v-reveal.stagger class="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <ProductCard v-for="item in productStore.relatedProducts.slice(0, 4)" :key="item.id" :product="item" />
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useProductStore } from '@/stores/productStore'
import { useCartStore } from '@/stores/cartStore'
import { useWishlistStore } from '@/stores/wishlistStore'
import { useCompareStore } from '@/stores/compareStore'
import { useToast } from '@/composables/useToast'
import { PLACEHOLDER_IMAGE, applyImageFallback } from '@/utils/imageFallback'
import { formatEuro } from '@/utils/money'
import { business } from '@/config/business'
import { webglAvailable } from '@/three/webgl'
import ProductViewer3D from '@/components/three/ProductViewer3D.vue'
import ProductCard from './ProductCard.vue'

const route = useRoute()
const productStore = useProductStore()
const cartStore = useCartStore()
const wishlistStore = useWishlistStore()
const compareStore = useCompareStore()
const { showToast } = useToast()

const quantity = ref(1)
const busy = ref(false)
const view = ref(webglAvailable() ? '3d' : 'photo')

// Only show the product that matches the URL (the store may still hold the
// previous one while the next loads).
const product = computed(() => {
  const current = productStore.product
  return current && String(current.id) === String(route.params.id) ? current : null
})
const imageUrl = computed(() => product.value?.image_url || product.value?.image || PLACEHOLDER_IMAGE)
const cartItem = computed(() => cartStore.items.find(item => item.product?.id === product.value?.id))
const isInWishlist = computed(() => wishlistStore.items.some(item => item.id === product.value?.id))
const isInCompare = computed(() => compareStore.items.some(item => item.id === product.value?.id))
const soldOut = computed(() => !product.value?.available || product.value?.stock <= 0)

const stockLabel = computed(() => {
  if (soldOut.value) return 'Sold out today'
  if (product.value.stock <= 5) return `Only ${product.value.stock} left`
  return 'Fresh today'
})
const stockTone = computed(() => (soldOut.value ? 'is-out' : product.value.stock <= 5 ? 'is-low' : 'is-in'))

const dietary = computed(() => [
  product.value.is_vegan && { label: 'Vegan', icon: 'leaf' },
  !product.value.is_vegan && product.value.is_vegetarian && { label: 'Vegetarian', icon: 'seedling' },
  product.value.is_gluten_free && { label: 'Gluten free', icon: 'wheat-awn' }
].filter(Boolean))

const nutrition = computed(() => {
  const info = product.value?.nutrition_info
  if (!info) return []
  return [
    ['Energy', info.calories, 'kcal'],
    ['Protein', info.proteins, 'g'],
    ['Carbohydrates', info.carbohydrates, 'g'],
    ['Fat', info.fats, 'g'],
    ['Fibre', info.fiber, 'g']
  ].filter(([, value]) => value !== null && value !== undefined)
    .map(([label, value, unit]) => ({ label, value: `${value} ${unit}` }))
})

async function loadProduct() {
  quantity.value = 1
  const found = await productStore.fetchProductById(route.params.id)
  if (!found) return
  productStore.fetchRelatedProducts(route.params.id).catch(() => {})
}

async function withBusy(action, success) {
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

const addToCart = () => withBusy(
  () => cartStore.addItem(product.value.id, quantity.value),
  `${product.value.name} added to your cart`
)
const setCartQuantity = (value) => withBusy(() => cartStore.updateQuantity(product.value.id, value))

function toggleWishlist() {
  if (isInWishlist.value) {
    wishlistStore.removeItem(product.value.id)
    showToast('Removed from your wishlist')
  } else {
    wishlistStore.addItem(product.value)
    showToast('Saved to your wishlist')
  }
}

function toggleCompare() {
  if (isInCompare.value) {
    compareStore.removeItem(product.value.id)
    showToast('Removed from compare')
  } else if (compareStore.items.length >= 4) {
    showToast('You can compare up to 4 products', 'warning')
  } else {
    compareStore.addItem(product.value)
    showToast('Added to compare')
  }
}

async function shareProduct() {
  try {
    if (navigator.share) {
      await navigator.share({ title: product.value.name, url: window.location.href })
    } else {
      await navigator.clipboard.writeText(window.location.href)
      showToast('Link copied')
    }
  } catch (error) {
    if (error?.name !== 'AbortError') showToast('Could not share this page', 'error')
  }
}

watch(() => route.params.id, (id) => { if (id) loadProduct() }, { immediate: true })
watch(product, (value) => { if (value) document.title = `${value.name} - ${business.name}` })
</script>

<style scoped>
.pd {
  padding-top: 1rem;
}

.pd-grid {
  display: grid;
  gap: 3rem;
}

@media (min-width: 1024px) {
  .pd-grid {
    grid-template-columns: minmax(0, 1.15fr) minmax(0, 1fr);
    gap: 4.5rem;
  }

  .pd-stage-col {
    position: sticky;
    top: 6.5rem;
    align-self: start;
  }
}

.pd-stage {
  position: relative;
  height: min(62vh, 520px);
  min-height: 340px;
  border-radius: 2rem;
  overflow: hidden;
  border: 1px solid rgba(244, 236, 225, 0.08);
  background:
    radial-gradient(120% 90% at 50% 100%, rgba(210, 96, 63, 0.14), transparent 60%),
    radial-gradient(80% 70% at 50% 40%, rgba(230, 161, 90, 0.14), transparent 70%),
    linear-gradient(180deg, #1e1914, #15120f);
}

@media (min-width: 1024px) {
  .pd-stage {
    height: min(78vh, 720px);
  }
}

.pd-stage-glow {
  position: absolute;
  left: 50%;
  bottom: 12%;
  width: 60%;
  height: 12%;
  transform: translateX(-50%);
  border-radius: 50%;
  background: radial-gradient(closest-side, rgba(242, 196, 141, 0.25), transparent);
  filter: blur(20px);
  pointer-events: none;
}

.pd-photo {
  position: absolute;
  inset: 10%;
  width: 80%;
  height: 80%;
  object-fit: contain;
  filter: drop-shadow(0 40px 40px rgba(0, 0, 0, 0.5));
}

.pd-toggle {
  position: absolute;
  left: 1rem;
  bottom: 1rem;
  display: inline-flex;
  padding: 0.25rem;
  border-radius: 9999px;
  background: rgba(14, 12, 10, 0.6);
  border: 1px solid rgba(244, 236, 225, 0.12);
  backdrop-filter: blur(12px);
  z-index: 2;
}

.pd-toggle button {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.45rem 0.95rem;
  border-radius: 9999px;
  font-size: 0.8rem;
  font-weight: 600;
  color: #b9ab98;
  transition: background 0.3s, color 0.3s;
}

.pd-toggle button.is-active {
  color: #0e0c0a;
  background: #e6a15a;
}

.pd-actions {
  position: absolute;
  top: 1rem;
  left: 1rem;
  display: flex;
  gap: 0.5rem;
  z-index: 2;
}

.pd-icon {
  display: grid;
  place-items: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 9999px;
  color: #f4ece1;
  background: rgba(14, 12, 10, 0.55);
  border: 1px solid rgba(244, 236, 225, 0.12);
  backdrop-filter: blur(12px);
  transition: color 0.3s, background 0.3s;
}

.pd-icon:hover {
  background: rgba(14, 12, 10, 0.8);
}

.pd-icon.is-on {
  color: #e6a15a;
}

.pd-crumbs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  font-size: 0.85rem;
  color: #7d7061;
}

.pd-crumbs a {
  color: #b9ab98;
}

.pd-crumbs a:hover {
  color: #f4ece1;
}

.pd-price {
  font-size: 2rem;
  font-weight: 700;
  color: #f2c48d;
  font-variant-numeric: tabular-nums;
}

.pd-stock {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.35rem 0.85rem;
  border-radius: 9999px;
  font-size: 0.8rem;
  font-weight: 600;
  border: 1px solid rgba(244, 236, 225, 0.12);
}

.pd-dot {
  width: 0.45rem;
  height: 0.45rem;
  border-radius: 50%;
  background: currentColor;
  box-shadow: 0 0 0 4px color-mix(in srgb, currentColor 20%, transparent);
}

.pd-stock.is-in { color: #9fd49a; }
.pd-stock.is-low { color: #f2c48d; }
.pd-stock.is-out { color: #f08f79; }

.pd-description {
  margin-top: 1.5rem;
  max-width: 34rem;
  font-size: 1.1rem;
  line-height: 1.7;
  color: #d9cfc2;
}

.pd-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.3rem 0.8rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  text-transform: none;
  color: #d9cfc2;
  border: 1px solid rgba(244, 236, 225, 0.14);
}

.pd-chip.is-seasonal {
  color: #0e0c0a;
  background: #f2c48d;
  border-color: transparent;
}

.pd-buy {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 2.25rem;
}

.pd-stepper {
  display: inline-flex;
  align-items: center;
  gap: 1rem;
  padding: 0.35rem;
  border-radius: 9999px;
  border: 1px solid rgba(244, 236, 225, 0.14);
  color: #f4ece1;
  font-weight: 700;
}

.pd-stepper button {
  display: grid;
  place-items: center;
  width: 2.6rem;
  height: 2.6rem;
  border-radius: 9999px;
  background: rgba(244, 236, 225, 0.06);
  transition: background 0.3s;
}

.pd-stepper button:hover:not(:disabled) {
  background: rgba(230, 161, 90, 0.25);
}

.pd-stepper button:disabled {
  opacity: 0.35;
}

.pd-service {
  display: grid;
  gap: 0.75rem;
  margin-top: 2rem;
  padding: 1.25rem 1.4rem;
  border-radius: 1.5rem;
  background: rgba(244, 236, 225, 0.03);
  border: 1px solid rgba(244, 236, 225, 0.07);
  font-size: 0.92rem;
  color: #d9cfc2;
}

.pd-service li {
  display: flex;
  gap: 0.8rem;
  align-items: baseline;
}

.pd-service svg {
  width: 1rem;
  color: #e6a15a;
}

.pd-service small {
  color: #7d7061;
  font-size: inherit;
}

.pd-details {
  margin-top: 2rem;
  border-top: 1px solid rgba(244, 236, 225, 0.08);
}

.pd-details details {
  border-bottom: 1px solid rgba(244, 236, 225, 0.08);
}

.pd-details summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.15rem 0;
  cursor: pointer;
  list-style: none;
  font-family: 'Instrument Serif', Georgia, serif;
  font-size: 1.6rem;
  color: #f4ece1;
}

.pd-details summary::-webkit-details-marker {
  display: none;
}

.pd-details summary span {
  font-family: 'Manrope Variable', system-ui, sans-serif;
  font-size: 0.8rem;
  color: #7d7061;
}

.pd-details summary::after {
  content: '+';
  margin-left: 1rem;
  font-family: 'Manrope Variable', system-ui, sans-serif;
  font-size: 1.25rem;
  color: #e6a15a;
  transition: transform 0.3s;
}

.pd-details details[open] summary::after {
  transform: rotate(45deg);
}

.pd-details summary span {
  margin-left: auto;
}

.pd-ingredients {
  padding-bottom: 1.25rem;
  line-height: 1.7;
  color: #b9ab98;
}

.pd-allergens {
  display: grid;
  gap: 0.6rem;
  padding-bottom: 1.25rem;
}

.pd-allergens li {
  display: flex;
  flex-direction: column;
  color: #b9ab98;
  font-size: 0.92rem;
}

.pd-allergens strong {
  color: #f4ece1;
}

.pd-nutrition {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(8.5rem, 1fr));
  gap: 0.75rem;
  padding-bottom: 1.25rem;
}

.pd-nutrition div {
  padding: 0.85rem 1rem;
  border-radius: 1rem;
  background: rgba(244, 236, 225, 0.04);
}

.pd-nutrition dt {
  font-size: 0.75rem;
  color: #7d7061;
}

.pd-nutrition dd {
  margin-top: 0.2rem;
  font-weight: 700;
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
