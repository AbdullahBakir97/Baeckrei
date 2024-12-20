<template>
  <div class="min-h-screen bg-gray-50">
    <Navbar />
    <main class="flex-grow container mx-auto px-4 py-8">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <Footer />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import Navbar from '@/components/layout/Navbar.vue'
import Footer from '@/components/layout/Footer.vue'

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

/* Base styles */
:root {
  color-scheme: light;
}

body {
  @apply bg-gray-50 text-gray-900;
  margin: 0;
  padding: 0;
}

#app {
  @apply text-gray-900;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Form Controls */
.input {
  @apply px-4 py-2 bg-white rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500;
}

.checkbox {
  @apply rounded border-gray-300 text-blue-600 focus:ring-blue-500;
}

/* Buttons */
.btn {
  @apply px-4 py-2 rounded-lg font-medium transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-primary {
  @apply bg-blue-600 text-white hover:bg-blue-700;
}

.btn-secondary {
  @apply bg-gray-200 text-gray-800 hover:bg-gray-300;
}

/* Cards */
.card {
  @apply bg-white rounded-lg shadow-sm border border-gray-200;
}
</style>