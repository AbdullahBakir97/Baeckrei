<template>
  <div class="app">
    <AmbientBackground />
    <a href="#main" class="skip-link">Skip to content</a>
    <Navbar />
    <main id="main" class="main-container" :class="{ 'is-full-bleed': route.meta.fullBleed }">
      <router-view v-slot="{ Component, route }">
        <transition :css="false" mode="out-in" @leave="onLeave" @enter="onEnter">
          <component :is="Component" :key="route.path" />
        </transition>
      </router-view>
    </main>
    <Footer />
    <Toast />
    <ModalWrapper />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from '@/components/layout/Navbar.vue'
import Footer from '@/components/layout/Footer.vue'
import Toast from '@/components/common/Toast.vue'
import AmbientBackground from '@/components/layout/AmbientBackground.vue'
import ModalWrapper from '@/components/common/ModalWrapper.vue'
import { gsap, ScrollTrigger, initSmoothScroll, scrollToTop, prefersReducedMotion } from '@/motion'

const route = useRoute()

// Page transitions: the old page lifts away, the new one settles in.
const onLeave = (el, done) => {
  if (prefersReducedMotion()) return done()
  gsap.to(el, { opacity: 0, y: -16, duration: 0.3, ease: 'power2.in', onComplete: done })
}

const onEnter = (el, done) => {
  scrollToTop()
  if (prefersReducedMotion()) {
    ScrollTrigger.refresh()
    return done()
  }
  gsap.fromTo(el, { opacity: 0, y: 24 }, {
    opacity: 1, y: 0, duration: 0.6, ease: 'power3.out', clearProps: 'transform,opacity',
    onComplete: () => { ScrollTrigger.refresh(); done() }
  })
}

onMounted(() => {
  initSmoothScroll()
})
</script>

<style>
/* Dark theme overrides */
.app {
  min-height: 100vh;
  position: relative;
  isolation: isolate;
  color: var(--color-text-primary);
}

/* Pages set their own width so sections can run edge to edge. The top
   padding clears the fixed navigation; full-bleed pages (the home hero)
   run underneath it. */
.main-container {
  position: relative;
  z-index: 1;
  min-height: 60vh;
  padding-top: 6rem;
}

.main-container.is-full-bleed {
  padding-top: 0;
}

.skip-link {
  position: fixed;
  top: 0.75rem;
  left: 0.75rem;
  z-index: 100;
  padding: 0.5rem 1rem;
  border-radius: 9999px;
  background: #e6a15a;
  color: #0e0c0a;
  font-weight: 700;
  transform: translateY(-200%);
  transition: transform 0.2s;
}

.skip-link:focus {
  transform: translateY(0);
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