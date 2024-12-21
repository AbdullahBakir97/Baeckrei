<template>
  <div class="animated-background">
    <!-- Gradient Definitions -->
    <svg class="background-pattern" preserveAspectRatio="xMidYMid slice" viewBox="0 0 1000 1000">
      <defs>
        <!-- Primary Gradient -->
        <linearGradient id="stroke-gradient-1" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color: #FF6B6B; stop-opacity: 1" />
          <stop offset="50%" style="stop-color: #FF4646; stop-opacity: 1" />
          <stop offset="100%" style="stop-color: #FF2525; stop-opacity: 1" />
        </linearGradient>

        <!-- Secondary Gradient -->
        <linearGradient id="stroke-gradient-2" x1="100%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" style="stop-color: #FF8585; stop-opacity: 1" />
          <stop offset="50%" style="stop-color: #FF6B6B; stop-opacity: 1" />
          <stop offset="100%" style="stop-color: #FF4646; stop-opacity: 1" />
        </linearGradient>

        <!-- Enhanced Glow Filter -->
        <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur in="SourceGraphic" stdDeviation="3" result="blur" />
          <feColorMatrix in="blur" type="matrix" values="
            1 0 0 0 1
            0 0 0 0 0.2
            0 0 0 0 0.2
            0 0 0 20 -10" 
            result="glow" />
          <feComposite in="glow" in2="SourceGraphic" operator="over" result="colored-glow" />
          <feMerge>
            <feMergeNode in="colored-glow" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>

        <!-- Professional Bakery Elements -->
        <g id="bakery-elements">
          <!-- Professional Croissant -->
          <path id="croissant" d="
            M 30,50 
            C 20,30 25,15 45,15 
            C 65,15 75,25 80,40 
            C 85,55 80,70 65,75 
            C 50,80 35,75 30,50 
            M 40,35 C 45,30 55,30 60,35 
            M 35,55 C 40,50 50,50 55,55" />

          <!-- Elegant Coffee Cup -->
          <path id="coffee" d="
            M 25,35 
            L 75,35 
            C 85,35 85,45 85,50 
            C 85,70 75,80 50,80 
            C 25,80 15,70 15,50 
            C 15,45 15,35 25,35 
            M 75,45 
            L 85,45 
            C 95,45 95,55 85,55 
            L 75,55 
            M 35,25 
            Q 50,15 65,25" />

          <!-- Detailed Cake -->
          <path id="cake" d="
            M 20,80 L 80,80 
            L 80,60 C 80,55 65,50 50,50 C 35,50 20,55 20,60 
            L 20,80 
            M 25,60 L 75,60 
            L 75,40 C 75,35 65,30 50,30 C 35,30 25,35 25,40 
            L 25,60 
            M 35,30 L 65,30 
            C 65,25 60,20 50,20 C 40,20 35,25 35,30 
            M 45,20 L 55,20 
            M 50,20 L 50,10" />

          <!-- Professional Cookie -->
          <path id="cookie" d="
            M 50,15 
            C 75,15 85,40 85,60 
            C 85,80 65,85 50,85 
            C 35,85 15,80 15,60 
            C 15,40 25,15 50,15 
            M 35,40 A 3,3 0 1,1 35,46 
            M 65,40 A 3,3 0 1,1 65,46 
            M 50,60 A 3,3 0 1,1 50,66 
            M 30,55 A 3,3 0 1,1 30,61 
            M 70,55 A 3,3 0 1,1 70,61" />

          <!-- Detailed Bread -->
          <path id="bread" d="
            M 25,70 
            C 25,40 75,40 75,70 
            C 75,85 65,90 50,90 
            C 35,90 25,85 25,70 
            M 35,50 C 35,35 65,35 65,50 
            M 30,60 Q 50,55 70,60 
            M 35,70 Q 50,65 65,70" />
        </g>
      </defs>

      <!-- Animated Elements -->
      <g v-for="n in elementCount" :key="n">
        <use :href="`#${randomElement()}`"
             class="bakery-element"
             :style="getElementStyle()" />
      </g>
    </svg>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const elementCount = ref(18)
const elements = ['croissant', 'coffee', 'cake', 'cookie', 'bread']

const randomElement = () => elements[Math.floor(Math.random() * elements.length)]

const getElementStyle = () => {
  const x = Math.random() * 1000
  const y = Math.random() * 1000
  const scale = 0.35 + Math.random() * 0.3
  const rotation = Math.random() * 360
  const delay = Math.random() * -40
  const duration = 30 + Math.random() * 20
  const gradient = Math.random() > 0.5 ? 'stroke-gradient-1' : 'stroke-gradient-2'

  return {
    '--x': `${x}px`,
    '--y': `${y}px`,
    '--scale': scale,
    '--rotation': `${rotation}deg`,
    '--delay': `${delay}s`,
    '--duration': `${duration}s`,
    '--gradient': `url(#${gradient})`
  }
}

let animationFrame
const animate = () => {
  const elements = document.querySelectorAll('.bakery-element')
  elements.forEach(element => {
    if (Math.random() < 0.01) {
      const newStyle = getElementStyle()
      Object.entries(newStyle).forEach(([key, value]) => {
        element.style.setProperty(key, value)
      })
    }
  })
  animationFrame = requestAnimationFrame(animate)
}

onMounted(() => {
  animate()
})

onUnmounted(() => {
  if (animationFrame) {
    cancelAnimationFrame(animationFrame)
  }
})
</script>

<style scoped>
.animated-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: -1;
  background: rgba(17, 17, 17, 0.98);
}

.background-pattern {
  width: 100%;
  height: 100%;
}

.bakery-element {
  fill: none;
  stroke: var(--gradient);
  stroke-width: 3.5;
  stroke-linecap: round;
  stroke-linejoin: round;
  filter: url(#glow);
  opacity: 0;
  transform-origin: center;
  will-change: transform, opacity;
  animation: 
    elementFade var(--duration) var(--delay) infinite cubic-bezier(0.645, 0.045, 0.355, 1.000),
    elementFloat calc(var(--duration) * 1.2) var(--delay) infinite cubic-bezier(0.445, 0.050, 0.550, 0.950);
  transition: all 0.3s ease-in-out;
}

@keyframes elementFade {
  0%, 100% {
    opacity: 0;
    stroke-dashoffset: 1000;
  }
  10%, 90% {
    opacity: 0.4;
    stroke-dashoffset: 0;
  }
  50% {
    opacity: 0.7;
    stroke-dashoffset: 0;
  }
}

@keyframes elementFloat {
  0% {
    transform: translate(var(--x), var(--y)) 
               scale(var(--scale)) 
               rotate(var(--rotation));
  }
  33% {
    transform: translate(calc(var(--x) + 40px), calc(var(--y) - 30px))
               scale(calc(var(--scale) * 1.15))
               rotate(calc(var(--rotation) + 120deg));
  }
  66% {
    transform: translate(calc(var(--x) - 30px), calc(var(--y) + 40px))
               scale(var(--scale))
               rotate(calc(var(--rotation) + 240deg));
  }
  100% {
    transform: translate(var(--x), var(--y))
               scale(var(--scale))
               rotate(calc(var(--rotation) + 360deg));
  }
}

@media (prefers-reduced-motion: reduce) {
  .bakery-element {
    animation: none !important;
  }
}
</style>