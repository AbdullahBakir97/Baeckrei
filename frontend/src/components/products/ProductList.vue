<template>
  <div class="container py-8">
    <!-- Header Section -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
      <h1 class="text-2xl sm:text-3xl font-bold text-gray-900">Our Products</h1>
      <div class="flex flex-wrap items-center gap-4">
        <!-- View Toggle -->
        <div class="flex items-center bg-white rounded-lg border border-gray-200 p-1">
          <button
            @click="viewMode = 'grid'"
            class="p-2 rounded-md transition-colors"
            :class="viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'hover:bg-gray-100'"
          >
            <i class="fas fa-grid-2 text-lg"></i>
          </button>
          <button
            @click="viewMode = 'list'"
            class="p-2 rounded-md transition-colors"
            :class="viewMode === 'list' ? 'bg-blue-100 text-blue-600' : 'hover:bg-gray-100'"
          >
            <i class="fas fa-list text-lg"></i>
          </button>
        </div>
        <!-- Sort Dropdown -->
        <select
          v-model="sortBy"
          class="input min-w-[160px]"
          @change="handleSort"
        >
          <option value="name">Name</option>
          <option value="price_asc">Price: Low to High</option>
          <option value="price_desc">Price: High to Low</option>
          <option value="newest">Newest</option>
        </select>
      </div>
    </div>

    <!-- Filters and Products Grid -->
    <div class="flex flex-col lg:flex-row gap-8">
      <!-- Filters Sidebar -->
      <aside class="w-full lg:w-64 flex-shrink-0">
        <div class="sticky top-4">
          <div class="card p-6 space-y-6">
            <!-- Category Filter -->
            <div>
              <h3 class="font-semibold mb-3">Categories</h3>
              <div class="space-y-2">
                <label
                  v-for="category in categories"
                  :key="category.id"
                  class="flex items-center gap-2 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    :value="category.id"
                    v-model="selectedCategories"
                    class="checkbox"
                  />
                  <span class="text-gray-700">{{ category.name }}</span>
                </label>
              </div>
            </div>

            <!-- Price Range Filter -->
            <div>
              <h3 class="font-semibold mb-3">Price Range</h3>
              <div class="space-y-4">
                <div class="relative pt-1">
                  <input
                    type="range"
                    v-model="priceRange[1]"
                    min="0"
                    max="1000"
                    step="10"
                    class="w-full appearance-none h-2 bg-gray-200 rounded-full outline-none cursor-pointer"
                  />
                </div>
                <div class="flex justify-between text-sm text-gray-600">
                  <span>${{ priceRange[0] }}</span>
                  <span>${{ priceRange[1] }}</span>
                </div>
              </div>
            </div>

            <!-- Dietary Preferences -->
            <div>
              <h3 class="font-semibold mb-3">Dietary Preferences</h3>
              <div class="space-y-2">
                <label class="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    v-model="filters.dietary.isVegan"
                    class="checkbox"
                  />
                  <span class="text-gray-700">Vegan</span>
                </label>
                <label class="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    v-model="filters.dietary.isVegetarian"
                    class="checkbox"
                  />
                  <span class="text-gray-700">Vegetarian</span>
                </label>
                <label class="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    v-model="filters.dietary.isGlutenFree"
                    class="checkbox"
                  />
                  <span class="text-gray-700">Gluten Free</span>
                </label>
              </div>
            </div>

            <!-- Clear Filters -->
            <button
              @click="clearFilters"
              class="btn btn-secondary w-full"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </aside>

      <!-- Products Grid -->
      <div class="flex-grow">
        <div v-if="productStore.loading" class="grid place-items-center h-96">
          <div class="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
        </div>
        <div 
          v-if="!productStore.loading && !productStore.error && productStore.products && productStore.products.length > 0" 
          class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          <ProductCard
            v-for="product in productStore.products"
            :key="product.id"
            :product="product"
            @add-to-cart="addToCart"
          />
        </div>

        <!-- Empty State -->
        <div 
          v-if="!productStore.loading && !productStore.error && (!productStore.products || productStore.products.length === 0)" 
          class="card p-8 text-center"
        >
          <i class="fas fa-box-open text-4xl text-gray-400 mb-4"></i>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">No Products Found</h3>
          <p class="text-gray-600">Try adjusting your filters or search criteria</p>
        </div>

        <!-- Error State -->
        <div v-if="productStore.error" class="card p-8 text-center text-red-600">
          <p>{{ productStore.error }}</p>
        </div>

        <!-- Pagination -->
        <div v-if="productStore.products.length" class="mt-8 flex justify-center gap-4">
          <button
            @click="previousPage"
            :disabled="!productStore.hasPreviousPage"
            class="btn btn-secondary"
          >
            Previous
          </button>
          <button
            @click="nextPage"
            :disabled="!productStore.hasNextPage"
            class="btn btn-secondary"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useProductStore } from '@/stores/productStore'
import { useRoute } from 'vue-router'
import ProductCard from './ProductCard.vue'

const productStore = useProductStore()
const route = useRoute()

const props = defineProps({
  category: {
    type: String,
    default: ''
  }
})

// State
const viewMode = ref('grid')
const sortBy = ref('name')
const selectedCategories = ref([])
const priceRange = ref([0, 1000])
const filters = ref({
  dietary: {
    isVegan: false,
    isVegetarian: false,
    isGlutenFree: false
  },
  category: ''
})

// Mock categories (replace with API data)
const categories = ref([
  { id: 1, name: 'Breads' },
  { id: 2, name: 'Pastries' },
  { id: 3, name: 'Cakes' },
  { id: 4, name: 'Cookies' }
])

// Computed
const maxPrice = computed(() => {
  if (!productStore.products.length) return 1000
  return Math.max(...productStore.products.map(p => p.price))
})

const totalPages = computed(() => {
  return Math.ceil(productStore.pagination.total / productStore.pagination.pageSize)
})

// Methods
const loadProducts = async () => {
  try {
    await productStore.fetchProducts({
      sort: sortBy.value,
      categories: selectedCategories.value,
      price_min: priceRange.value[0],
      price_max: priceRange.value[1],
      ...filters.value.dietary,
      category: filters.value.category
    })
  } catch (error) {
    console.error('Error loading products:', error)
  }
}

const handleSort = () => {
  loadProducts()
}

const clearFilters = () => {
  selectedCategories.value = []
  priceRange.value = [0, maxPrice.value]
  filters.value.dietary = {
    isVegan: false,
    isVegetarian: false,
    isGlutenFree: false
  }
  filters.value.category = ''
  loadProducts()
}

const addToCart = (product) => {
  // TODO: Implement cart functionality
  console.log('Add to cart:', product)
}

const previousPage = () => {
  if (productStore.hasPreviousPage) {
    productStore.setPage(productStore.pagination.page - 1)
    loadProducts()
  }
}

const nextPage = () => {
  if (productStore.hasNextPage) {
    productStore.setPage(productStore.pagination.page + 1)
    loadProducts()
  }
}

// Watchers
watch([selectedCategories, priceRange, filters], () => {
  productStore.setPage(1) // Reset to first page when filters change
  loadProducts()
}, { deep: true })

watch(() => props.category, (newCategory) => {
  if (newCategory) {
    filters.value.category = newCategory;
    loadProducts();
  }
});

watch(() => route.params.category, (newCategory) => {
  if (newCategory) {
    filters.value.category = newCategory;
    loadProducts();
  }
});

// Lifecycle
onMounted(() => {
  loadProducts()
})
</script>

<style scoped>
/* Custom range input styling */
input[type="range"] {
  @apply appearance-none bg-gray-200 h-2 rounded-full;
}

input[type="range"]::-webkit-slider-thumb {
  @apply appearance-none w-4 h-4 rounded-full bg-blue-600 cursor-pointer;
}

input[type="range"]::-moz-range-thumb {
  @apply w-4 h-4 rounded-full bg-blue-600 cursor-pointer border-none;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>