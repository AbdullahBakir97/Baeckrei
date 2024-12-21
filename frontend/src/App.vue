<template>
  <div class="app bg-gray-900 min-h-screen">
    <AnimatedBackground />
    <Navbar />
    <main class="container mx-auto px-4 py-8">
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
  background-color: var(--color-bg-primary);
  color: var(--color-text-primary);
  min-height: 100vh;
  position: relative;
  isolation: isolate;
}

.container {
  background-color: var(--color-bg-primary);
}

/* Toast customization for dark theme */
.toast-container {
  background-color: var(--color-bg-secondary);
  color: var(--color-text-primary);
  border-color: var(--color-border);
}

.toast-success {
  background-color: var(--color-success);
}

.toast-error {
  background-color: var(--color-error);
}

.toast-warning {
  background-color: var(--color-warning);
}

/* Base styles */
:root {
  color-scheme: dark;
}

body {
  @apply bg-gray-900 text-gray-100;
  margin: 0;
  padding: 0;
}

#app {
  @apply text-gray-100;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Form Controls */
.input {
  @apply px-4 py-2 bg-gray-700 rounded-lg border border-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500;
}

.checkbox {
  @apply rounded border-gray-500 text-blue-600 focus:ring-blue-500;
}

/* Buttons */
.btn {
  @apply px-4 py-2 rounded-lg font-medium transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-primary {
  @apply bg-blue-600 text-white hover:bg-blue-700;
}

.btn-secondary {
  @apply bg-gray-700 text-gray-200 hover:bg-gray-600;
}

/* Cards */
.card {
  @apply bg-gray-800 rounded-lg shadow-sm border border-gray-700;
}
</style>