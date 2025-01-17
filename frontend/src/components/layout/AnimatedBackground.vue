<template>
  <div class="animated-background">
    <div class="gradient-overlay"></div>
    <div class="bakery-items">
      <div
        v-for="(item, index) in displayedItems"
        :key="item.id"
        class="bakery-item"
        :ref="el => itemRefs[index] = el"
      >
        <img 
          :src="item.src" 
          :alt="'Bakery item ' + (index + 1)"
          class="bakery-image"
          @load="initializeAnimation(index, $event.target)"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useWindowSize } from '@vueuse/core'
import { processImages } from '@/utils/imageProcessor'
import gsap from 'gsap'
import { MotionPathPlugin } from 'gsap/MotionPathPlugin'

gsap.registerPlugin(MotionPathPlugin)

const props = defineProps({
  images: {
    type: Array,
    required: true
  },
  maxItems: {
    type: Number,
    default: 30
  },
  visibleItems: {
    type: Number,
    default: 15
  }
})

const { width, height } = useWindowSize()
const processedItems = ref([])
const displayedItems = ref([])
const itemRefs = ref([])
const animations = ref([])
const currentSet = ref(0)

const BATCH_SIZE = 8
const STAGGER_DELAY = 0.3
const BASE_DURATION = 25
const ROTATION_INTERVAL = 45000
const zones = [
  { x: 0.3, y: 0.3, width: 0.4, height: 0.4 },
  { x: 0, y: 0, width: 0.4, height: 0.4 },
  { x: 0.6, y: 0, width: 0.4, height: 0.4 },
  { x: 0, y: 0.6, width: 0.4, height: 0.4 },
  { x: 0.6, y: 0.6, width: 0.4, height: 0.4 }
]

const getRandomPosition = (isEdge = false, preferredZone = null) => {
  const depth = Math.random() * 0.3 + 0.7
  const scale = 0.8 + (depth * 0.3)
  const opacity = 0.5 + (depth * 0.5)
  
  let x, y
  const extraSpace = 200
  
  if (isEdge) {
    const edge = Math.floor(Math.random() * 4)
    switch (edge) {
      case 0: // Top
        x = Math.random() * width.value
        y = -extraSpace
        break
      case 1: // Right
        x = width.value + extraSpace
        y = Math.random() * height.value
        break
      case 2: // Bottom
        x = Math.random() * width.value
        y = height.value + extraSpace
        break
      case 3: // Left
        x = -extraSpace
        y = Math.random() * height.value
        break
    }
  } else if (preferredZone) {
    const offsetX = (Math.random() - 0.5) * 50
    const offsetY = (Math.random() - 0.5) * 50
    
    x = (preferredZone.x + Math.random() * preferredZone.width) * width.value + offsetX
    y = (preferredZone.y + Math.random() * preferredZone.height) * height.value + offsetY
  } else {
    x = Math.random() * width.value
    y = Math.random() * height.value
  }

  return { x, y, scale, opacity, depth }
}

const updateDisplayedItems = () => {
  const totalItems = processedItems.value.length
  const itemsPerSet = props.visibleItems
  const startIndex = (currentSet.value * itemsPerSet) % totalItems
  
  let items = []
  for (let i = 0; i < itemsPerSet; i++) {
    const index = (startIndex + i) % totalItems
    items.push(processedItems.value[index])
  }
  
  const itemsPerZone = Math.ceil(itemsPerSet / zones.length)
  const distributedItems = items.map((item, index) => {
    const zoneIndex = Math.floor(index / itemsPerZone) % zones.length
    return {
      ...item,
      preferredZone: zones[zoneIndex]
    }
  })
  
  displayedItems.value = distributedItems
}

const rotateItems = () => {
  const fadeOutPromises = animations.value.map((anim, index) => {
    if (!anim) return Promise.resolve()
    
    const element = document.querySelector(`.bakery-item-${index}`)
    if (!element) return Promise.resolve()

    return new Promise(resolve => {
      gsap.to(element, {
        opacity: 0,
        scale: 0.5,
        duration: 1.5,
        ease: "power2.inOut",
        onComplete: () => {
          if (anim && anim.kill) anim.kill()
          resolve()
        }
      })
    })
  })

  Promise.all(fadeOutPromises).then(() => {
    animations.value = []
    itemRefs.value = []
    currentSet.value = (currentSet.value + 1) % Math.ceil(processedItems.value.length / props.visibleItems)
    updateDisplayedItems()
  })
}

const initializeAnimation = (index, element) => {
  if (!element || animations.value[index]) return

  const item = displayedItems.value[index]
  const batchIndex = Math.floor(index / BATCH_SIZE)
  const startPos = getRandomPosition(true)
  
  gsap.set(element.parentElement, {
    x: startPos.x,
    y: startPos.y,
    opacity: 0,
    scale: startPos.scale * 0.8,
    rotation: Math.random() * 30 - 15,
    transformOrigin: "center center",
    force3D: true
  })

  const masterTimeline = gsap.timeline({
    repeat: -1,
    defaults: { ease: "none" }
  })

  masterTimeline
    .to(element.parentElement, {
      opacity: startPos.opacity,
      scale: startPos.scale,
      duration: 2,
      ease: "power2.out"
    })
    
  const createMovementSequence = () => {
    const timeline = gsap.timeline()
    const duration = BASE_DURATION + (Math.random() * 4 - 2)
    
    const segments = 2
    let lastPos = getRandomPosition(false, item.preferredZone)
    
    for (let i = 0; i < segments; i++) {
      const nextPos = getRandomPosition(false, item.preferredZone)
      const segmentDuration = duration / segments
      
      const cp1x = lastPos.x + (nextPos.x - lastPos.x) * (0.4 + Math.random() * 0.2)
      const cp1y = lastPos.y + (Math.random() - 0.5) * 100
      const cp2x = nextPos.x - (nextPos.x - lastPos.x) * (0.4 + Math.random() * 0.2)
      const cp2y = nextPos.y + (Math.random() - 0.5) * 100
      
      timeline.to(element.parentElement, {
        motionPath: {
          path: `M${lastPos.x},${lastPos.y} C${cp1x},${cp1y} ${cp2x},${cp2y} ${nextPos.x},${nextPos.y}`,
          autoRotate: false
        },
        rotation: Math.random() * 30 - 15,
        scale: nextPos.scale,
        duration: segmentDuration,
        ease: "power1.inOut"
      })
      
      lastPos = nextPos
    }

    return timeline
  }

  for (let i = 0; i < 2; i++) {
    const sequence = createMovementSequence()
    masterTimeline.add(sequence, i === 0 ? ">" : "-=1")
  }

  const staggerDelay = batchIndex * STAGGER_DELAY
  masterTimeline.delay(staggerDelay)
  
  animations.value[index] = masterTimeline
}

onMounted(async () => {
  try {
    const processed = await processImages(props.images)
    const extraSpace = 200
    
    processedItems.value = processed.map((img, index) => ({
      ...img,
      id: `bakery-${index}`,
      x: -extraSpace + Math.random() * (width.value + extraSpace * 2),
      y: -extraSpace + Math.random() * (height.value + extraSpace * 2),
      rotation: Math.random() * 30 - 15,
      scale: 0.8
    }))
    
    updateDisplayedItems()
    
    setInterval(rotateItems, ROTATION_INTERVAL)
  } catch (error) {
    console.error('Error processing bakery images:', error)
  }
})

onUnmounted(() => {
  animations.value.forEach(anim => {
    if (anim) {
      anim.kill()
    }
  })
})
</script>

<style scoped>
.animated-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  pointer-events: none;
  z-index: -1;
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
}

.gradient-overlay {
  position: absolute;
  inset: 0;
  background: 
    linear-gradient(
      to bottom,
      #1a1a1a 0%,
      transparent 150px,
      transparent calc(100% - 150px),
      #1a1a1a 100%
    ),
    radial-gradient(
      circle at 50% 50%,
      rgba(239, 68, 68, 0.03) 0%,
      transparent 70%
    );
  mix-blend-mode: overlay;
}

.bakery-items {
  width: 100%;
  height: 100%;
  transform-style: preserve-3d;
  perspective: 1500px;
  will-change: transform;
}

.bakery-item {
  position: absolute;
  will-change: transform, opacity;
  backface-visibility: hidden;
  transform-style: preserve-3d;
}

.bakery-image {
  width: 70px;
  height: 70px;
  object-fit: contain;
  pointer-events: none;
  user-select: none;
  -webkit-user-drag: none;
  filter: drop-shadow(0 4px 8px rgba(0,0,0,0.12));
}

@media (prefers-reduced-motion: reduce) {
  .bakery-item {
    transition: opacity 0.3s ease;
  }
}
</style>
