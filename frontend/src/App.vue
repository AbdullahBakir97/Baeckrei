<template>
  <div class="app">
    <AnimatedBackground :images="bakeryImages" :maxItems="30" />
    <Navbar />
    <main class="main-container">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <Footer />
    <Toast />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import Navbar from '@/components/layout/Navbar.vue'
import Footer from '@/components/layout/Footer.vue'
import Toast from '@/components/common/Toast.vue'
import AnimatedBackground from '@/components/layout/AnimatedBackground.vue'

// Import bakery images
import img1 from '@/assets/bakery/_6c31eb8b-2e73-4336-8100-0d4665af533f-removebg-preview.png'
import img2 from '@/assets/bakery/_6d98c08d-fe70-49ab-b17d-e5311b0d486f-removebg-preview.png'
import img3 from '@/assets/bakery/_8b3e5425-2b1c-47e2-9b11-fa54cd4c6380-removebg-preview.png'
import img4 from '@/assets/bakery/_b3ba0503-ebcc-4641-8728-114f1a809c30-removebg-preview.png'
import img5 from '@/assets/bakery/_c0c68da2-178d-420e-8764-efbf02ce3a98-removebg-preview.png'
import img6 from '@/assets/bakery/_d514ba7a-e89e-45da-b5b4-bde24de3ec50-removebg-preview.png'
import img7 from '@/assets/bakery/_e2fc7fc0-c4a3-45ce-ab25-ac3243dad013-removebg-preview.png'
import img8 from '@/assets/bakery/_e7ecf254-d253-4be4-9e66-c23f42e2c3d4-removebg-preview.png'
import img9 from '@/assets/bakery/croissant.png'
import img10 from '@/assets/bakery/coffee3.png'
import img11 from '@/assets/bakery/cuppchtino.png'
import img12 from '@/assets/bakery/cuppo.png'
import img13 from '@/assets/bakery/latte.png'
import img14 from '@/assets/bakery/hotchocolate.png'
import img15 from '@/assets/bakery/ecklier.png'
import img16 from '@/assets/bakery/vbowl.png'
import whatsapp1 from '@/assets/bakery/WhatsApp_Image_2025-01-17_at_15.24.12_f2692574-removebg-preview.png'
import whatsapp2 from '@/assets/bakery/WhatsApp_Image_2025-01-17_at_15.38.00_c66d2370-removebg-preview.png'
import whatsapp3 from '@/assets/bakery/WhatsApp_Image_2025-01-17_at_15.40.25_944bb55f-removebg-preview.png'
import whatsapp4 from '@/assets/bakery/WhatsApp_Image_2025-01-17_at_15.42.12_78c711b9-removebg-preview.png'
import whatsapp5 from '@/assets/bakery/WhatsApp_Image_2025-01-17_at_15.47.19_c64dd93f-removebg-preview.png'


const bakeryImages = [
  img1, img2, img3, img4, img5, img6, img7, img8, img9, 
  img10, img11, img12, img13, img14, img15, img16,
  whatsapp1, whatsapp2, whatsapp3, whatsapp4, whatsapp5
]

onMounted(() => {
  // Any app-wide initialization can go here
})
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Dark theme overrides */
.app {
  min-height: 100vh;
  position: relative;
  isolation: isolate;
  color: var(--color-text-primary);
}

.main-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
  position: relative;
  z-index: 1;
}

/* Toast customization */
.toast-container {
  background-color: rgba(23, 23, 23, 0.8);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--color-text-primary);
}

.toast-success {
  background-color: rgba(34, 197, 94, 0.9);
}

.toast-error {
  background-color: rgba(239, 68, 68, 0.9);
}

.toast-warning {
  background-color: rgba(234, 179, 8, 0.9);
}

/* Base styles */
:root {
  color-scheme: dark;
}

body {
  margin: 0;
  padding: 0;
  color: #fff;
}

#app {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #fff;
}

/* Form Controls */
.input {
  @apply px-4 py-2 rounded-lg border focus:outline-none focus:ring-2 focus:ring-red-500;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-color: rgba(255, 255, 255, 0.1);
}

.checkbox {
  @apply rounded text-red-600 focus:ring-red-500;
  border-color: rgba(255, 255, 255, 0.2);
}

/* Buttons */
.btn {
  @apply px-4 py-2 rounded-lg font-medium transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-primary {
  @apply bg-red-600 text-white hover:bg-red-700;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #fff;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.15);
}

/* Cards */
.card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}
</style>