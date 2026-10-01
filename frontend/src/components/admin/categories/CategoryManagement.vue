<template>
  <div class="space-y-6">
    <div class="flex flex-wrap items-center justify-between gap-4">
      <p class="text-sm text-cream-muted">Hidden categories and their products are not shown in the shop.</p>
      <button type="button" class="px-4 py-2 text-sm font-medium rounded-full text-oven-950 bg-crust hover:bg-crust-light" @click="edit()">
        Add category
      </button>
    </div>

    <p v-if="error" class="rounded-md bg-red-400/10 p-3 text-sm text-red-300" role="alert">{{ error }}</p>

    <!-- Form -->
    <form v-if="form" class="admin-panel p-6 grid sm:grid-cols-2 gap-4 text-cream" @submit.prevent="save">
      <h2 class="sm:col-span-2 text-lg font-semibold text-cream">{{ form.id ? 'Edit category' : 'New category' }}</h2>
      <div>
        <label for="cat-name" class="block text-sm font-medium text-cream/80">Name</label>
        <input id="cat-name" v-model.trim="form.name" required maxlength="100"
               class="mt-1 block w-full rounded-md border border-cream/15 px-3 py-2 shadow-sm sm:text-sm text-cream bg-oven-800" />
        <p v-if="fieldErrors.name" class="mt-1 text-sm text-red-300">{{ fieldErrors.name }}</p>
      </div>
      <div>
        <label for="cat-order" class="block text-sm font-medium text-cream/80">Position</label>
        <input id="cat-order" v-model.number="form.order" type="number" min="0"
               class="mt-1 block w-full rounded-md border border-cream/15 px-3 py-2 shadow-sm sm:text-sm text-cream bg-oven-800" />
        <p class="mt-1 text-xs text-cream-muted">Lower numbers are listed first.</p>
      </div>
      <div class="sm:col-span-2">
        <label for="cat-description" class="block text-sm font-medium text-cream/80">Description</label>
        <textarea id="cat-description" v-model.trim="form.description" rows="2"
                  class="mt-1 block w-full rounded-md border border-cream/15 px-3 py-2 shadow-sm sm:text-sm text-cream bg-oven-800"></textarea>
      </div>
      <label class="flex items-center gap-2 text-sm text-cream/80">
        <input v-model="form.is_active" type="checkbox" class="rounded border-cream/15 text-crust" />
        Show in the shop
      </label>
      <div class="sm:col-span-2 flex gap-3">
        <button type="submit" class="px-4 py-2 text-sm font-medium rounded-full text-oven-950 bg-crust hover:bg-crust-light" :disabled="saving">
          {{ saving ? 'Saving…' : 'Save category' }}
        </button>
        <button type="button" class="px-4 py-2 text-sm font-medium rounded-full text-cream/80 bg-cream/[0.05] hover:bg-cream/10" @click="form = null">Cancel</button>
      </div>
    </form>

    <!-- List -->
    <div class="admin-panel overflow-x-auto">
      <table class="min-w-full divide-y divide-cream/10 admin-table">
        <thead>
          <tr>
            <th scope="col">Name</th>
            <th scope="col">Shop link</th>
            <th scope="col" class="text-right">Products</th>
            <th scope="col">Visible</th>
            <th scope="col" class="text-right">Position</th>
            <th scope="col"><span class="sr-only">Actions</span></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-cream/10">
          <tr v-if="loading"><td colspan="6" class="text-center text-cream-muted">Loading categories…</td></tr>
          <tr v-for="category in categories" v-else :key="category.id">
            <td class="font-medium text-cream">
              {{ category.name }}
              <span v-if="category.description" class="block text-xs font-normal text-cream-muted truncate max-w-xs">{{ category.description }}</span>
            </td>
            <td>
              <router-link :to="{ name: 'category', params: { category: category.slug } }" class="text-crust hover:underline">
                /categories/{{ category.slug }}
              </router-link>
            </td>
            <td class="text-right tabular-nums">{{ category.product_count }}</td>
            <td>
              <span class="px-2 py-1 text-xs font-medium rounded-full" :class="category.is_active ? 'bg-emerald-400/10 text-emerald-300' : 'bg-cream/[0.05] text-cream-muted'">
                {{ category.is_active ? 'Visible' : 'Hidden' }}
              </span>
            </td>
            <td class="text-right tabular-nums">{{ category.order }}</td>
            <td class="text-right space-x-3">
              <template v-if="confirmDeleteId === category.id">
                <button type="button" class="text-red-300 hover:text-red-300 bg-transparent font-medium" @click="remove(category)">Delete</button>
                <button type="button" class="text-cream-muted hover:text-cream bg-transparent" @click="confirmDeleteId = null">Keep</button>
              </template>
              <template v-else>
                <button type="button" class="text-crust hover:text-crust-light bg-transparent font-medium" @click="edit(category)">Edit</button>
                <button type="button" class="text-cream-muted hover:text-cream bg-transparent" @click="toggleVisible(category)">
                  {{ category.is_active ? 'Hide' : 'Show' }}
                </button>
                <button type="button" class="text-red-300 hover:text-red-300 bg-transparent" @click="confirmDeleteId = category.id">Delete</button>
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import axios from '@/plugins/axios'
import { useProductStore } from '@/stores/productStore'

const API = '/api/products/'
const productStore = useProductStore()
const categories = ref([])
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const form = ref(null)
const fieldErrors = reactive({})
const confirmDeleteId = ref(null)

async function load() {
  loading.value = true
  try {
    const response = await axios.get(`${API}categories/`, { params: { include_inactive: 'true' } })
    categories.value = response.data.results || []
  } catch (err) {
    error.value = 'Categories could not be loaded.'
  } finally {
    loading.value = false
  }
}

// The shop's footer and filters read categories from the product store.
const refreshShop = () => productStore.fetchCategories()

function edit(category) {
  Object.keys(fieldErrors).forEach(k => delete fieldErrors[k])
  form.value = category
    ? { id: category.id, name: category.name, description: category.description, order: category.order, is_active: category.is_active }
    : { name: '', description: '', order: 0, is_active: true }
}

async function save() {
  saving.value = true
  error.value = ''
  Object.keys(fieldErrors).forEach(k => delete fieldErrors[k])
  const { id, ...payload } = form.value
  try {
    if (id) await axios.patch(`${API}${id}/update_category/`, payload)
    else await axios.post(`${API}create_category/`, payload)
    form.value = null
    await load()
    refreshShop()
  } catch (err) {
    const data = err.response?.data || {}
    for (const [key, value] of Object.entries(data)) fieldErrors[key] = [].concat(value)[0]
    if (!Object.keys(fieldErrors).length) error.value = 'The category could not be saved.'
  } finally {
    saving.value = false
  }
}

async function toggleVisible(category) {
  try {
    await axios.patch(`${API}${category.id}/update_category/`, { is_active: !category.is_active })
    category.is_active = !category.is_active
    refreshShop()
  } catch (err) {
    error.value = 'The category could not be updated.'
  }
}

async function remove(category) {
  error.value = ''
  try {
    await axios.delete(`${API}${category.id}/delete_category/`)
    categories.value = categories.value.filter(c => c.id !== category.id)
    refreshShop()
  } catch (err) {
    error.value = err.response?.data?.detail || 'The category could not be deleted.'
  } finally {
    confirmDeleteId.value = null
  }
}

onMounted(load)
</script>

<style scoped>
.admin-table {
  background: transparent;
}

.admin-table th {
  @apply px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-cream-muted bg-cream/[0.03];
  border-color: rgba(244, 236, 225, 0.08);
}

.admin-table td {
  @apply px-4 py-3 text-sm text-cream/80;
  background: transparent;
  border-color: rgba(244, 236, 225, 0.08);
}
</style>
