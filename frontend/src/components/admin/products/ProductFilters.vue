<template>
  <div class="flex flex-wrap gap-4 items-center">
    <div class="w-48">
      <label class="block text-sm font-medium text-cream/80 mb-1">{{ $t('admin.fields.category') }}</label>
      <select
        v-model="filters.category"
        class="block w-full ps-3 pe-10 py-2 text-base border-cream/15 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
      >
        <option value="">{{ $t('admin.filters.allCategories') }}</option>
        <option v-for="category in categories" :key="category.id" :value="category.id">
          {{ categoryName(category) }}
        </option>
      </select>
    </div>

    <div class="w-48">
      <label class="block text-sm font-medium text-cream/80 mb-1">{{ $t('admin.fields.status') }}</label>
      <select
        v-model="filters.status"
        class="block w-full ps-3 pe-10 py-2 text-base border-cream/15 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
      >
        <option value="">{{ $t('admin.filters.allStatuses') }}</option>
        <option value="active">{{ $t('admin.productStatus.active') }}</option>
        <option value="draft">{{ $t('admin.productStatus.draft') }}</option>
        <option value="discontinued">{{ $t('admin.productStatus.discontinued') }}</option>
      </select>
    </div>

    <div class="w-48">
      <label class="block text-sm font-medium text-cream/80 mb-1">{{ $t('admin.filters.priceRange') }}</label>
      <div class="flex gap-2">
        <input
          v-model.number="filters.priceMin"
          type="number"
          :placeholder="$t('admin.filters.min')"
          class="block w-full px-3 py-2 text-base border-cream/15 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
        />
        <input
          v-model.number="filters.priceMax"
          type="number"
          :placeholder="$t('admin.filters.max')"
          class="block w-full px-3 py-2 text-base border-cream/15 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
        />
      </div>
    </div>

    <div class="w-48">
      <label class="block text-sm font-medium text-cream/80 mb-1">{{ $t('admin.filters.stockStatus') }}</label>
      <select
        v-model="filters.stockStatus"
        class="block w-full ps-3 pe-10 py-2 text-base border-cream/15 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
      >
        <option value="">{{ $t('admin.filters.all') }}</option>
        <option value="in_stock">{{ $t('admin.filters.inStock') }}</option>
        <option value="low_stock">{{ $t('admin.filters.lowStock') }}</option>
        <option value="out_of_stock">{{ $t('admin.filters.outOfStock') }}</option>
      </select>
    </div>

    <div class="flex items-end space-x-2 rtl:space-x-reverse">
      <button
        @click="applyFilters"
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-full shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      >
        {{ $t('admin.filters.apply') }}
      </button>
      <button
        @click="resetFilters"
        class="admin-panel inline-flex items-center px-4 py-2 border border-cream/15 text-sm font-medium text-cream/80 hover:bg-cream/[0.03] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      >
        {{ $t('admin.filters.reset') }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useProductStore } from '@/stores/productStore'
import { categoryName } from '@/i18n/catalog'

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
</script>
