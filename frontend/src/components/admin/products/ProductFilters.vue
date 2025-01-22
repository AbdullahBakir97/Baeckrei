`<template>
  <div class="flex flex-wrap gap-4 items-center">
    <div class="w-48">
      <label class="block text-sm font-medium text-gray-700 mb-1">Category</label>
      <select
        v-model="filters.category"
        class="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
      >
        <option value="">All Categories</option>
        <option v-for="category in categories" :key="category.id" :value="category.id">
          {{ category.name }}
        </option>
      </select>
    </div>

    <div class="w-48">
      <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
      <select
        v-model="filters.status"
        class="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
      >
        <option value="">All Status</option>
        <option value="active">Active</option>
        <option value="inactive">Inactive</option>
      </select>
    </div>

    <div class="w-48">
      <label class="block text-sm font-medium text-gray-700 mb-1">Price Range</label>
      <div class="flex gap-2">
        <input
          v-model.number="filters.priceMin"
          type="number"
          placeholder="Min"
          class="block w-full px-3 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
        />
        <input
          v-model.number="filters.priceMax"
          type="number"
          placeholder="Max"
          class="block w-full px-3 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
        />
      </div>
    </div>

    <div class="w-48">
      <label class="block text-sm font-medium text-gray-700 mb-1">Stock Status</label>
      <select
        v-model="filters.stockStatus"
        class="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
      >
        <option value="">All</option>
        <option value="in_stock">In Stock</option>
        <option value="low_stock">Low Stock</option>
        <option value="out_of_stock">Out of Stock</option>
      </select>
    </div>

    <div class="flex items-end space-x-2">
      <button
        @click="applyFilters"
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      >
        Apply Filters
      </button>
      <button
        @click="resetFilters"
        class="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      >
        Reset
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useProductStore } from '@/stores/productStore'

const productStore = useProductStore()
const emit = defineEmits(['filter'])

const filters = ref({
  category: '',
  status: '',
  priceMin: null,
  priceMax: null,
  stockStatus: ''
})

const categories = ref([])

const loadCategories = async () => {
  try {
    categories.value = await productStore.fetchCategories()
  } catch (error) {
    console.error('Error loading categories:', error)
  }
}

const applyFilters = () => {
  emit('filter', { ...filters.value })
}

const resetFilters = () => {
  filters.value = {
    category: '',
    status: '',
    priceMin: null,
    priceMax: null,
    stockStatus: ''
  }
  emit('filter', { ...filters.value })
}

// Load categories when component is mounted
loadCategories()
</script>`
