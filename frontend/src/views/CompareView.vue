<template>
  <div class="section pb-10">
    <div>
      <PageHeader :eyebrow="$t('compare.eyebrow')" :title="$t('compare.title')" :subtitle="$t('compare.subtitle')" />

      <div v-if="loading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-white/20"></div>
      </div>

      <div v-else-if="!products.length" class="glass-panel text-center py-12">
        <p class="display-title text-4xl">{{ $t('compare.emptyTitle') }}</p>
        <p class="mt-2 text-cream-muted">{{ $t('compare.emptyText') }}</p>
        <router-link to="/products" class="btn-amber mt-6">{{ $t('common.browseProducts') }}</router-link>
      </div>

      <div v-else class="glass-panel overflow-x-auto">
        <table class="w-full min-w-[40rem] text-start text-gray-300 compare-table">
          <thead>
            <tr>
              <th scope="col" class="w-40"></th>
              <th v-for="product in products" :key="product.id" scope="col" class="align-top">
                <img :src="product.image_url || product.image || PLACEHOLDER_IMAGE" :alt="localized(product, 'name')"
                     class="h-24 w-24 rounded-lg object-contain bg-white/5" @error="applyImageFallback" />
                <router-link :to="{ name: 'product-detail', params: { id: product.id } }"
                             class="mt-2 block font-display text-2xl text-cream hover:text-crust-light">{{ localized(product, 'name') }}</router-link>
                <button type="button" class="mt-1 text-sm text-gray-400 hover:text-red-300 bg-transparent" @click="remove(product.id)">{{ $t('common.remove') }}</button>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows" :key="row.label">
              <th scope="row" class="text-gray-400 font-medium">{{ $t(row.label) }}</th>
              <td v-for="product in products" :key="product.id" class="tabular-nums">{{ row.value(product) }}</td>
            </tr>
          </tbody>
        </table>
        <div class="mt-4">
          <button type="button" class="btn-ghost" @click="clearAll">{{ $t('compare.clear') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import PageHeader from '@/components/common/PageHeader.vue'
import { useCompareStore } from '@/stores/compareStore'
import { useFreshProducts } from '@/composables/useFreshProducts'
import { PLACEHOLDER_IMAGE, applyImageFallback } from '@/utils/imageFallback'
import { useI18n } from 'vue-i18n'
import { formatEuro } from '@/utils/money'
import { categoryName, localized } from '@/i18n/catalog'

const compareStore = useCompareStore()
const { products, missingIds, loading, load } = useFreshProducts()

const { t } = useI18n()
const yesNo = (value) => (value ? t('compare.yes') : t('compare.no'))
const nutrient = (key, unit) => (product) => {
  const value = product.nutrition_info?.[key]
  return value != null ? `${Number(value).toFixed(1)} ${unit}` : '—'
}

const rows = [
  { label: 'shop.price', value: p => formatEuro(p.price) },
  { label: 'shop.category', value: p => categoryName(p.category) || '—' },
  { label: 'compare.inStock', value: p => yesNo(p.available && p.stock > 0) },
  { label: 'common.vegan', value: p => yesNo(p.is_vegan) },
  { label: 'common.vegetarian', value: p => yesNo(p.is_vegetarian) },
  { label: 'common.glutenFree', value: p => yesNo(p.is_gluten_free) },
  { label: 'product.allergens', value: p => (p.allergens || []).map(a => a.name).join(', ') || t('compare.noneListed') },
  { label: 'compare.energy', value: nutrient('calories', 'kcal') },
  { label: 'product.protein', value: nutrient('proteins', 'g') },
  { label: 'product.carbs', value: nutrient('carbohydrates', 'g') },
  { label: 'product.fat', value: nutrient('fats', 'g') },
  { label: 'product.fibre', value: nutrient('fiber', 'g') }
]

function remove(id) {
  compareStore.removeItem(id)
  products.value = products.value.filter(p => p.id !== id)
}

function clearAll() {
  compareStore.clearCompare()
  products.value = []
}

onMounted(async () => {
  compareStore.fetchItems()
  await load(compareStore.items)
  missingIds.value.forEach(id => compareStore.removeItem(id))
})
</script>

<style scoped>
.compare-table th,
.compare-table td {
  padding: 0.75rem 1rem 0.75rem 0;
  border-color: rgba(255, 255, 255, 0.08);
  background: transparent;
}

.compare-table tbody tr {
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}
</style>
