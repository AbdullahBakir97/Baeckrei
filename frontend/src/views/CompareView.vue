<template>
  <div class="min-h-screen py-12 px-4">
    <div class="max-w-6xl mx-auto">
      <PageHeader title="Compare products" subtitle="Price, dietary information, allergens and nutrition side by side" icon="code-compare" />

      <div v-if="loading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-white/20"></div>
      </div>

      <div v-else-if="!products.length" class="glass-panel text-center py-12">
        <p class="text-lg text-white font-medium">Nothing to compare yet</p>
        <p class="mt-2 text-gray-400">Use "Compare" on up to four product pages to see them here.</p>
        <router-link to="/products" class="btn-amber mt-6">Browse products</router-link>
      </div>

      <div v-else class="glass-panel overflow-x-auto">
        <table class="w-full min-w-[40rem] text-left text-gray-300 compare-table">
          <thead>
            <tr>
              <th scope="col" class="w-40"></th>
              <th v-for="product in products" :key="product.id" scope="col" class="align-top">
                <img :src="product.image_url || product.image || PLACEHOLDER_IMAGE" :alt="product.name"
                     class="h-24 w-24 rounded-lg object-contain bg-white/5" @error="applyImageFallback" />
                <router-link :to="{ name: 'product-detail', params: { id: product.id } }"
                             class="mt-2 block font-semibold text-white hover:text-amber-300">{{ product.name }}</router-link>
                <button type="button" class="mt-1 text-sm text-gray-400 hover:text-red-300 bg-transparent" @click="remove(product.id)">Remove</button>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows" :key="row.label">
              <th scope="row" class="text-gray-400 font-medium">{{ row.label }}</th>
              <td v-for="product in products" :key="product.id" class="tabular-nums">{{ row.value(product) }}</td>
            </tr>
          </tbody>
        </table>
        <div class="mt-4">
          <button type="button" class="btn-ghost" @click="clearAll">Clear comparison</button>
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

const compareStore = useCompareStore()
const { products, missingIds, loading, load } = useFreshProducts()

const yesNo = (value) => (value ? 'Yes' : 'No')
const nutrient = (key, unit) => (product) => {
  const value = product.nutrition_info?.[key]
  return value != null ? `${Number(value).toFixed(1)} ${unit}` : '—'
}

const rows = [
  { label: 'Price', value: p => `${Number(p.price).toFixed(2)} €` },
  { label: 'Category', value: p => p.category?.name || '—' },
  { label: 'In stock', value: p => (p.available && p.stock > 0 ? 'Yes' : 'No') },
  { label: 'Vegan', value: p => yesNo(p.is_vegan) },
  { label: 'Vegetarian', value: p => yesNo(p.is_vegetarian) },
  { label: 'Gluten free', value: p => yesNo(p.is_gluten_free) },
  { label: 'Allergens', value: p => (p.allergens || []).map(a => a.name).join(', ') || 'None listed' },
  { label: 'Energy (per 100 g)', value: nutrient('calories', 'kcal') },
  { label: 'Protein', value: nutrient('proteins', 'g') },
  { label: 'Carbohydrates', value: nutrient('carbohydrates', 'g') },
  { label: 'Fat', value: nutrient('fats', 'g') },
  { label: 'Fibre', value: nutrient('fiber', 'g') }
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
