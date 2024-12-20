<template>
  <div
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    @click.self="$emit('close')"
  >
    <div class="bg-white rounded-lg max-w-3xl w-full mx-4 overflow-hidden">
      <!-- Close Button -->
      <button
        @click="$emit('close')"
        class="absolute top-4 right-4 text-gray-500 hover:text-gray-700"
      >
        <i class="fas fa-times text-xl"></i>
      </button>

      <div class="flex flex-col md:flex-row">
        <!-- Product Image -->
        <div class="md:w-1/2">
          <div class="relative pb-[100%]">
            <img
              :src="product.image"
              :alt="product.name"
              class="absolute inset-0 w-full h-full object-cover"
            >
          </div>
        </div>

        <!-- Product Details -->
        <div class="p-6 md:w-1/2">
          <div class="mb-6">
            <h2 class="text-2xl font-bold mb-2">{{ product.name }}</h2>
            <p class="text-gray-600">{{ product.description }}</p>
          </div>

          <!-- Price -->
          <div class="flex items-center gap-2 mb-4">
            <span class="text-2xl font-bold text-gray-900">
              ${{ formatPrice(product.price) }}
            </span>
            <span
              v-if="product.oldPrice"
              class="text-lg text-gray-500 line-through"
            >
              ${{ formatPrice(product.oldPrice) }}
            </span>
          </div>

          <!-- Stock Status -->
          <div class="mb-4">
            <span
              :class="{
                'text-green-600': product.available,
                'text-red-600': !product.available
              }"
            >
              {{ product.available ? 'In Stock' : 'Out of Stock' }}
            </span>
          </div>

          <!-- Dietary Information -->
          <div class="mb-6">
            <h3 class="font-semibold mb-2">Dietary Information</h3>
            <div class="flex flex-wrap gap-2">
              <span
                v-if="product.isVegan"
                class="badge badge-green"
              >
                <i class="fas fa-leaf mr-1"></i>
                Vegan
              </span>
              <span
                v-if="product.isVegetarian"
                class="badge badge-green"
              >
                <i class="fas fa-seedling mr-1"></i>
                Vegetarian
              </span>
              <span
                v-if="product.isGlutenFree"
                class="badge badge-yellow"
              >
                <i class="fas fa-wheat-alt mr-1"></i>
                Gluten Free
              </span>
            </div>
          </div>

          <!-- Ingredients -->
          <div class="mb-6">
            <h3 class="font-semibold mb-2">Ingredients</h3>
            <ul class="list-disc list-inside text-gray-600">
              <li v-for="ingredient in product.ingredients" :key="ingredient.id">
                {{ ingredient.name }}
              </li>
            </ul>
          </div>

          <!-- Allergens -->
          <div class="mb-6">
            <h3 class="font-semibold mb-2">Allergens</h3>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="allergen in product.allergens"
                :key="allergen.id"
                class="badge badge-red"
              >
                {{ allergen.name }}
              </span>
            </div>
          </div>

          <!-- Add to Cart -->
          <div class="flex items-center gap-4">
            <div class="flex items-center border rounded-lg">
              <button
                @click="decrementQuantity"
                class="px-3 py-2 hover:bg-gray-100"
                :disabled="quantity <= 1"
              >
                <i class="fas fa-minus"></i>
              </button>
              <input
                type="number"
                v-model.number="quantity"
                min="1"
                class="w-16 text-center border-x py-2"
              >
              <button
                @click="incrementQuantity"
                class="px-3 py-2 hover:bg-gray-100"
              >
                <i class="fas fa-plus"></i>
              </button>
            </div>
            <button
              @click="addToCart"
              :disabled="!product.available || loading"
              class="btn btn-primary flex-grow"
              :class="{ 'opacity-50 cursor-not-allowed': !product.available || loading }"
            >
              <i class="fas fa-shopping-cart mr-2"></i>
              {{ loading ? 'Adding...' : 'Add to Cart' }}
            </button>
          </div>

          <!-- View Full Details Link -->
          <div class="mt-4 text-center">
            <router-link
              :to="{ name: 'product-detail', params: { id: product.id }}"
              class="text-primary-600 hover:text-primary-700"
            >
              View Full Details
              <i class="fas fa-arrow-right ml-1"></i>
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useCartStore } from '@/stores/cartStore'

const props = defineProps({
  product: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close'])

const cartStore = useCartStore()
const quantity = ref(1)
const loading = ref(false)

// Methods
const formatPrice = (price) => {
  return price.toFixed(2)
}

const incrementQuantity = () => {
  quantity.value++
}

const decrementQuantity = () => {
  if (quantity.value > 1) {
    quantity.value--
  }
}

const addToCart = async () => {
  if (!props.product.available) return

  try {
    loading.value = true
    await cartStore.addToCart(props.product, quantity.value)
    // You could add a toast notification here
    emit('close')
  } catch (error) {
    console.error('Failed to add to cart:', error)
    // Handle error (show error toast, etc.)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.badge {
  @apply px-2 py-1 rounded-full text-sm font-medium;
}

.badge-green {
  @apply bg-green-100 text-green-800;
}

.badge-yellow {
  @apply bg-yellow-100 text-yellow-800;
}

.badge-red {
  @apply bg-red-100 text-red-800;
}

/* Add transition for modal */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
