<template>
  <div class="space-y-8">
    <!-- Loading State -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-32">
      <div class="relative w-20 h-20">
        <div class="absolute inset-0 rounded-full border-t-2 border-red-500/30 animate-spin"></div>
        <div class="absolute inset-[4px] rounded-full border-t-2 border-red-500/50 animate-spin-slow"></div>
        <div class="absolute inset-[8px] rounded-full border-t-2 border-red-500/70 animate-spin-slower"></div>
      </div>
      <p class="mt-4 text-cream-faint">Loading product details...</p>
    </div>

    <div v-else-if="loadError" class="rounded-lg bg-red-400/10 p-6 text-red-300" role="alert">
      {{ loadError }}
      <router-link to="/admin/products" class="ml-2 underline">Back to products</router-link>
    </div>

    <template v-else>
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-cream">{{ product.name }}</h1>
          <p class="mt-1 text-sm text-cream-muted">ID: {{ product.id }}</p>
        </div>
        <div class="flex items-center gap-4">
          <button
            @click="router.push('/admin/products')"
            class="px-4 py-2 text-sm font-medium text-cream-faint hover:text-white bg-[#2a231c] hover:bg-[#342b22] rounded-lg transition-colors"
          >
            <font-awesome-icon icon="arrow-left" class="mr-2" />
            Back to Products
          </button>
          <button
            @click="handleEdit"
            class="px-4 py-2 text-sm font-medium text-oven-950 bg-crust hover:bg-crust-light rounded-full transition-colors"
          >
            Edit Product
          </button>
        </div>
      </div>

      <!-- Main Content -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Left Column - Basic Info -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Basic Information -->
          <div class="bg-[#1e1914] rounded-xl border border-cream/[0.07] overflow-hidden">
            <div class="p-6 border-b border-cream/[0.07]">
              <h2 class="text-lg font-bold text-white">Basic Information</h2>
            </div>
            <div class="p-6 space-y-6">
              <!-- Image -->
              <div class="aspect-video rounded-lg overflow-hidden bg-[#15120f]">
                <img
                  v-if="product.image"
                  :src="product.image"
                  :alt="product.name"
                  class="w-full h-full object-cover"
                />
                <div v-else class="w-full h-full flex items-center justify-center">
                  <font-awesome-icon icon="box-open" class="text-4xl text-cream/80" />
                </div>
              </div>

              <!-- Details -->
              <div class="grid grid-cols-2 gap-6">
                <div>
                  <label class="block text-sm font-medium text-cream-faint">Category</label>
                  <p class="mt-1 text-white">{{ product.category?.name || '—' }}</p>
                </div>
                <div>
                  <label class="block text-sm font-medium text-cream-faint">Price</label>
                  <p class="mt-1 text-white">{{ formatPrice(product.price) }} €</p>
                </div>
                <div>
                  <label class="block text-sm font-medium text-cream-faint">Stock</label>
                  <p class="mt-1" :class="getStockColor">{{ product.stock }} units</p>
                </div>
                <div>
                  <label class="block text-sm font-medium text-cream-faint">Status</label>
                  <p class="mt-1" :class="getStatusColor">{{ product.status }}</p>
                </div>
              </div>

              <!-- Description -->
              <div>
                <label class="block text-sm font-medium text-cream-faint">Description</label>
                <p class="mt-1 text-white">{{ product.description }}</p>
              </div>

              <!-- Dietary Information -->
              <div class="flex gap-4">
                <span
                  v-if="product.is_vegan"
                  class="px-3 py-1 text-sm font-medium text-green-500 bg-green-500/10 rounded-full"
                >
                  <font-awesome-icon icon="leaf" class="mr-1" />
                  Vegan
                </span>
                <span
                  v-if="product.is_vegetarian"
                  class="px-3 py-1 text-sm font-medium text-green-500 bg-green-500/10 rounded-full"
                >
                  <font-awesome-icon icon="seedling" class="mr-1" />
                  Vegetarian
                </span>
                <span
                  v-if="product.is_gluten_free"
                  class="px-3 py-1 text-sm font-medium text-yellow-500 bg-yellow-500/10 rounded-full"
                >
                  <font-awesome-icon icon="wheat-alt" class="mr-1" />
                  Gluten Free
                </span>
              </div>
            </div>
          </div>

          <!-- Ingredients -->
          <div class="bg-[#1e1914] rounded-xl border border-cream/[0.07] overflow-hidden">
            <div class="p-6 border-b border-cream/[0.07]">
              <h2 class="text-lg font-bold text-white">Ingredients</h2>
            </div>
            <div class="p-6">
              <div class="grid grid-cols-2 gap-4">
                <div v-for="ingredient in product.ingredients" :key="ingredient.id" 
                     class="p-4 bg-[#2a231c] rounded-lg">
                  <h3 class="font-medium text-white">{{ ingredient.name }}</h3>
                  <p v-if="ingredient.description" class="mt-1 text-sm text-cream-faint">
                    {{ ingredient.description }}
                  </p>
                  <!-- Allergens -->
                  <div v-if="ingredient.allergens?.length" class="mt-2 flex flex-wrap gap-2">
                    <span
                      v-for="allergen in ingredient.allergens"
                      :key="allergen.id"
                      class="px-2 py-1 text-xs font-medium text-red-500 bg-red-500/10 rounded-full"
                    >
                      {{ allergen.name }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column - Additional Info -->
        <div class="space-y-6">
          <!-- Nutrition Information -->
          <div class="bg-[#1e1914] rounded-xl border border-cream/[0.07] overflow-hidden">
            <div class="p-6 border-b border-cream/[0.07]">
              <h2 class="text-lg font-bold text-white">Nutrition Information</h2>
              <p class="mt-1 text-sm text-cream-faint">Per 100g serving</p>
            </div>
            <div class="p-6">
              <div class="space-y-4">
                <div class="flex justify-between items-center p-3 bg-[#2a231c] rounded-lg">
                  <span class="text-cream-faint">Calories</span>
                  <span class="text-white font-medium">
                    {{ product.nutrition_info?.calories || 0 }} kcal
                  </span>
                </div>
                <div class="flex justify-between items-center p-3 bg-[#2a231c] rounded-lg">
                  <span class="text-cream-faint">Proteins</span>
                  <span class="text-white font-medium">
                    {{ product.nutrition_info?.proteins || 0 }}g
                  </span>
                </div>
                <div class="flex justify-between items-center p-3 bg-[#2a231c] rounded-lg">
                  <span class="text-cream-faint">Carbohydrates</span>
                  <span class="text-white font-medium">
                    {{ product.nutrition_info?.carbohydrates || 0 }}g
                  </span>
                </div>
                <div class="flex justify-between items-center p-3 bg-[#2a231c] rounded-lg">
                  <span class="text-cream-faint">Fats</span>
                  <span class="text-white font-medium">
                    {{ product.nutrition_info?.fats || 0 }}g
                  </span>
                </div>
                <div class="flex justify-between items-center p-3 bg-[#2a231c] rounded-lg">
                  <span class="text-cream-faint">Fiber</span>
                  <span class="text-white font-medium">
                    {{ product.nutrition_info?.fiber || 0 }}g
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Stock Management -->
          <div class="bg-[#1e1914] rounded-xl border border-cream/[0.07] overflow-hidden">
            <div class="p-6 border-b border-cream/[0.07]">
              <h2 class="text-lg font-bold text-white">Stock Management</h2>
            </div>
            <div class="p-6">
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-cream-faint">Update Stock</label>
                  <div class="mt-2 flex gap-2">
                    <input
                      v-model="stockQuantity"
                      type="number"
                      min="0"
                      class="flex-1 px-4 py-2 bg-[#2a231c] border border-cream/[0.07] rounded-lg text-white focus:outline-none focus:border-red-500"
                      placeholder="Enter quantity"
                    />
                    <button
                      @click="updateStock"
                      :disabled="!stockQuantity"
                      class="px-4 py-2 text-sm font-medium text-white bg-ember hover:bg-ember/80 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors"
                    >
                      Update
                    </button>
                  </div>
                </div>
                
                <div class="flex justify-between items-center p-3 bg-[#2a231c] rounded-lg">
                  <span class="text-cream-faint">Current Stock</span>
                  <span :class="getStockColor" class="font-medium">
                    {{ product.stock }} units
                  </span>
                </div>
                
                <div class="flex justify-between items-center p-3 bg-[#2a231c] rounded-lg">
                  <span class="text-cream-faint">Status</span>
                  <span :class="getStatusColor" class="font-medium">
                    {{ product.status }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
    <ProductFormModal
      v-if="showForm && product"
      :product="product"
      :saving="saving"
      :server-errors="formErrors"
      @close="showForm = false"
      @save="saveProduct"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from '@/plugins/axios'
import ProductFormModal from './ProductFormModal.vue'
import { useProductStore } from '@/stores/productStore'
import { useToast } from '@/composables/useToast'

const productStore = useProductStore()
const { showToast } = useToast()

const router = useRouter()
const route = useRoute()
const loading = ref(true)
const product = ref(null)
const stockQuantity = ref(null)

const formatPrice = (price) => {
  return Number(price).toFixed(2)
}

const getStockColor = computed(() => {
  const stock = product.value?.stock || 0
  if (stock === 0) return 'text-red-500'
  if (stock < 10) return 'text-yellow-500'
  return 'text-green-500'
})

const getStatusColor = computed(() => {
  const status = product.value?.status
  const colors = {
    'draft': 'text-yellow-500',
    'active': 'text-green-500',
    'discontinued': 'text-red-500'
  }
  return colors[status] || 'text-cream-faint'
})

const loadError = ref('')
const showForm = ref(false)
const saving = ref(false)
const formErrors = ref({})

const fetchProduct = async () => {
  try {
    loading.value = true
    loadError.value = ''
    const response = await axios.get(`/api/products/${route.params.id}/`)
    product.value = response.data
  } catch (error) {
    loadError.value = error.response?.status === 404
      ? 'This product does not exist.'
      : 'The product could not be loaded.'
  } finally {
    loading.value = false
  }
}

const updateStock = async () => {
  try {
    const response = await axios.patch(`/api/products/${product.value.id}/`, {
      stock: stockQuantity.value
    })
    product.value = response.data
    stockQuantity.value = null
    showToast('Stock updated')
  } catch (error) {
    showToast('The stock could not be updated', 'error')
  }
}

const handleEdit = () => {
  formErrors.value = {}
  showForm.value = true
}

const saveProduct = async (data) => {
  saving.value = true
  formErrors.value = {}
  try {
    product.value = await productStore.updateProduct(data)
    showForm.value = false
    showToast('Product saved')
  } catch (error) {
    formErrors.value = error.response?.data || { general: 'The product could not be saved.' }
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchProduct()
})
</script>

<style scoped>
.animate-spin-slow {
  animation: spin 2s linear infinite;
}
.animate-spin-slower {
  animation: spin 3s linear infinite;
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
