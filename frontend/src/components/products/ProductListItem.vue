<template>
  <div class="card flex">
    <!-- Product Image -->
    <div class="w-48 flex-shrink-0">
      <div class="relative h-full">
        <img
          :src="product.image"
          :alt="product.name"
          class="w-full h-full object-cover"
        >
        <!-- Badges -->
        <div class="absolute top-2 left-2 flex flex-col gap-1">
          <span
            v-if="product.isNew"
            class="bg-primary-500 text-white text-xs px-2 py-1 rounded"
          >
            New
          </span>
          <span
            v-if="!product.available"
            class="bg-red-500 text-white text-xs px-2 py-1 rounded"
          >
            Out of Stock
          </span>
        </div>
      </div>
    </div>

    <!-- Product Info -->
    <div class="flex-grow p-4 flex flex-col">
      <div class="flex-grow">
        <!-- Category -->
        <div class="text-sm text-gray-500 mb-1">
          {{ product.category.name }}
        </div>

        <!-- Name -->
        <h3 class="text-lg font-semibold mb-2 hover:text-primary-600 transition-colors">
          <router-link :to="{ name: 'product-detail', params: { id: product.id }}">
            {{ product.name }}
          </router-link>
        </h3>

        <!-- Description -->
        <p class="text-gray-600 text-sm mb-4">
          {{ product.description }}
        </p>

        <!-- Dietary Info -->
        <div class="flex gap-2 mb-4">
          <span
            v-if="product.isVegan"
            class="text-xs px-2 py-1 bg-green-100 text-green-800 rounded-full"
          >
            Vegan
          </span>
          <span
            v-if="product.isVegetarian"
            class="text-xs px-2 py-1 bg-green-100 text-green-800 rounded-full"
          >
            Vegetarian
          </span>
          <span
            v-if="product.isGlutenFree"
            class="text-xs px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full"
          >
            Gluten Free
          </span>
        </div>
      </div>

      <!-- Price and Actions -->
      <div class="flex items-center justify-between mt-4">
        <div class="flex items-center gap-2">
          <span class="text-lg font-bold text-gray-900">
            ${{ formatPrice(product.price) }}
          </span>
          <span
            v-if="product.oldPrice"
            class="text-sm text-gray-500 line-through"
          >
            ${{ formatPrice(product.oldPrice) }}
          </span>
        </div>

        <div class="flex items-center gap-2">
          <button
            @click="showQuickView = true"
            class="btn btn-secondary"
          >
            <i class="fas fa-eye mr-2"></i>
            Quick View
          </button>
          <button
            @click="$emit('add-to-cart', product)"
            :disabled="!product.available"
            class="btn btn-primary"
            :class="{ 'opacity-50 cursor-not-allowed': !product.available }"
          >
            <i class="fas fa-shopping-cart mr-2"></i>
            Add to Cart
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Quick View Modal -->
  <QuickViewModal
    v-if="showQuickView"
    :product="product"
    @close="showQuickView = false"
    @add-to-cart="$emit('add-to-cart', product)"
  />
</template>

<script setup>
import { ref } from 'vue'
import QuickViewModal from './QuickViewModal.vue'

const props = defineProps({
  product: {
    type: Object,
    required: true
  }
})

defineEmits(['add-to-cart'])

// State
const showQuickView = ref(false)

// Methods
const formatPrice = (price) => {
  return price.toFixed(2)
}
</script>

<style scoped>
/* Add any custom styles here */
</style>
