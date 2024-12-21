<template>
  <div class="container py-8">
    <!-- Header Section -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
      <h1 class="text-2xl sm:text-3xl font-bold text-gray-200">Our Products</h1>
      <div class="flex flex-wrap items-center gap-4">
        <!-- View Toggle -->
        <div class="flex items-center glass-panel rounded-lg p-1">
          <button
            @click="viewMode = 'grid'"
            class="p-2 rounded-md transition-all duration-300"
            :class="viewMode === 'grid' ? 'active-view' : 'hover:bg-opacity-20 hover:bg-red-500'"
          >
            <font-awesome-icon icon="fa-solid fa-th-large" class="text-lg" />
          </button>
          <button
            @click="viewMode = 'list'"
            class="p-2 rounded-md transition-all duration-300"
            :class="viewMode === 'list' ? 'active-view' : 'hover:bg-opacity-20 hover:bg-red-500'"
          >
            <font-awesome-icon icon="fa-solid fa-list" class="text-lg" />
          </button>
        </div>
        <!-- Sort Dropdown -->
        <select
          v-model="sortBy"
          class="search-input min-w-[160px] rounded-lg"
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
          <div class="glass-panel p-6 space-y-6 rounded-lg">
            <!-- Category Filter -->
            <div>
              <h3 class="text-gray-200 font-semibold mb-3">Categories</h3>
              <div class="space-y-2">
                <label
                  v-for="category in categories"
                  :key="category.id"
                  class="flex items-center gap-2 cursor-pointer filter-item"
                >
                  <input
                    type="checkbox"
                    :value="category.id"
                    v-model="selectedCategories"
                    class="form-checkbox rounded text-red-500 focus:ring-red-500 bg-gray-800 border-gray-700"
                  >
                  <span class="text-gray-300">{{ category.name }}</span>
                </label>
              </div>
            </div>

            <!-- Price Range Filter -->
            <div>
              <h3 class="text-gray-200 font-semibold mb-3">Price Range</h3>
              <div class="space-y-4">
                <div class="flex gap-4">
                  <div class="flex-1">
                    <input
                      type="number"
                      v-model="priceRange[0]"
                      placeholder="Min"
                      class="search-input w-full rounded-lg"
                    >
                  </div>
                  <div class="flex-1">
                    <input
                      type="number"
                      v-model="priceRange[1]"
                      placeholder="Max"
                      class="search-input w-full rounded-lg"
                    >
                  </div>
                </div>
              </div>
            </div>

            <!-- Dietary Preferences -->
            <div>
              <h3 class="text-gray-200 font-semibold mb-3">Dietary Preferences</h3>
              <div class="space-y-2">
                <label class="flex items-center gap-2 cursor-pointer filter-item">
                  <input
                    type="checkbox"
                    v-model="filters.dietary.isVegan"
                    class="form-checkbox rounded text-red-500 focus:ring-red-500 bg-gray-800 border-gray-700"
                  >
                  <span class="text-gray-300">Vegan</span>
                </label>
                <label class="flex items-center gap-2 cursor-pointer filter-item">
                  <input
                    type="checkbox"
                    v-model="filters.dietary.isVegetarian"
                    class="form-checkbox rounded text-red-500 focus:ring-red-500 bg-gray-800 border-gray-700"
                  >
                  <span class="text-gray-300">Vegetarian</span>
                </label>
                <label class="flex items-center gap-2 cursor-pointer filter-item">
                  <input
                    type="checkbox"
                    v-model="filters.dietary.isGlutenFree"
                    class="form-checkbox rounded text-red-500 focus:ring-red-500 bg-gray-800 border-gray-700"
                  >
                  <span class="text-gray-300">Gluten Free</span>
                </label>
              </div>
            </div>

            <!-- Clear Filters Button -->
            <button
              @click="clearFilters"
              class="w-full px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 
                     transition duration-200 focus:outline-none focus:ring-2 focus:ring-red-500"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </aside>

      <!-- Products Grid -->
      <div class="flex-grow">
        <!-- Loading State -->
        <div v-if="productStore.loading" class="grid place-items-center h-96">
          <div class="animate-spin rounded-full h-32 w-32 border-b-2 border-red-500"></div>
        </div>

        <!-- Products Grid/List View -->
        <div v-else-if="!productStore.error && productStore.products && productStore.products.length > 0" 
          :class="[
            viewMode === 'grid' ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6' : 'space-y-4'
          ]"
        >
          <template v-if="viewMode === 'grid'">
            <ProductCard 
              v-for="product in productStore.products"
              :key="product.id"
              :product="product"
              cardColor="#313131"
              stripColor="#35AFFB"
              buttonColor="#35AFFB"
              textColor="#ffffff"
              @add-to-cart="addToCart"
            />
          </template>
          <template v-else>
            <ProductListItem 
              v-for="product in productStore.products"
              :key="product.id"
              :product="product"
              @add-to-cart="addToCart"
            />
          </template>
        </div>

        <!-- Empty State -->
        <div 
          v-else-if="!productStore.loading && !productStore.error && (!productStore.products || productStore.products.length === 0)" 
          class="card p-8 text-center"
        >
          <font-awesome-icon icon="fa-solid fa-box-open" class="text-4xl text-gray-400 mb-4" />
          <h3 class="text-lg font-semibold text-gray-900 mb-2">No Products Found</h3>
          <p class="text-gray-600">Try adjusting your filters or search criteria</p>
        </div>

        <!-- Error State -->
        <div v-else-if="productStore.error" class="card p-8 text-center text-red-600">
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
import ProductListItem from './ProductListItem.vue'
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { 
  faThLarge,
  faList,
  faBoxOpen
} from '@fortawesome/free-solid-svg-icons'

library.add(faThLarge, faList, faBoxOpen)

const productStore = useProductStore()
const route = useRoute()

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
  { id: 'breads', name: 'Breads' },
  { id: 'pastries', name: 'Pastries' },
  { id: 'cakes', name: 'Cakes' },
  { id: 'cookies', name: 'Cookies' }
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

const addToCart = async (product) => {
  try {
    // TODO: Implement cart functionality
    console.log('Add to cart:', product)
  } catch (error) {
    console.error('Error adding to cart:', error)
  }
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

watch(() => route.params.category, (newCategory) => {
  if (newCategory) {
    filters.value.category = newCategory
    loadProducts()
  }
})

// Lifecycle
onMounted(() => {
  loadProducts()
})
</script>

<style scoped>
.glass-panel {
  background: linear-gradient(
    to bottom,
    rgba(17, 17, 17, 0.95) 0%,
    rgba(17, 17, 17, 0.85) 100%
  );
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 107, 107, 0.1);
  box-shadow: 
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06),
    0 0 20px rgba(255, 107, 107, 0.1);
}

.search-input {
  @apply relative px-4 py-2 text-gray-100 
         transition-all duration-300;
  background: rgba(23, 23, 23, 0.7);
  border: 1px solid rgba(255, 107, 107, 0.2);
  backdrop-filter: blur(4px);
}

.search-input:focus {
  @apply outline-none;
  background: rgba(23, 23, 23, 0.9);
  border-color: rgba(255, 107, 107, 0.4);
  box-shadow: 
    0 0 0 2px rgba(255, 107, 107, 0.1),
    0 0 20px rgba(255, 107, 107, 0.2);
}

.active-view {
  @apply bg-red-500 bg-opacity-20 text-red-400;
  box-shadow: 0 0 10px rgba(255, 107, 107, 0.2);
}

.filter-item {
  @apply transition-all duration-300;
}

.filter-item:hover span {
  @apply text-gray-100;
}

/* Custom checkbox styles */
.form-checkbox {
  @apply rounded transition-all duration-300;
  border: 1px solid rgba(255, 107, 107, 0.2);
}

.form-checkbox:checked {
  background-color: rgba(255, 107, 107, 0.8);
  border-color: rgba(255, 107, 107, 0.4);
}

.form-checkbox:focus {
  box-shadow: 0 0 0 2px rgba(255, 107, 107, 0.2);
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