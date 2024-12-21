<template>
  <Transition name="modal">
    <div v-if="show" 
         class="fixed inset-0 flex items-center justify-center z-50"
         @mouseenter="keepOpen"
         @mouseleave="startCloseTimer">
      <div class="absolute inset-0 bg-black/60 backdrop-blur-sm"></div>
      
      <div class="relative bg-gray-900/90 rounded-xl overflow-hidden w-[90%] max-w-2xl
                  border border-white/10 shadow-2xl backdrop-blur-md
                  transform transition-all duration-300">
        <!-- Close Button -->
        <button @click="$emit('close')" 
                class="absolute top-4 right-4 text-gray-400 hover:text-white
                       transition-colors duration-200">
          <i class="fas fa-times text-xl"></i>
        </button>

        <div class="flex flex-col md:flex-row">
          <!-- Product Image -->
          <div class="relative w-full md:w-1/2 aspect-square">
            <img :src="product.image" 
                 :alt="product.name"
                 class="w-full h-full object-cover"
            />
            <div class="absolute inset-0 bg-gradient-to-t from-gray-900/80 to-transparent"></div>
          </div>

          <!-- Product Details -->
          <div class="w-full md:w-1/2 p-6 flex flex-col">
            <h2 class="text-2xl font-bold mb-2 bg-gradient-to-r from-red-400 to-red-600 
                       bg-clip-text text-transparent">
              {{ product.name }}
            </h2>

            <div class="flex items-center gap-2 mb-4">
              <span class="text-2xl font-bold text-red-500">
                ${{ formatPrice(product.price) }}
              </span>
              <span :class="[
                'px-2 py-1 rounded-full text-sm font-medium',
                product.stock > 5 ? 'bg-green-500/20 text-green-300' :
                product.stock > 0 ? 'bg-yellow-500/20 text-yellow-300' :
                'bg-red-500/20 text-red-300'
              ]">
                {{ product.stock > 5 ? 'In Stock' :
                   product.stock > 0 ? `Only ${product.stock} left` :
                   'Out of Stock' }}
              </span>
            </div>

            <p class="text-gray-300 mb-4">{{ product.description }}</p>

            <!-- Product Features -->
            <div class="space-y-2 mb-6">
              <div v-if="product.isVegan" 
                   class="flex items-center gap-2 text-green-300">
                <i class="fas fa-leaf"></i>
                <span>Vegan Friendly</span>
              </div>
              <div v-if="product.isGlutenFree" 
                   class="flex items-center gap-2 text-yellow-300">
                <i class="fas fa-wheat-alt"></i>
                <span>Gluten Free</span>
              </div>
            </div>

            <!-- Add to Cart Section -->
            <div class="mt-auto">
              <div class="flex items-center gap-4 mb-4">
                <div class="flex items-center gap-2">
                  <button @click="decrementQuantity"
                          :disabled="quantity <= 1"
                          class="p-2 rounded-lg bg-white/10 hover:bg-white/20 
                                 transition-colors duration-200
                                 disabled:opacity-50 disabled:cursor-not-allowed">
                    <i class="fas fa-minus"></i>
                  </button>
                  <span class="w-8 text-center">{{ quantity }}</span>
                  <button @click="incrementQuantity"
                          :disabled="quantity >= product.stock"
                          class="p-2 rounded-lg bg-white/10 hover:bg-white/20 
                                 transition-colors duration-200
                                 disabled:opacity-50 disabled:cursor-not-allowed">
                    <i class="fas fa-plus"></i>
                  </button>
                </div>
                <button @click="addToCart"
                        :disabled="!product.available"
                        class="flex-1 py-2 px-4 rounded-lg bg-gradient-to-r 
                               from-red-500 to-red-600 text-white font-medium
                               hover:from-red-600 hover:to-red-700
                               disabled:opacity-50 disabled:cursor-not-allowed
                               transition-all duration-200">
                  Add to Cart
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  product: {
    type: Object,
    required: true
  },
  show: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'add-to-cart'])

const quantity = ref(1)
let closeTimer = null

const formatPrice = (price) => {
  return price.toFixed(2)
}

const incrementQuantity = () => {
  if (quantity.value < props.product.stock) {
    quantity.value++
  }
}

const decrementQuantity = () => {
  if (quantity.value > 1) {
    quantity.value--
  }
}

const addToCart = () => {
  emit('add-to-cart', {
    product: props.product,
    quantity: quantity.value
  })
  emit('close')
}

const keepOpen = () => {
  if (closeTimer) {
    clearTimeout(closeTimer)
    closeTimer = null
  }
}

const startCloseTimer = () => {
  closeTimer = setTimeout(() => {
    emit('close')
  }, 300)
}

onUnmounted(() => {
  if (closeTimer) {
    clearTimeout(closeTimer)
  }
})
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease-out;
}

.modal-enter-from {
  opacity: 0;
  transform: scale(0.95);
}

.modal-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

/* Gradient Border Animation */
@keyframes borderGlow {
  0%, 100% {
    border-color: rgba(255, 255, 255, 0.1);
  }
  50% {
    border-color: rgba(239, 68, 68, 0.3);
  }
}

.modal-content {
  animation: borderGlow 2s infinite;
}
</style>
