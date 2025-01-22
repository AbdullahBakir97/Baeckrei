`<template>
  <div class="overflow-x-auto">
    <div class="flex items-center justify-between mb-4 px-6 pt-6">
      <div class="flex items-center space-x-4">
        <div class="relative">
          <input
            type="text"
            v-model="searchQuery"
            placeholder="Search..."
            class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
          />
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <i class="fas fa-search text-gray-400"></i>
          </div>
        </div>
        <slot name="filters"></slot>
      </div>
      <slot name="actions"></slot>
    </div>

    <div class="min-w-full divide-y divide-gray-200">
      <div class="bg-gray-50">
        <div class="grid" :style="{ gridTemplateColumns: gridColumns }">
          <div
            v-for="column in columns"
            :key="column.key"
            class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:text-gray-700"
            @click="sort(column.key)"
          >
            {{ column.label }}
            <span v-if="sortKey === column.key" class="ml-1">
              {{ sortOrder === 'asc' ? '↑' : '↓' }}
            </span>
          </div>
          <div v-if="hasActions" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
            Actions
          </div>
        </div>
      </div>

      <div class="bg-white divide-y divide-gray-200">
        <div
          v-for="item in sortedItems"
          :key="item.id"
          class="grid hover:bg-gray-50"
          :style="{ gridTemplateColumns: gridColumns }"
        >
          <div
            v-for="column in columns"
            :key="column.key"
            class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
          >
            <slot :name="column.key" :item="item">
              {{ item[column.key] }}
            </slot>
          </div>
          <div v-if="hasActions" class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
            <slot name="actions" :item="item"></slot>
          </div>
        </div>
      </div>
    </div>

    <div class="px-6 py-4 flex items-center justify-between border-t border-gray-200">
      <div class="flex items-center">
        <select
          v-model="pageSize"
          class="mr-2 border-gray-300 rounded-md text-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
        >
          <option v-for="size in pageSizes" :key="size" :value="size">
            {{ size }} per page
          </option>
        </select>
      </div>
      <div class="flex items-center space-x-2">
        <button
          :disabled="currentPage === 1"
          @click="currentPage--"
          class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
        >
          Previous
        </button>
        <span class="text-sm text-gray-700">
          Page {{ currentPage }} of {{ totalPages }}
        </span>
        <button
          :disabled="currentPage === totalPages"
          @click="currentPage++"
          class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
        >
          Next
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  items: {
    type: Array,
    required: true
  },
  columns: {
    type: Array,
    required: true
  },
  hasActions: {
    type: Boolean,
    default: true
  },
  totalItems: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['update:page', 'update:pageSize', 'update:sort', 'search'])

const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const sortKey = ref('')
const sortOrder = ref('asc')
const pageSizes = [10, 25, 50, 100]

const gridColumns = computed(() => {
  const baseColumns = props.columns.length
  const actionColumn = props.hasActions ? 1 : 0
  return `repeat(${baseColumns + actionColumn}, minmax(0, 1fr))`
})

const totalPages = computed(() => Math.ceil(props.totalItems / pageSize.value))

const sortedItems = computed(() => {
  if (!sortKey.value) return props.items

  return [...props.items].sort((a, b) => {
    const aVal = a[sortKey.value]
    const bVal = b[sortKey.value]
    
    if (sortOrder.value === 'asc') {
      return aVal > bVal ? 1 : -1
    }
    return aVal < bVal ? 1 : -1
  })
})

const sort = (key) => {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortOrder.value = 'asc'
  }
  emit('update:sort', { key: sortKey.value, order: sortOrder.value })
}

watch(searchQuery, (newVal) => {
  emit('search', newVal)
})

watch(currentPage, (newVal) => {
  emit('update:page', newVal)
})

watch(pageSize, (newVal) => {
  emit('update:pageSize', newVal)
  currentPage.value = 1
})
</script>`
