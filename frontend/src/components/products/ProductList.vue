<template>
  <div class="section pb-10">
    <!-- Header -->
    <header class="pt-6">
      <p v-reveal class="eyebrow">{{ heading.kicker }}</p>
      <div class="mt-3 flex flex-wrap items-end justify-between gap-6">
        <h1 :key="heading.title" v-split.load class="display-title text-6xl sm:text-8xl">{{ heading.title }}</h1>
        <p v-if="!productStore.loading" class="text-cream-faint tabular-nums">
          {{ $t('common.products', productStore.pagination.count) }}
        </p>
      </div>
      <p v-if="heading.subtitle" v-reveal="{ delay: 0.15 }" class="mt-4 max-w-xl text-lg text-cream-muted">{{ heading.subtitle }}</p>
    </header>

    <!-- Categories -->
    <nav class="pills mt-10" :aria-label="$t('shop.categories')">
      <router-link to="/products" class="pill" :class="{ 'is-active': !routeCategory && !isSeasonal }">{{ $t('shop.all') }}</router-link>
      <router-link v-for="category in categories" :key="category.slug"
                   :to="{ name: 'category', params: { category: category.slug } }"
                   class="pill" :class="{ 'is-active': routeCategory === category.slug }">
        {{ categoryName(category) }}
      </router-link>
      <router-link :to="{ name: 'seasonal' }" class="pill" :class="{ 'is-active': isSeasonal }">
        <font-awesome-icon icon="fire" class="text-ember" /> {{ $t('common.seasonal') }}
      </router-link>
    </nav>

    <!-- Toolbar -->
    <div class="toolbar">
      <div class="flex flex-wrap gap-2" role="group" :aria-label="$t('shop.dietary')">
        <button v-for="option in dietaryOptions" :key="option.key" type="button" class="chip"
                :class="{ 'is-on': dietary[option.key] }" :aria-pressed="dietary[option.key]"
                @click="dietary[option.key] = !dietary[option.key]">
          <font-awesome-icon :icon="option.icon" /> {{ $t(option.label) }}
        </button>
        <button type="button" class="chip" :class="{ 'is-on': showPrice }" :aria-expanded="showPrice" @click="showPrice = !showPrice">
          <font-awesome-icon icon="euro-sign" /> {{ $t('shop.price') }}
        </button>
      </div>
      <div class="flex items-center gap-3">
        <button v-if="hasFilters" type="button" class="text-sm text-cream-muted underline-offset-4 hover:text-cream hover:underline" @click="clearFilters">
          {{ $t('shop.clearFilters') }}
        </button>
        <label class="sr-only" for="sort">{{ $t('shop.sortBy') }}</label>
        <select id="sort" v-model="sortBy" class="sort">
          <option value="name">{{ $t('shop.sortName') }}</option>
          <option value="price_asc">{{ $t('shop.sortPriceAsc') }}</option>
          <option value="price_desc">{{ $t('shop.sortPriceDesc') }}</option>
          <option value="newest">{{ $t('shop.sortNewest') }}</option>
        </select>
      </div>
    </div>

    <transition name="expand">
      <div v-if="showPrice" class="price-row">
        <label>
          <span>{{ $t('shop.min') }}</span>
          <input v-model.number="priceMin" type="number" min="0" step="0.5" inputmode="decimal" placeholder="0" />
        </label>
        <span class="text-cream-faint">–</span>
        <label>
          <span>{{ $t('shop.max') }}</span>
          <input v-model.number="priceMax" type="number" min="0" step="0.5" inputmode="decimal" :placeholder="$t('shop.any')" />
        </label>
      </div>
    </transition>

    <!-- Grid -->
    <div v-if="productStore.loading && !productStore.products.length" class="grid-products" aria-busy="true">
      <div v-for="n in 8" :key="n" class="skeleton-card">
        <div class="skeleton aspect-square rounded-2xl"></div>
        <div class="skeleton mt-4 h-3 w-16 rounded-full"></div>
        <div class="skeleton mt-3 h-6 w-2/3 rounded-full"></div>
      </div>
    </div>

    <p v-else-if="productStore.error" class="empty">
      <span class="display-title text-4xl">{{ $t('shop.loadError') }}</span>
      <button type="button" class="btn-ghost mt-6" @click="loadProducts">{{ $t('common.tryAgain') }}</button>
    </p>

    <div v-else-if="!productStore.products.length" class="empty">
      <font-awesome-icon icon="box-open" class="text-4xl text-crust" />
      <span class="display-title text-4xl mt-4">{{ $t('shop.emptyTitle') }}</span>
      <p class="mt-2 text-cream-muted">{{ $t('shop.emptyText') }}</p>
      <button v-if="hasFilters" type="button" class="btn-ghost mt-6" @click="clearFilters">{{ $t('shop.clearFilters') }}</button>
    </div>

    <div v-else ref="grid" class="grid-products" :class="{ 'is-refreshing': productStore.loading }">
      <ProductCard v-for="product in productStore.products" :key="product.id" :product="product" />
    </div>

    <!-- Pagination -->
    <nav v-if="totalPages > 1" class="pager" :aria-label="$t('shop.pages')">
      <button type="button" class="btn-ghost" :disabled="!productStore.hasPreviousPage" @click="goTo(currentPage - 1)">
        <font-awesome-icon icon="arrow-right" class="rotate-180" /> {{ $t('common.previous') }}
      </button>
      <span class="tabular-nums text-cream-muted">{{ currentPage }} / {{ totalPages }}</span>
      <button type="button" class="btn-ghost" :disabled="!productStore.hasNextPage" @click="goTo(currentPage + 1)">
        {{ $t('common.next') }} <font-awesome-icon icon="arrow-right" />
      </button>
    </nav>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useProductStore } from '@/stores/productStore'
import { gsap, ScrollTrigger, prefersReducedMotion, scrollToTop } from '@/motion'
import { business } from '@/config/business'
import { usePageMeta } from '@/seo'
import { useI18n } from 'vue-i18n'
import { categoryName, categoryDescription } from '@/i18n/catalog'
import ProductCard from './ProductCard.vue'

const productStore = useProductStore()
const route = useRoute()

const { t } = useI18n()
const grid = ref(null)
const sortBy = ref('name')
const currentPage = ref(1)
const showPrice = ref(false)
const priceMin = ref('')
const priceMax = ref('')
const dietary = reactive({ vegan: false, vegetarian: false, glutenFree: false })

const dietaryOptions = [
  { key: 'vegan', label: 'common.vegan', icon: 'leaf' },
  { key: 'vegetarian', label: 'common.vegetarian', icon: 'seedling' },
  { key: 'glutenFree', label: 'common.glutenFree', icon: 'wheat-awn' }
]

const categories = computed(() => productStore.categories.filter(c => c.is_active !== false))
const totalPages = computed(() => productStore.pagination.total_pages || 1)

// Category pages (/categories/:category), the seasonal page and search
// results reuse this list with a fixed filter from the route.
const routeCategory = computed(() => route.params.category || '')
const isSeasonal = computed(() => Boolean(route.meta.seasonal))
const searchQuery = computed(() => (route.query.search || '').toString().trim())

const heading = computed(() => {
  if (routeCategory.value) {
    const category = categories.value.find(c => c.slug === routeCategory.value)
    return { kicker: t('shop.category'), title: categoryName(category) || t('shop.category'), subtitle: categoryDescription(category) }
  }
  if (isSeasonal.value) return { kicker: t('shop.seasonalKicker'), title: t('common.seasonal'), subtitle: t('shop.seasonalText') }
  if (searchQuery.value) return { kicker: t('common.search'), title: t('shop.searchTitle', { query: searchQuery.value }), subtitle: '' }
  return { kicker: t('shop.kicker'), title: t('shop.title'), subtitle: t('shop.subtitle', { street: business.street, city: business.city }) }
})

const hasFilters = computed(() =>
  Object.values(dietary).some(Boolean) || priceMin.value !== '' || priceMax.value !== ''
)

async function loadProducts() {
  await productStore.fetchProducts({
    page: currentPage.value,
    ordering: sortBy.value,
    category: routeCategory.value,
    seasonal: isSeasonal.value,
    search: searchQuery.value,
    price_min: priceMin.value !== '' && priceMin.value > 0 ? priceMin.value : null,
    price_max: priceMax.value !== '' && priceMax.value > 0 ? priceMax.value : null,
    is_vegan: dietary.vegan,
    is_vegetarian: dietary.vegetarian,
    is_gluten_free: dietary.glutenFree
  }).catch(() => {})
  await nextTick()
  animateGrid()
}

// Cards rise in one after another whenever a new set arrives.
function animateGrid() {
  ScrollTrigger.refresh()
  if (!grid.value || prefersReducedMotion()) return
  gsap.fromTo(grid.value.children,
    { y: 40, opacity: 0 },
    { y: 0, opacity: 1, duration: 0.8, ease: 'power3.out', stagger: 0.05, clearProps: 'transform,opacity' })
}

function reload() {
  currentPage.value = 1
  loadProducts()
}

function goTo(page) {
  currentPage.value = page
  scrollToTop()
  loadProducts()
}

function clearFilters() {
  Object.keys(dietary).forEach(key => { dietary[key] = false })
  priceMin.value = ''
  priceMax.value = ''
}

let priceTimer = null
watch([priceMin, priceMax], () => {
  clearTimeout(priceTimer)
  priceTimer = setTimeout(reload, 400)
})
watch([sortBy, () => ({ ...dietary })], reload, { deep: true })
watch(() => [route.params.category, route.meta.seasonal, route.query.search], reload)
usePageMeta(() => ({
  title: heading.value.title,
  description: heading.value.subtitle || undefined,
  // Filtered result lists (search) should not be indexed.
  noindex: Boolean(searchQuery.value) || undefined
}))

onMounted(() => {
  if (!productStore.categories.length) productStore.fetchCategories()
  loadProducts()
})
</script>

<style scoped>
.pills {
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
  padding-bottom: 0.25rem;
  scrollbar-width: none;
}

.pill {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  flex-shrink: 0;
  padding: 0.6rem 1.2rem;
  border-radius: 9999px;
  font-size: 0.92rem;
  font-weight: 600;
  color: #d9cfc2;
  border: 1px solid rgba(244, 236, 225, 0.12);
  transition: background 0.3s, color 0.3s, border-color 0.3s;
}

.pill:hover {
  color: #f4ece1;
  border-color: rgba(244, 236, 225, 0.3);
}

.pill.is-active {
  color: #0e0c0a;
  background: #f4ece1;
  border-color: transparent;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 1.5rem;
  padding: 1.25rem 0;
  border-block: 1px solid rgba(244, 236, 225, 0.07);
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.45rem 0.95rem;
  border-radius: 9999px;
  font-size: 0.85rem;
  font-weight: 600;
  color: #b9ab98;
  background: rgba(244, 236, 225, 0.04);
  transition: background 0.3s, color 0.3s;
}

.chip:hover {
  color: #f4ece1;
}

.chip.is-on {
  color: #0e0c0a;
  background: #e6a15a;
}

.sort {
  padding: 0.55rem 2.25rem 0.55rem 1rem;
  border-radius: 9999px;
  font-size: 0.9rem;
  color: #f4ece1;
  background: rgba(244, 236, 225, 0.04);
  border: 1px solid rgba(244, 236, 225, 0.12);
}

.price-row {
  display: flex;
  align-items: flex-end;
  gap: 1rem;
  padding: 1.25rem 0 0.25rem;
}

.price-row label {
  display: grid;
  gap: 0.35rem;
  font-size: 0.75rem;
  color: #7d7061;
}

.price-row input {
  width: 8rem;
  padding: 0.55rem 0.9rem;
  border-radius: 0.9rem;
  background: rgba(244, 236, 225, 0.04);
  border: 1px solid rgba(244, 236, 225, 0.12);
  color: #f4ece1;
}

.grid-products {
  display: grid;
  gap: 1.25rem;
  margin-top: 2.5rem;
  grid-template-columns: repeat(auto-fill, minmax(min(100%, 16.5rem), 1fr));
  transition: opacity 0.3s;
}

.grid-products.is-refreshing {
  opacity: 0.5;
}

.skeleton-card {
  padding: 0.75rem;
  border-radius: 1.5rem;
  border: 1px solid rgba(244, 236, 225, 0.06);
}

.skeleton {
  background: linear-gradient(100deg, rgba(244, 236, 225, 0.04) 30%, rgba(244, 236, 225, 0.09) 50%, rgba(244, 236, 225, 0.04) 70%);
  background-size: 200% 100%;
  animation: shimmer 1.4s linear infinite;
}

@keyframes shimmer {
  to { background-position: -200% 0; }
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 6rem 1rem;
  text-align: center;
}

.pager {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.5rem;
  margin-top: 4rem;
}

.pager button:disabled {
  opacity: 0.35;
  pointer-events: none;
}

.expand-enter-active,
.expand-leave-active {
  transition: opacity 0.3s, transform 0.4s var(--ease-out-expo);
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
