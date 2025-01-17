<template>
  <div class="bg-[rgba(255,255,255,0.05)] backdrop-blur-xl shadow-xl rounded-2xl p-6 
              border border-[rgba(255,255,255,0.1)] hover:border-amber-500/30
              transition-all duration-500 ease-in-out group
              hover:shadow-amber-500/10 hover:bg-[rgba(255,255,255,0.07)]">
    <div class="flex items-center gap-6">
      <!-- Product Image -->
      <div class="w-32 h-32 rounded-xl overflow-hidden bg-[rgba(255,255,255,0.03)] 
                  backdrop-blur-sm shadow-inner group-hover:shadow-amber-500/5
                  transition-all duration-500 ease-in-out">
        <img v-if="product.image"
             :src="product.image"
             :alt="product.name"
             class="w-full h-full object-cover transform group-hover:scale-110 
                    transition-transform duration-700 ease-in-out"
             @error="$event.target.src = '/images/placeholder.png'" />
      </div>

      <!-- Product Info -->
      <div class="flex-1">
        <h3 class="text-xl font-bold text-white mb-2 group-hover:text-amber-500/90
                   transition-colors duration-300">
          {{ product.name }}
        </h3>
        <p class="text-sm text-gray-400 mb-4">
          {{ product.description }}
        </p>
        <QuantityControl 
          :quantity="quantity"
          :loading="loading"
          :product="product"
          :total-price="numericTotalPrice"
          :unit-price="numericUnitPrice"
          @update-quantity="(id, newQuantity) => $emit('update-quantity', id, newQuantity)"
          @remove-item="(id) => $emit('remove-item', id)"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, computed } from 'vue'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import QuantityControl from './QuantityControl.vue'

const props = defineProps({
  product: {
    type: Object,
    required: true
  },
  quantity: {
    type: Number,
    required: true
  },
  unitPrice: {
    type: [Number, String],
    required: true
  },
  totalPrice: {
    type: [Number, String],
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const numericTotalPrice = computed(() => Number(props.totalPrice))
const numericUnitPrice = computed(() => Number(props.unitPrice))

defineEmits(['update-quantity', 'remove-item'])

const formatPrice = (price) => {
  return Number(price || 0).toFixed(2)
}
</script>

<style scoped>
.cart-item {
  @apply rounded-lg p-6 transition-all duration-300;
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.cart-item:hover {
  background: rgba(255, 255, 255, 0.03);
  border-color: rgba(245, 158, 11, 0.3);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.1),
    0 4px 8px rgba(245, 158, 11, 0.2);
}

.remove-btn {
  @apply flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg
         text-gray-300 hover:text-amber-400 disabled:opacity-50 transition-all duration-300;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
</style>
