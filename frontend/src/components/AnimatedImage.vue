<template>
  <div 
    class="animated-image-container"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
  >
    <div 
      class="animated-image"
      :style="{
        width: `${width}px`,
        height: `${height}px`
      }"
    >
      <img 
        :src="image.src" 
        :alt="alt"
        :class="{
          'hover-effect': isHovered,
          'animate-in': shouldAnimate
        }"
        @load="handleImageLoad"
      >
      <div 
        class="shadow"
        :class="{
          'shadow-hover': isHovered
        }"
      ></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { pauseAnimation, resumeAnimation, resetAnimation } from '@/utils/imageProcessor'

const props = defineProps({
  image: {
    type: Object,
    required: true
  },
  width: {
    type: Number,
    default: 300
  },
  height: {
    type: Number,
    default: 300
  },
  alt: {
    type: String,
    default: 'Product image'
  }
})

const isHovered = ref(false)
const shouldAnimate = ref(false)

const handleMouseEnter = () => {
  isHovered.value = true
  resumeAnimation(props.image)
}

const handleMouseLeave = () => {
  isHovered.value = false
  pauseAnimation(props.image)
}

const handleImageLoad = () => {
  shouldAnimate.value = true
  resetAnimation(props.image)
}

onMounted(() => {
  shouldAnimate.value = true
})

onUnmounted(() => {
  pauseAnimation(props.image)
})
</script>

<style scoped>
.animated-image-container {
  perspective: 1000px;
  transform-style: preserve-3d;
}

.animated-image {
  position: relative;
  transform-style: preserve-3d;
  transition: transform 0.3s ease;
}

.animated-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  transform: translateZ(20px);
  opacity: 0;
  transition: all 0.3s ease;
}

.animated-image img.animate-in {
  opacity: 1;
}

.animated-image img.hover-effect {
  transform: translateZ(30px);
}

.shadow {
  position: absolute;
  bottom: -20px;
  left: 0;
  right: 0;
  height: 20px;
  background: radial-gradient(ellipse at center, rgba(0,0,0,0.2) 0%, rgba(0,0,0,0) 70%);
  transform: rotateX(90deg);
  filter: blur(5px);
  opacity: 0;
  transition: all 0.3s ease;
}

.shadow.shadow-hover {
  opacity: 1;
  filter: blur(8px);
  transform: rotateX(90deg) scale(1.1);
}

.animated-image:hover {
  transform: translateY(-10px);
}
</style>
