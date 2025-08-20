<template>
  <div class="flex items-center justify-between w-full">
    <div class="flex items-center gap-4">
      <div class="quantity-controls">
        <button @click="$emit('update-quantity', product.id, quantity - 1)"
                :disabled="loading || quantity <= 1"
                class="w-8 h-8 rounded-lg bg-[rgba(255,255,255,0.02)] 
                       hover:bg-gradient-to-r hover:from-amber-500/20 hover:to-amber-600/20
                       flex items-center justify-center 
                       transition-all duration-300 group
                       disabled:opacity-50 disabled:cursor-not-allowed">
          <font-awesome-icon icon="minus" 
                           class="text-gray-400 group-hover:text-amber-500
                                  transition-colors duration-300" />
        </button>
        <span class="text-white font-medium w-6 text-center">{{ quantity }}</span>
        <button @click="$emit('update-quantity', product.id, quantity + 1)"
                :disabled="loading || quantity >= product.stock"
                :title="quantity >= product.stock ? 'Maximum stock reached' : ''"
                class="w-8 h-8 rounded-lg bg-[rgba(255,255,255,0.02)]
                       hover:bg-gradient-to-r hover:from-amber-500/20 hover:to-amber-600/20
                       flex items-center justify-center
                       transition-all duration-300 group
                       disabled:opacity-50 disabled:cursor-not-allowed">
          <font-awesome-icon icon="plus"
                           class="text-gray-400 group-hover:text-amber-500
                                  transition-colors duration-300" />
        </button>
      </div>
      <span v-if="quantity >= product.stock" 
            class="text-xs text-amber-500">
        Max stock reached
      </span>
    </div>
    <div class="flex items-center gap-6">
      <p class="text-2xl font-bold text-transparent bg-clip-text 
                 bg-gradient-to-r from-amber-400 to-amber-600">
        {{ formatPrice(totalPrice) }} €
      </p>
      <p class="text-sm text-gray-400 mt-1">
        {{ formatPrice(unitPrice) }} € each
      </p>
      <button @click="$emit('remove-item', product.id)"
              :disabled="loading"
              class="w-8 h-8 rounded-lg bg-[rgba(255,255,255,0.05)]
                     hover:bg-red-500/20 active:bg-red-500/30
                     flex items-center justify-center
                     transition-all duration-300 ease-in-out
                     group/trash
                     disabled:opacity-50 disabled:cursor-not-allowed">
        <font-awesome-icon icon="trash"
                         class="text-gray-400 group-hover/trash:text-red-400
                                transition-colors duration-300" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { computed } from 'vue'

const props = defineProps({
  quantity: {
    type: Number,
    required: true
  },
  product: {
    type: Object,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  unitPrice: {
    type: Number,
    required: true
  },
  totalPrice: {
    type: Number,
    required: true
  }
})

const formatPrice = (price) => {
  return Number(price).toFixed(2)
}

defineEmits(['update-quantity', 'remove-item'])
</script>

<style scoped>
.quantity-controls {
  @apply flex items-center rounded-lg;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(4px);
}

.disabled\:opacity-50:disabled {
  opacity: 0.5;
}

.disabled\:cursor-not-allowed:disabled {
  cursor: not-allowed;
}
</style>
