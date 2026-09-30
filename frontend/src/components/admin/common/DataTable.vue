<template>
  <div class="overflow-x-auto">
    <div class="flex items-center justify-between mb-4 px-6 pt-6">
      <div class="flex items-center space-x-4">
        <div class="relative">
          <input
            type="text"
            v-model="searchQuery"
            placeholder="Search..."
            class="block w-full pl-10 pr-3 py-2 border border-cream/15 rounded-md leading-5 bg-oven-800 placeholder-gray-500 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
          />
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <font-awesome-icon icon="search" class="text-cream-faint" />
          </div>
        </div>
        <slot name="filters"></slot>
      </div>
      <slot name="toolbar"></slot>
    </div>

    <div class="min-w-full divide-y divide-cream/10">
      <div class="bg-cream/[0.03]">
        <div class="grid" :style="{ gridTemplateColumns: gridColumns }">
          <div
            v-for="column in columns"
            :key="column.key"
            class="px-6 py-3 text-left text-xs font-medium text-cream-muted uppercase tracking-wider cursor-pointer hover:text-cream/80"
            @click="sort(column.key)"
          >
            {{ column.label }}
            <span v-if="sortKey === column.key" class="ml-1">
              {{ sortOrder === 'asc' ? '↑' : '↓' }}
            </span>
          </div>
          <div v-if="hasActions" class="px-6 py-3 text-right text-xs font-medium text-cream-muted uppercase tracking-wider">
            Actions
          </div>
        </div>
      </div>

      <div class="bg-oven-800 divide-y divide-cream/10">
        <div
          v-for="item in sortedItems"
          :key="item.id"
          class="grid hover:bg-cream/[0.03]"
          :style="{ gridTemplateColumns: gridColumns }"
        >
          <div
            v-for="column in columns"
            :key="column.key"
            class="px-6 py-4 whitespace-nowrap text-sm text-cream"
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

    <div class="px-6 py-4 flex items-center justify-between border-t border-cream/10">
      <div class="flex items-center">
        <select
          v-model="pageSize"
          class="mr-2 border-cream/15 rounded-md text-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
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
          class="admin-panel relative inline-flex items-center px-4 py-2 border border-cream/15 text-sm font-medium text-cream/80 hover:bg-cream/[0.03] disabled:opacity-50"
        >
          Previous
        </button>
        <span class="text-sm text-cream/80">
          Page {{ currentPage }} of {{ totalPages }}
        </span>
        <button
          :disabled="currentPage === totalPages"
          @click="currentPage++"
          class="admin-panel relative inline-flex items-center px-4 py-2 border border-cream/15 text-sm font-medium text-cream/80 hover:bg-cream/[0.03] disabled:opacity-50"
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

// Wait until typing pauses instead of searching on every keystroke.
let searchTimer = null
watch(searchQuery, (newVal) => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => emit('search', newVal), 300)
})

watch(currentPage, (newVal) => {
  emit('update:page', newVal)
})

watch(pageSize, (newVal) => {
  emit('update:pageSize', newVal)
  currentPage.value = 1
})
</script>`
