<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/60"> <!-- Added overlay background -->
    <div class="relative w-full h-full max-w-4xl mx-auto flex flex-col">
      <!-- Close button -->
      <button
        @click="handleClose"
        class="absolute top-4 right-4 z-50 p-2 bg-black/50 rounded-full hover:bg-black/70 transition-colors"
      >
        <font-awesome-icon icon="times" class="text-white text-xl" />
      </button>

      <!-- Image container with glass effect -->
      <div class="relative flex-1 flex items-center justify-center p-4">
        <div class="absolute inset-0 backdrop-blur-sm bg-white/10"></div> <!-- Glass effect background -->
        <img
          :key="currentImage"
          :src="currentImage"
          :alt="productName"
          class="relative z-10 max-h-[80vh] max-w-full object-contain"
          @error="handleImageError"
          ref="mainImage"
        />
        
        <!-- Navigation buttons -->
        <button
          v-if="images.length > 1 && currentIndex > 0"
          @click="previousImage"
          class="absolute left-4 p-2 bg-black/50 rounded-full hover:bg-black/70 transition-colors z-20"
        >
          <font-awesome-icon icon="chevron-left" class="text-white text-xl" />
        </button>
        
        <button
          v-if="images.length > 1 && currentIndex < images.length - 1"
          @click="nextImage"
          class="absolute right-4 p-2 bg-black/50 rounded-full hover:bg-black/70 transition-colors z-20"
        >
          <font-awesome-icon icon="chevron-right" class="text-white text-xl" />
        </button>
      </div>

      <!-- Thumbnails with glass effect -->
      <div v-if="images.length > 1" class="relative flex justify-center gap-2 p-4">
        <div class="absolute inset-0 backdrop-blur-sm bg-white/10"></div> <!-- Glass effect background -->
        <button
          v-for="(image, index) in images"
          :key="index"
          @click="currentIndex = index"
          class="relative z-10 w-16 h-16 rounded-lg overflow-hidden transition-transform hover:scale-105"
          :class="{ 'ring-2 ring-amber-500': currentIndex === index }"
        >
          <img 
            :src="image"
            :alt="`${productName} thumbnail ${index + 1}`"
            class="w-full h-full object-cover"
            @error="handleThumbnailError"
          >
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed, onMounted } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true
  },
  images: {
    type: Array,
    required: true,
    validator: (value) => value.length > 0
  },
  initialIndex: {
    type: Number,
    default: 0,
    validator: (value) => value >= 0
  },
  productName: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['update:modelValue', 'close'])
const mainImage = ref(null)
const currentIndex = ref(0) // Initialize with 0

// Initialize currentIndex when component mounts
onMounted(() => {
    currentIndex.value = props.initialIndex >= 0 && props.initialIndex < props.images.length 
        ? props.initialIndex 
        : 0
})

// Watch for props changes
watch(() => props.images, (newImages) => {
    console.log('Images changed:', newImages)
}, { immediate: true })

watch(() => props.initialIndex, (newIndex) => {
    console.log('Initial index changed:', newIndex)
    if (newIndex >= 0 && newIndex < props.images.length) {
        currentIndex.value = newIndex
    }
}, { immediate: true })

const currentImage = computed(() => {
    const index = currentIndex.value >= 0 && currentIndex.value < props.images.length 
        ? currentIndex.value 
        : 0
    return props.images[index] || props.images[0] || '/placeholder.png'
})

const handleImageError = (event) => {
    event.target.src = '/placeholder.png'
}

const handleThumbnailError = (event) => {
    event.target.src = '/placeholder.png'
}

const handleClose = () => {
    emit('update:modelValue', false)
    emit('close')
}

const previousImage = () => {
    if (currentIndex.value > 0) {
        currentIndex.value--
    }
}

const nextImage = () => {
    if (currentIndex.value < props.images.length - 1) {
        currentIndex.value++
    }
}
</script>

<style scoped>
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgba(251, 191, 36, 0.5) rgba(255, 255, 255, 0.1);
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(251, 191, 36, 0.5);
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(251, 191, 36, 0.7);
}
</style>
