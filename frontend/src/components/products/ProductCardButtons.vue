<template>
  <div class="cart-controls">
    <template v-if="isInCart">
      <div class="cart-actions">
        <div class="quantity-controls">
          <button
            ref="decrementBtn"
            class="quantity-btn"
            :disabled="loading"
            @click="$emit('update-quantity', cartItem.quantity === 1 ? 0 : cartItem.quantity - 1)"
          >
            <font-awesome-icon icon="fa-solid fa-minus" />
          </button>
          
          <input 
            class="quantity"
            type="number"
            :value="cartItem.quantity"
            @input="$emit('update-quantity', $event.target.valueAsNumber)"
            min="1"
            :max="product.stock"
          />
          
          <button
            ref="incrementBtn"
            class="quantity-btn"
            :disabled="loading || cartItem.quantity >= product.stock"
            @click="$emit('update-quantity', cartItem.quantity + 1)"
          >
            <font-awesome-icon icon="fa-solid fa-plus" />
          </button>
        </div>
        <button 
          ref="removeBtn"
          class="remove-btn"
          :disabled="loading"
          @click="$emit('remove-from-cart')"
        >
          <font-awesome-icon icon="fa-solid fa-trash-can" />
          <span>Remove</span>
        </button>
      </div>
    </template>
    <template v-else>
      <button
        ref="addToCartBtn"
        class="add-to-cart-btn"
        :disabled="loading || !product.available"
        @click="$emit('add-to-cart')"
      >
        <font-awesome-icon icon="fa-solid fa-cart-plus" />
        <span>{{ product.stock > 0 ? 'Add to Cart' : 'Out of Stock' }}</span>
      </button>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { library } from '@fortawesome/fontawesome-svg-core'
import { 
  faCartPlus,
  faPlus,
  faMinus,
  faTrashCan
} from '@fortawesome/free-solid-svg-icons'

library.add(faCartPlus, faPlus, faMinus, faTrashCan)

const props = defineProps({
  product: {
    type: Object,
    required: true
  },
  cartItem: {
    type: Object,
    default: null
  },
  isInCart: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['add-to-cart', 'update-quantity', 'remove-from-cart'])

const addToCartBtn = ref(null)
const decrementBtn = ref(null)
const incrementBtn = ref(null)
const removeBtn = ref(null)

const handleMouseMove = (e, button) => {
  if (!button) return
  
  const rect = button.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  
  const centerX = rect.width / 2
  const centerY = rect.height / 2
  
  const rotateX = (y - centerY) / 8
  const rotateY = (centerX - x) / 8
  
  button.style.transform = `
    perspective(1000px)
    rotateX(${rotateX}deg)
    rotateY(${rotateY}deg)
    translateZ(10px)
  `
}

const resetButtonTransform = (button) => {
  if (!button) return
  button.style.transform = `
    perspective(1000px)
    rotateX(0deg)
    rotateY(0deg)
    translateZ(0px)
  `
}

onMounted(() => {
  // Add event listeners for mouse movement
  if (addToCartBtn.value) {
    addToCartBtn.value.addEventListener('mousemove', (e) => handleMouseMove(e, addToCartBtn.value))
    addToCartBtn.value.addEventListener('mouseleave', () => resetButtonTransform(addToCartBtn.value))
  }
  
  if (decrementBtn.value) {
    decrementBtn.value.addEventListener('mousemove', (e) => handleMouseMove(e, decrementBtn.value))
    decrementBtn.value.addEventListener('mouseleave', () => resetButtonTransform(decrementBtn.value))
  }
  
  if (incrementBtn.value) {
    incrementBtn.value.addEventListener('mousemove', (e) => handleMouseMove(e, incrementBtn.value))
    incrementBtn.value.addEventListener('mouseleave', () => resetButtonTransform(incrementBtn.value))
  }
  
  if (removeBtn.value) {
    removeBtn.value.addEventListener('mousemove', (e) => handleMouseMove(e, removeBtn.value))
    removeBtn.value.addEventListener('mouseleave', () => resetButtonTransform(removeBtn.value))
  }
})

onUnmounted(() => {
  // Clean up event listeners
  if (addToCartBtn.value) {
    addToCartBtn.value.removeEventListener('mousemove', handleMouseMove)
    addToCartBtn.value.removeEventListener('mouseleave', resetButtonTransform)
  }
  
  if (decrementBtn.value) {
    decrementBtn.value.removeEventListener('mousemove', handleMouseMove)
    decrementBtn.value.removeEventListener('mouseleave', resetButtonTransform)
  }
  
  if (incrementBtn.value) {
    incrementBtn.value.removeEventListener('mousemove', handleMouseMove)
    incrementBtn.value.removeEventListener('mouseleave', resetButtonTransform)
  }
  
  if (removeBtn.value) {
    removeBtn.value.removeEventListener('mousemove', handleMouseMove)
    removeBtn.value.removeEventListener('mouseleave', resetButtonTransform)
  }
})
</script>

<style scoped>
.cart-controls {
  @apply flex flex-col items-center gap-2 relative w-full;
  transform-style: preserve-3d;
}

.cart-actions {
  @apply flex flex-col items-center gap-3 w-full;
  transform-style: preserve-3d;
}

.quantity-controls {
  @apply flex items-center justify-center gap-1 w-auto;
  transform-style: preserve-3d;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 0.5rem;
  padding: 0.25rem;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.quantity-btn {
  @apply w-7 h-7 rounded-md flex items-center justify-center relative;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(245, 158, 11, 0.2);
  transform-style: preserve-3d;
  transition: all 0.15s ease;
  transform-origin: center center;
  will-change: transform;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.quantity-btn svg {
  color: #f59e0b;
  transition: all 0.3s ease;
}

.quantity-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(245, 158, 11, 0.4);
  box-shadow: 0 0 15px rgba(245, 158, 11, 0.2);
}

.quantity {
  @apply text-lg font-semibold text-center rounded-md text-gray-200;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(245, 158, 11, 0.2);
  width: 2.5rem;
  height: 1.75rem;
  outline: none;
  -moz-appearance: textfield;
  transition: all 0.15s ease;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.quantity:hover,
.quantity:focus {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(245, 158, 11, 0.4);
  box-shadow: 
    0 0 0 2px rgba(245, 158, 11, 0.1),
    0 0 20px rgba(245, 158, 11, 0.2);
}

.add-to-cart-btn {
  @apply w-full py-2 px-4 rounded-lg flex items-center justify-center gap-2 
         text-base font-semibold relative;
  background: transparent;
  border: 1px solid rgba(245, 158, 11, 0.3);
  transform-style: preserve-3d;
  transition: all 0.15s ease;
  transform-origin: center center;
  will-change: transform;
}

.add-to-cart-btn span,
.add-to-cart-btn svg {
  color: #f59e0b;
  transition: all 0.3s ease;
}

.add-to-cart-btn:hover {
  border-color: rgba(245, 158, 11, 0.8);
  box-shadow: 0 0 15px rgba(245, 158, 11, 0.2);
}

.add-to-cart-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  border-color: rgba(245, 158, 11, 0.1);
  box-shadow: none;
}

.remove-btn {
  @apply w-full py-2 px-4 rounded-lg flex items-center justify-center gap-2 
         text-base font-semibold relative;
  background: transparent;
  border: 1px solid rgba(245, 158, 11, 0.3);
  transform-style: preserve-3d;
  transition: all 0.15s ease;
  transform-origin: center center;
  will-change: transform;
}

.remove-btn span,
.remove-btn svg {
  color: #f59e0b;
  transition: all 0.3s ease;
}

.remove-btn:hover {
  border-color: rgba(245, 158, 11, 0.8);
  box-shadow: 0 0 15px rgba(245, 158, 11, 0.2);
}

button:not(:disabled):active {
  transform: perspective(1000px) translateZ(-10px);
}

button:disabled {
  @apply opacity-50 cursor-not-allowed;
  transform: none !important;
}

button:disabled span,
button:disabled svg {
  opacity: 0.5;
}

.out-of-stock-message {
  @apply text-gray-400 text-sm mt-2;
}
</style>
