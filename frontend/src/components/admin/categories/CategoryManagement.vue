<template>
  <div class="space-y-6">
    <div class="flex flex-wrap items-center justify-between gap-4">
      <p class="text-sm text-gray-600">Hidden categories and their products are not shown in the shop.</p>
      <button type="button" class="px-4 py-2 text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700" @click="edit()">
        Add category
      </button>
    </div>

    <p v-if="error" class="rounded-md bg-red-50 p-3 text-sm text-red-700" role="alert">{{ error }}</p>

    <!-- Form -->
    <form v-if="form" class="bg-white rounded-lg shadow p-6 grid sm:grid-cols-2 gap-4 text-gray-800" @submit.prevent="save">
      <h2 class="sm:col-span-2 text-lg font-semibold text-gray-900">{{ form.id ? 'Edit category' : 'New category' }}</h2>
      <div>
        <label for="cat-name" class="block text-sm font-medium text-gray-700">Name</label>
        <input id="cat-name" v-model.trim="form.name" required maxlength="100"
               class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm sm:text-sm text-gray-900 bg-white" />
        <p v-if="fieldErrors.name" class="mt-1 text-sm text-red-600">{{ fieldErrors.name }}</p>
      </div>
      <div>
        <label for="cat-order" class="block text-sm font-medium text-gray-700">Position</label>
        <input id="cat-order" v-model.number="form.order" type="number" min="0"
               class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm sm:text-sm text-gray-900 bg-white" />
        <p class="mt-1 text-xs text-gray-500">Lower numbers are listed first.</p>
      </div>
      <div class="sm:col-span-2">
        <label for="cat-description" class="block text-sm font-medium text-gray-700">Description</label>
        <textarea id="cat-description" v-model.trim="form.description" rows="2"
                  class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm sm:text-sm text-gray-900 bg-white"></textarea>
      </div>
      <label class="flex items-center gap-2 text-sm text-gray-700">
        <input v-model="form.is_active" type="checkbox" class="rounded border-gray-300 text-indigo-600" />
        Show in the shop
      </label>
      <div class="sm:col-span-2 flex gap-3">
        <button type="submit" class="px-4 py-2 text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700" :disabled="saving">
          {{ saving ? 'Saving…' : 'Save category' }}
        </button>
        <button type="button" class="px-4 py-2 text-sm font-medium rounded-md text-gray-700 bg-gray-100 hover:bg-gray-200" @click="form = null">Cancel</button>
      </div>
    </form>

    <!-- List -->
    <div class="bg-white rounded-lg shadow overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200 admin-table">
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
        <tbody class="divide-y divide-gray-200">
          <tr v-if="loading"><td colspan="6" class="text-center text-gray-500">Loading categories…</td></tr>
          <tr v-for="category in categories" v-else :key="category.id">
            <td class="font-medium text-gray-900">
              {{ category.name }}
              <span v-if="category.description" class="block text-xs font-normal text-gray-500 truncate max-w-xs">{{ category.description }}</span>
            </td>
            <td>
              <router-link :to="{ name: 'category', params: { category: category.slug } }" class="text-indigo-600 hover:underline">
                /categories/{{ category.slug }}
              </router-link>
            </td>
            <td class="text-right tabular-nums">{{ category.product_count }}</td>
            <td>
              <span class="px-2 py-1 text-xs font-medium rounded-full" :class="category.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'">
                {{ category.is_active ? 'Visible' : 'Hidden' }}
              </span>
            </td>
            <td class="text-right tabular-nums">{{ category.order }}</td>
            <td class="text-right space-x-3">
              <template v-if="confirmDeleteId === category.id">
                <button type="button" class="text-red-600 hover:text-red-800 bg-transparent font-medium" @click="remove(category)">Delete</button>
                <button type="button" class="text-gray-600 hover:text-gray-800 bg-transparent" @click="confirmDeleteId = null">Keep</button>
              </template>
              <template v-else>
                <button type="button" class="text-indigo-600 hover:text-indigo-900 bg-transparent font-medium" @click="edit(category)">Edit</button>
                <button type="button" class="text-gray-600 hover:text-gray-900 bg-transparent" @click="toggleVisible(category)">
                  {{ category.is_active ? 'Hide' : 'Show' }}
                </button>
                <button type="button" class="text-red-600 hover:text-red-800 bg-transparent" @click="confirmDeleteId = category.id">Delete</button>
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
  background: white;
}

.admin-table th {
  @apply px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-600 bg-gray-50;
  border-color: #e5e7eb;
}

.admin-table td {
  @apply px-4 py-3 text-sm text-gray-700;
  background: white;
  border-color: #e5e7eb;
}
</style>
