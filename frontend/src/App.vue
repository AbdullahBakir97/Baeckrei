<template>
  <div class="app">
    <AmbientBackground v-if="!bare" />
    <a href="#main" class="skip-link">{{ $t('common.skipToContent') }}</a>
    <AnnouncementBar v-if="!bare" />
    <Navbar v-if="!bare" />
    <main id="main" class="main-container" :class="{ 'is-full-bleed': route.meta.fullBleed || isAdmin }">
      <router-view v-slot="{ Component, route }">
        <transition :css="false" mode="out-in" @leave="onLeave" @enter="onEnter">
          <!-- The admin area keeps its layout mounted while its pages change. -->
          <component :is="Component" :key="`${isAdmin ? 'admin' : route.path}:${locale}`" />
        </transition>
      </router-view>
    </main>
    <Footer v-if="!bare" :key="locale" />
    <Toast />
    <CursorFollower v-if="!bare" />
    <IntroOverlay v-if="showIntro" @done="finishIntro" />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useHead } from '@unhead/vue'
import { business, loadShopInfo } from '@/config/business'
import AnnouncementBar from '@/components/layout/AnnouncementBar.vue'
import { SHARE_IMAGE, bakeryJsonLd, usePageMeta } from '@/seo'
import Navbar from '@/components/layout/Navbar.vue'
import Footer from '@/components/layout/Footer.vue'
import Toast from '@/components/common/Toast.vue'
import AmbientBackground from '@/components/layout/AmbientBackground.vue'
import CursorFollower from '@/components/layout/CursorFollower.vue'
import IntroOverlay from '@/components/layout/IntroOverlay.vue'
import { gsap, ScrollTrigger, initSmoothScroll, scrollToTop, prefersReducedMotion, markIntroDone } from '@/motion'

const route = useRoute()
// Switching language remounts the page so split headlines rebuild with the new text.
const { locale } = useI18n()
// The admin area has its own layout and navigation.
const isAdmin = computed(() => route.matched.some(record => record.meta.requiresAdmin))
// Admin and the in-shop menu board show without the shop's navigation.
const bare = computed(() => isAdmin.value || Boolean(route.meta.bare))

// The intro plays once per browser, on storefront pages, with motion allowed.
const INTRO_KEY = 'intro-seen'
const introSeen = () => { try { return localStorage.getItem(INTRO_KEY) === '1' } catch { return true } }
const showIntro = ref(!prefersReducedMotion() && !introSeen() && !/^\/(admin|menu-board|tv)/.test(window.location.pathname))
// Hours, address and the shop notice as saved in the admin.
loadShopInfo()
function finishIntro() {
  showIntro.value = false
  try { localStorage.setItem(INTRO_KEY, '1') } catch { /* ignore */ }
  markIntroDone()
}
if (!showIntro.value) markIntroDone()
// Never let entrance animations wait forever.
setTimeout(markIntroDone, 6000)

// Default title, description and share preview for every page; pages with
// their own content (products, posts, categories) refine it.
const { t, te } = useI18n()
const place = computed(() => ({ street: business.street, city: business.city }))
const PRIVATE = ['menu-board', 'tv', 'cart', 'checkout', 'order-detail', 'profile', 'orders', 'settings', 'login', 'register',
  'forgot-password', 'reset-password', 'newsletter-unsubscribe', 'wishlist', 'compare', 'not-found']
useHead(() => ({
  htmlAttrs: { lang: locale.value, dir: locale.value === 'ar' ? 'rtl' : 'ltr' },
  titleTemplate: (title) => (title ? `${title} · ${business.name}` : `${business.name} · ${t('seo.tagline', place.value)}`)
}))
usePageMeta(() => {
  const name = String(route.name || '')
  const key = `seo.descriptions.${name}`
  return {
    title: route.name === 'home' ? '' : (te(`seo.titles.${name}`) ? t(`seo.titles.${name}`) : route.meta.title),
    description: te(key) ? t(key, place.value) : t('seo.defaultDescription', place.value),
    image: SHARE_IMAGE,
    type: 'website',
    path: route.path,
    noindex: isAdmin.value || PRIVATE.includes(name),
    jsonLd: bakeryJsonLd()
  }
})

// Page transitions: the old page lifts away, the new one settles in.
// With reduced motion there is no animation, but finishing on the next
// frame (not synchronously) keeps back-to-back navigations safe.
const nextFrame = (done) => requestAnimationFrame(() => done())

const onLeave = (el, done) => {
  if (prefersReducedMotion()) return nextFrame(done)
  gsap.to(el, { opacity: 0, y: -16, duration: 0.3, ease: 'power2.in', onComplete: done })
}

const onEnter = (el, done) => {
  scrollToTop()
  if (prefersReducedMotion()) {
    ScrollTrigger.refresh()
    return nextFrame(done)
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
  inset-inline-start: 0.75rem;
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