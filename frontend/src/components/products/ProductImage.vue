<template>
  <div class="lg:col-span-1">
    <div class="info-card sticky top-4">
      <!-- Main Image -->
      <div class="relative group p-4">
        <!-- Glass background effect with lower z-index -->
        <div class="absolute inset-0 backdrop-blur-md bg-gradient-to-br from-white/10 to-transparent rounded-xl z-0"></div>
        <div class="absolute inset-0 shadow-inner border border-white/10 rounded-xl z-0"></div>
        
        <div class="aspect-square rounded-lg overflow-hidden bg-[rgba(255,255,255,0.02)] relative">
          <!-- Inner glass effect with lower z-index -->
          <div class="absolute inset-0 backdrop-blur-sm bg-gradient-to-br from-white/5 to-transparent z-0"></div>
          <img
            :src="getImageUrl(selectedImage || product.image)"
            :alt="product.name"
            @error="handleImageError"
            @click="openImageModal"
            class="w-full h-full object-contain mix-blend-normal transform transition-transform duration-500 
                   group-hover:scale-110 cursor-zoom-in relative z-10"
          >
        </div>
        <!-- Button container with higher z-index -->
        <div class="absolute top-2 right-2 space-y-2 z-20">
          <button @click="openImageModal"
                  class="bg-black/50 p-2 rounded-full opacity-0 group-hover:opacity-100 
                        transition-opacity duration-300 hover:bg-black/70 relative
                        hover:ring-2 hover:ring-blue-500/50"
                  :class="{ 'ring-2 ring-blue-500/50': showZoomModal }">
            <font-awesome-icon icon="magnifying-glass-plus" 
                              class="text-white text-lg hover:text-blue-500 
                                      transition-colors duration-300" />
          </button>

          <button @click="shareProduct"
                  class="bg-black/50 p-2 rounded-full opacity-0 group-hover:opacity-100 
                        transition-opacity duration-300 hover:bg-black/70 relative
                        hover:ring-2 hover:ring-green-500/50">
            <font-awesome-icon icon="share-nodes" 
                              class="text-white text-lg hover:text-green-500 
                                      transition-colors duration-300" />
          </button>
          
          <button @click="toggleWishlist"
                  class="bg-black/50 p-2 rounded-full opacity-0 group-hover:opacity-100 
                         transition-opacity duration-300 hover:bg-black/70 relative
                         hover:ring-2 hover:ring-red-500/50"
                  :class="{ 'text-red-500': isInWishlist }">
            <font-awesome-icon :icon="['far', 'heart']" class="text-white text-lg" 
                             :class="{ '!text-red-500': isInWishlist }" />
          </button>
          
          <button @click="toggleCompare"
                  class="bg-black/50 p-2 rounded-full opacity-0 group-hover:opacity-100 
                         transition-opacity duration-300 hover:bg-black/70 relative"
                  :class="{ 'text-amber-500': isInCompare }">
            <font-awesome-icon icon="code-compare" class="text-white text-lg"
                             :class="{ '!text-amber-500': isInCompare }" />
          </button>
        </div>
      </div>

      <!-- Keep ImageZoomModal unchanged -->
      <ImageZoomModal
        v-if="showZoomModal"
        :images="allImages"
        :initial-index="currentImageIndex"
        :product-name="product.name"
        @close="closeZoomModal"
        v-model="showZoomModal"
      />
      
      <!-- Thumbnail Images with updated background -->
      <div v-if="product.images?.length > 0" 
           class="grid grid-cols-5 gap-2 p-4 pt-0 relative">
        <!-- Add glass background effect for thumbnail container -->
        <div class="absolute inset-0 backdrop-blur-sm bg-gradient-to-br from-white/5 to-transparent rounded-xl"></div>
        
        <button
          @click="selectedImage = null; openImageModal()"
          class="relative aspect-square rounded-lg overflow-hidden bg-[rgba(255,255,255,0.02)]
                 hover:ring-2 hover:ring-amber-500/50 transition-all duration-300"
          :class="{ 'ring-2 ring-amber-500': !selectedImage }"
        >
          <img
            :src="getImageUrl(product.image)"
            :alt="`${product.name} main`"
            @error="handleImageError"
            class="w-full h-full object-contain mix-blend-normal hover:scale-105 
                   transition-transform duration-300"
          >
        </button>

        <button
          v-for="(image, index) in product.images.slice(0, 4)"
          :key="index"
          @click="selectedImage = image; openImageModal()"
          class="relative aspect-square rounded-lg overflow-hidden bg-[rgba(255,255,255,0.02)]
                 hover:ring-2 hover:ring-amber-500/50 transition-all duration-300"
          :class="{ 'ring-2 ring-amber-500': selectedImage === image }"
        >
          <img
            :src="getImageUrl(image)"
            :alt="`${product.name} thumbnail ${index + 1}`"
            @error="handleImageError"
            class="w-full h-full object-contain mix-blend-normal hover:scale-105 
                   transition-transform duration-300"
          >
        </button>
      </div>
    </div>
  </div>
</template>
  
  <script setup>
    import { ref, computed } from 'vue'
    import { useProductStore } from '@/stores/productStore'
    import { useModalStore } from '@/stores/modalStore'
    import ImageZoomModal from '@/components/common/ImageZoomModal.vue'

    const props = defineProps({
    product: {
        type: Object,
        required: true
    },
    isInWishlist: {
        type: Boolean,
        default: false
    },
    isInCompare: {
        type: Boolean,
        default: false
    }
    })

    const emit = defineEmits(['toggleWishlist', 'toggleCompare', 'shareProduct'])

    const showZoomModal = ref(false)
    const selectedImage = ref(null)
    const productStore = useProductStore()
    const modalStore = useModalStore()

    const openImageModal = (image = null) => {
      const imageIndex = image ? allImages.value.indexOf(image) : 0
      
      modalStore.openModal({
          component: 'ImageZoomModal',
          props: {
              images: allImages.value,
              initialIndex: Math.max(0, imageIndex), // Ensure it's never negative
              productName: props.product.name,
              modelValue: true,
              onClose: () => modalStore.closeModal()
          }
      })
    }
    
    // Close zoom modal function
    const closeZoomModal = () => {
        showZoomModal.value = false;
        modalStore.closeModal('imageZoom');
    }

    // Updated getImageUrl function
    const getImageUrl = (image) => {
        if (!image) return '/images/placeholder.png'
        
        // If image is a string (direct URL or path)
        if (typeof image === 'string') {
            return image.startsWith('http') ? image : `/media/${image}`
        }
        
        // If image is an object with url property
        if (image.url) {
            return image.url
        }
        
        // If image is an object with image_url property
        if (image.image_url) {
            return image.image_url
        }
        
        // Fallback to placeholder
        return '/images/placeholder.png'
    }
    
    // Computed property for all images
    const allImages = computed(() => {
        if (!props.product) return []
        
        const images = [getImageUrl(props.product.image)]
        if (props.product.images?.length) {
        images.push(...props.product.images.map(img => getImageUrl(img)))
        }
        return images.filter(img => img !== '/images/placeholder.png') // Filter out placeholders
    })
    
    // Get current image index
    const currentImageIndex = computed(() => {
        if (!selectedImage.value) return 0
        return allImages.value.findIndex(img => img === getImageUrl(selectedImage.value))
    })
    
    const handleImageError = (event) => {
        event.target.src = '/images/placeholder.png'
    }
    
    const shareProduct = () => {
        emit('shareProduct')
    }
    
    const toggleWishlist = () => {
        emit('toggleWishlist')
    }
    
    const toggleCompare = () => {
        emit('toggleCompare')
    }
  </script>