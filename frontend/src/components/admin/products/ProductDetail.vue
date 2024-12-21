<template>
  <div class="space-y-8">
    <!-- Loading State -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-32">
      <div class="relative w-20 h-20">
        <div class="absolute inset-0 rounded-full border-t-2 border-red-500/30 animate-spin"></div>
        <div class="absolute inset-[4px] rounded-full border-t-2 border-red-500/50 animate-spin-slow"></div>
        <div class="absolute inset-[8px] rounded-full border-t-2 border-red-500/70 animate-spin-slower"></div>
      </div>
      <p class="mt-4 text-gray-400">Loading product details...</p>
    </div>

    <template v-else>
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-white">{{ product.name }}</h1>
          <p class="mt-1 text-sm text-gray-400">ID: {{ product.id }}</p>
        </div>
        <div class="flex items-center gap-4">
          <button
            @click="router.push('/admin/products')"
            class="px-4 py-2 text-sm font-medium text-gray-400 hover:text-white bg-[#1A2642] hover:bg-[#1E2A4A] rounded-lg transition-colors"
          >
            <i class="fas fa-arrow-left mr-2"></i>
            Back to Products
          </button>
          <button
            @click="handleEdit"
            class="px-4 py-2 text-sm font-medium text-white bg-red-500 hover:bg-red-600 rounded-lg transition-colors"
          >
            <i class="fas fa-edit mr-2"></i>
            Edit Product
          </button>
        </div>
      </div>

      <!-- Main Content -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Left Column - Basic Info -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Basic Information -->
          <div class="bg-[#131B2F] rounded-xl border border-white/5 overflow-hidden">
            <div class="p-6 border-b border-white/5">
              <h2 class="text-lg font-bold text-white">Basic Information</h2>
            </div>
            <div class="p-6 space-y-6">
              <!-- Image -->
              <div class="aspect-video rounded-lg overflow-hidden bg-[#0B1120]">
                <img
                  v-if="product.image"
                  :src="product.image"
                  :alt="product.name"
                  class="w-full h-full object-cover"
                />
                <div v-else class="w-full h-full flex items-center justify-center">
                  <i class="fas fa-image text-4xl text-gray-700"></i>
                </div>
              </div>

              <!-- Details -->
              <div class="grid grid-cols-2 gap-6">
                <div>
                  <label class="block text-sm font-medium text-gray-400">Category</label>
                  <p class="mt-1 text-white">{{ product.category.name }}</p>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-400">Price</label>
                  <p class="mt-1 text-white">${{ formatPrice(product.price) }}</p>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-400">Stock</label>
                  <p class="mt-1" :class="getStockColor">{{ product.stock }} units</p>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-400">Status</label>
                  <p class="mt-1" :class="getStatusColor">{{ product.status }}</p>
                </div>
              </div>

              <!-- Description -->
              <div>
                <label class="block text-sm font-medium text-gray-400">Description</label>
                <p class="mt-1 text-white">{{ product.description }}</p>
              </div>

              <!-- Dietary Information -->
              <div class="flex gap-4">
                <span
                  v-if="product.is_vegan"
                  class="px-3 py-1 text-sm font-medium text-green-500 bg-green-500/10 rounded-full"
                >
                  <i class="fas fa-leaf mr-1"></i>
                  Vegan
                </span>
                <span
                  v-if="product.is_vegetarian"
                  class="px-3 py-1 text-sm font-medium text-green-500 bg-green-500/10 rounded-full"
                >
                  <i class="fas fa-seedling mr-1"></i>
                  Vegetarian
                </span>
                <span
                  v-if="product.is_gluten_free"
                  class="px-3 py-1 text-sm font-medium text-yellow-500 bg-yellow-500/10 rounded-full"
                >
                  <i class="fas fa-wheat-alt mr-1"></i>
                  Gluten Free
                </span>
              </div>
            </div>
          </div>

          <!-- Ingredients -->
          <div class="bg-[#131B2F] rounded-xl border border-white/5 overflow-hidden">
            <div class="p-6 border-b border-white/5">
              <h2 class="text-lg font-bold text-white">Ingredients</h2>
            </div>
            <div class="p-6">
              <div class="grid grid-cols-2 gap-4">
                <div v-for="ingredient in product.ingredients" :key="ingredient.id" 
                     class="p-4 bg-[#1A2642] rounded-lg">
                  <h3 class="font-medium text-white">{{ ingredient.name }}</h3>
                  <p v-if="ingredient.description" class="mt-1 text-sm text-gray-400">
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
          <div class="bg-[#131B2F] rounded-xl border border-white/5 overflow-hidden">
            <div class="p-6 border-b border-white/5">
              <h2 class="text-lg font-bold text-white">Nutrition Information</h2>
              <p class="mt-1 text-sm text-gray-400">Per 100g serving</p>
            </div>
            <div class="p-6">
              <div class="space-y-4">
                <div class="flex justify-between items-center p-3 bg-[#1A2642] rounded-lg">
                  <span class="text-gray-400">Calories</span>
                  <span class="text-white font-medium">
                    {{ product.nutrition_info?.calories || 0 }} kcal
                  </span>
                </div>
                <div class="flex justify-between items-center p-3 bg-[#1A2642] rounded-lg">
                  <span class="text-gray-400">Proteins</span>
                  <span class="text-white font-medium">
                    {{ product.nutrition_info?.proteins || 0 }}g
                  </span>
                </div>
                <div class="flex justify-between items-center p-3 bg-[#1A2642] rounded-lg">
                  <span class="text-gray-400">Carbohydrates</span>
                  <span class="text-white font-medium">
                    {{ product.nutrition_info?.carbohydrates || 0 }}g
                  </span>
                </div>
                <div class="flex justify-between items-center p-3 bg-[#1A2642] rounded-lg">
                  <span class="text-gray-400">Fats</span>
                  <span class="text-white font-medium">
                    {{ product.nutrition_info?.fats || 0 }}g
                  </span>
                </div>
                <div class="flex justify-between items-center p-3 bg-[#1A2642] rounded-lg">
                  <span class="text-gray-400">Fiber</span>
                  <span class="text-white font-medium">
                    {{ product.nutrition_info?.fiber || 0 }}g
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Stock Management -->
          <div class="bg-[#131B2F] rounded-xl border border-white/5 overflow-hidden">
            <div class="p-6 border-b border-white/5">
              <h2 class="text-lg font-bold text-white">Stock Management</h2>
            </div>
            <div class="p-6">
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-400">Update Stock</label>
                  <div class="mt-2 flex gap-2">
                    <input
                      v-model="stockQuantity"
                      type="number"
                      min="0"
                      class="flex-1 px-4 py-2 bg-[#1A2642] border border-white/5 rounded-lg text-white focus:outline-none focus:border-red-500"
                      placeholder="Enter quantity"
                    />
                    <button
                      @click="updateStock"
                      :disabled="!stockQuantity"
                      class="px-4 py-2 text-sm font-medium text-white bg-red-500 hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors"
                    >
                      Update
                    </button>
                  </div>
                </div>
                
                <div class="flex justify-between items-center p-3 bg-[#1A2642] rounded-lg">
                  <span class="text-gray-400">Current Stock</span>
                  <span :class="getStockColor" class="font-medium">
                    {{ product.stock }} units
                  </span>
                </div>
                
                <div class="flex justify-between items-center p-3 bg-[#1A2642] rounded-lg">
                  <span class="text-gray-400">Status</span>
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from '@/plugins/axios'

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
  return colors[status] || 'text-gray-400'
})

const fetchProduct = async () => {
  try {
    loading.value = true
    const response = await axios.get(`/api/admin/products/${route.params.id}/`)
    product.value = response.data
  } catch (error) {
    console.error('Error fetching product:', error)
  } finally {
    loading.value = false
  }
}

const updateStock = async () => {
  try {
    await axios.patch(`/api/admin/products/${product.value.id}/`, {
      stock: stockQuantity.value
    })
    product.value.stock = stockQuantity.value
    stockQuantity.value = null
  } catch (error) {
    console.error('Error updating stock:', error)
  }
}

const handleEdit = () => {
  router.push(`/admin/products/${product.value.id}/edit`)
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
