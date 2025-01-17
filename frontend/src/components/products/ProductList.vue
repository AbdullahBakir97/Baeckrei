<template>
  <div class="container py-8">
    <!-- Header Section -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
      <h1 class="text-2xl sm:text-3xl font-bold text-gray-200">Our Products</h1>
      
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-4 gap-8">
      <!-- Filters Sidebar -->
      <div class="lg:col-span-1">
        <div class="bg-[rgba(255,255,255,0.02)] backdrop-blur-[8px] border border-white/5 
                    hover:border-white/20 hover:shadow-red-500/10 transition-all duration-300
                    rounded-lg p-6 space-y-6">
          <div class="sticky top-4">
            <div class="glass-panel p-6 space-y-6 rounded-lg">
              <!-- Category Filter -->
              <div>
                <h3 class="text-gray-200 font-semibold mb-3">Categories</h3>
                <div v-if="productStore.categoriesLoading" class="flex justify-center py-4">
                  <font-awesome-icon icon="spinner" class="animate-spin text-amber-500" />
                </div>
                <div v-else-if="categories?.length > 0" class="space-y-2">
                  <label
                    v-for="category in categories"
                    :key="category?.id"
                    class="flex items-center gap-2 cursor-pointer filter-item"
                  >
                    <input
                      type="checkbox"
                      :value="category?.id"
                      v-model="selectedCategories"
                      class="form-checkbox rounded text-red-500 focus:ring-red-500 bg-gray-800 border-gray-700"
                    >
                    <span class="text-gray-300">{{ category?.name }}</span>
                  </label>
                </div>
                <div v-else class="text-gray-400 text-sm py-2">
                  No categories available
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
        </div>
      </div>

      <!-- Product Grid -->
      <div class="lg:col-span-3">
        <div class="bg-[rgba(255,255,255,0.02)] backdrop-blur-[8px] border border-white/5 rounded-lg p-6">
          <!-- View Toggle and Sort -->
          <div class="flex flex-wrap items-center justify-between gap-4 mb-8">
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
              class="search-input min-w-[160px] rounded-lg bg-[rgba(255,255,255,0.03)] backdrop-blur-sm 
                     border border-white/5 text-white px-4 py-2
                     focus:border-red-500/30 focus:ring-1 focus:ring-red-500/30"
              @change="handleSort"
            >
              <option value="name">Name</option>
              <option value="price_asc">Price: Low to High</option>
              <option value="price_desc">Price: High to Low</option>
              <option value="popularity">Popularity</option>
            </select>
          </div>

          <!-- Loading State -->
          <div v-if="productStore.loading" class="flex justify-center items-center p-8">
            <font-awesome-icon icon="spinner" spin class="text-4xl text-gray-400" />
          </div>

          <!-- Products Grid/List View -->
          <template v-else>
            <div class="products-container" ref="container" @mousemove="handleMouseMove">
              <div v-if="!productStore.error && productStore.products && productStore.products.length > 0" 
                :class="[viewMode === 'grid' ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6' : 'space-y-4']"
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

              <div v-else class="card p-8 text-center">
                <template v-if="productStore.error">
                  <p class="text-red-600">{{ productStore.error }}</p>
                </template>
                <template v-else>
                  <font-awesome-icon icon="fa-solid fa-box-open" class="text-4xl text-gray-400 mb-4" />
                  <h3 class="text-lg font-semibold text-gray-900 mb-2">No Products Found</h3>
                  <p class="text-gray-600">Try adjusting your filters or search criteria</p>
                </template>
              </div>

              <!-- Pagination -->
              <div v-if="productStore.products && productStore.products.length > 0" class="mt-8 flex justify-center gap-4">
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
          </template>
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

// Categories from store
const categories = computed(() => productStore.categories)

// Mouse tracking for gradient effect
const container = ref(null)

const handleMouseMove = (e) => {
  if (container.value) {
    const rect = container.value.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    container.value.style.setProperty('--mouse-x', `${x}px`)
    container.value.style.setProperty('--mouse-y', `${y}px`)
  }
}

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
      isVegan: filters.value.dietary.isVegan,
      isVegetarian: filters.value.dietary.isVegetarian,
      isGlutenFree: filters.value.dietary.isGlutenFree
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
onMounted(async () => {
  try {
    await productStore.fetchCategories()
    loadProducts()
  } catch (error) {
    console.error('Error initializing product list:', error)
  }
})
</script>

<style scoped>
.container {
  position: relative;
  z-index: 1;
}

.glass-panel {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.product-container {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  border-radius: 1rem;
  padding: 2rem;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 2rem;
  padding: 1rem;
}

.search-input {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
  padding: 0.5rem 1rem;
}

.search-input option {
  background: rgba(45, 45, 45, 0.95);
  color: #fff;
}

.active-view {
  background: rgba(239, 68, 68, 0.2);
  color: rgb(239, 68, 68);
}

.product-list-enter-active,
.product-list-leave-active {
  transition: all 0.3s ease;
}

.product-list-enter-from,
.product-list-leave-to {
  opacity: 0;
  transform: translateY(30px);
}

@supports not (backdrop-filter: blur(10px)) {
  .glass-panel,
  .product-container,
  .search-input {
    background: rgba(23, 23, 23, 0.95);
    border-color: rgba(255, 255, 255, 0.1);
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>