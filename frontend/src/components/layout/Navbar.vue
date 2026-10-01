<template>
  <header class="nav-wrap" :class="{ 'is-scrolled': scrolled, 'is-hidden': hidden && !menuOpen && !searchOpen }">
    <nav class="nav" :aria-label="$t('nav.main')">
      <router-link to="/" class="nav-logo" :aria-label="$t('nav.home', { name: business.name })">
        <span class="nav-logo-mark">{{ business.name.charAt(0) }}</span>{{ business.name.slice(1) }}
      </router-link>

      <ul class="nav-links">
        <li v-for="link in links" :key="link.to">
          <router-link :to="link.to" class="nav-link" :class="{ 'is-active': isActive(link.to) }">
            {{ $t(link.label) }}
          </router-link>
        </li>
      </ul>

      <div class="nav-tools">
        <button type="button" class="nav-lang" :aria-label="$t('nav.switchLanguage')" @click="toggleLocale">
          {{ otherLocale.short }}
        </button>
        <button type="button" class="nav-icon" :aria-label="$t('nav.search')" @click="openSearch">
          <font-awesome-icon icon="search" />
        </button>
        <router-link to="/wishlist" class="nav-icon hidden sm:grid" :aria-label="$t('nav.wishlist')">
          <font-awesome-icon icon="heart" />
          <span v-if="wishlistStore.items.length" class="nav-badge">{{ wishlistStore.items.length }}</span>
        </router-link>
        <router-link v-if="compareStore.items.length" to="/compare" class="nav-icon hidden sm:grid" :aria-label="$t('nav.compare')">
          <font-awesome-icon icon="code-compare" />
          <span class="nav-badge">{{ compareStore.items.length }}</span>
        </router-link>

        <!-- Account -->
        <div v-if="authStore.isAuthenticated" class="relative hidden md:block" @keydown.escape="userMenuOpen = false">
          <button type="button" class="nav-icon" :aria-expanded="userMenuOpen" aria-haspopup="true"
                  :aria-label="$t('nav.accountMenu')" @click="userMenuOpen = !userMenuOpen">
            <span class="nav-avatar">{{ initials }}</span>
          </button>
          <transition name="pop">
            <div v-if="userMenuOpen" class="nav-pop w-56" role="menu">
              <p class="px-3 pb-2 text-xs text-cream-faint truncate">{{ authStore.user?.email }}</p>
              <router-link v-if="authStore.isAdmin" to="/admin" class="nav-pop-item" role="menuitem" @click="userMenuOpen = false">{{ $t('nav.admin') }}</router-link>
              <router-link to="/profile" class="nav-pop-item" role="menuitem" @click="userMenuOpen = false">{{ $t('nav.profile') }}</router-link>
              <router-link to="/orders" class="nav-pop-item" role="menuitem" @click="userMenuOpen = false">{{ $t('nav.orders') }}</router-link>
              <router-link to="/settings" class="nav-pop-item" role="menuitem" @click="userMenuOpen = false">{{ $t('nav.settings') }}</router-link>
              <button type="button" class="nav-pop-item w-full text-left" role="menuitem" @click="logout">{{ $t('nav.signOut') }}</button>
            </div>
          </transition>
        </div>
        <router-link v-else to="/login" class="nav-signin hidden md:inline-flex">{{ $t('nav.signIn') }}</router-link>

        <!-- Cart -->
        <div class="relative" @mouseenter="cartPreview = true" @mouseleave="cartPreview = false">
          <router-link id="nav-cart" to="/cart" class="nav-cart" :aria-label="$t('nav.cartLabel', { count: cartStore.itemCount })">
            <font-awesome-icon icon="shopping-bag" />
            <span class="tabular-nums">{{ cartStore.itemCount }}</span>
          </router-link>
          <transition name="pop">
            <div v-if="cartPreview && cartStore.items.length" class="nav-pop w-80 hidden md:block">
              <ul class="max-h-72 overflow-auto">
                <li v-for="item in cartStore.items.slice(0, 4)" :key="item.product.id" class="flex items-center gap-3 p-2">
                  <img :src="item.product.image_url || item.product.image || PLACEHOLDER_IMAGE" alt="" class="h-12 w-12 object-contain" @error="applyImageFallback" />
                  <div class="min-w-0 flex-1">
                    <p class="truncate text-sm text-cream">{{ item.product.name }}</p>
                    <p class="text-xs text-cream-faint">{{ item.quantity }} × {{ formatEuro(item.product.price) }}</p>
                  </div>
                </li>
              </ul>
              <p v-if="cartStore.items.length > 4" class="px-2 pb-2 text-xs text-cream-faint">{{ $t('nav.more', { count: cartStore.items.length - 4 }) }}</p>
              <div class="mt-2 flex items-center justify-between border-t border-white/10 px-2 pt-3">
                <span class="text-sm text-cream-muted">{{ $t('common.total') }}</span>
                <span class="font-semibold text-crust-light">{{ formatEuro(cartStore.totalAmount) }}</span>
              </div>
              <router-link to="/cart" class="btn-amber mt-3 w-full !py-2.5" @click="cartPreview = false">{{ $t('nav.viewCart') }}</router-link>
            </div>
          </transition>
        </div>

        <button type="button" class="nav-burger md:hidden" :aria-expanded="menuOpen" aria-controls="mobile-menu"
                :aria-label="menuOpen ? $t('nav.closeMenu') : $t('nav.openMenu')" @click="toggleMenu">
          <span></span><span></span>
        </button>
      </div>
    </nav>

    <!-- Mobile menu -->
    <div v-show="menuOpen" id="mobile-menu" ref="menuEl" class="mobile-menu" @keydown.escape="closeMenu">
      <ul class="mobile-links">
        <li v-for="(link, index) in mobileLinks" :key="link.to" class="overflow-hidden">
          <router-link :to="link.to" class="mobile-link" @click="closeMenu">
            <span class="mobile-index">0{{ index + 1 }}</span>{{ $t(link.label) }}
          </router-link>
        </li>
      </ul>
      <div class="mobile-foot">
        <template v-if="authStore.isAuthenticated">
          <router-link v-if="authStore.isAdmin" to="/admin" @click="closeMenu">{{ $t('nav.admin') }}</router-link>
          <router-link to="/profile" @click="closeMenu">{{ $t('nav.profile') }}</router-link>
          <router-link to="/orders" @click="closeMenu">{{ $t('nav.orders') }}</router-link>
          <button type="button" @click="logout">{{ $t('nav.signOut') }}</button>
        </template>
        <template v-else>
          <router-link to="/login" @click="closeMenu">{{ $t('nav.signIn') }}</router-link>
          <router-link to="/register" @click="closeMenu">{{ $t('nav.createAccount') }}</router-link>
        </template>
        <button type="button" @click="toggleLocale">{{ otherLocale.label }}</button>
        <p class="mt-4 w-full text-cream-faint">{{ business.street }}, {{ business.city }}<span v-if="business.transit"> · {{ business.transit }}</span></p>
      </div>
    </div>

    <!-- Search -->
    <transition name="search">
      <div v-if="searchOpen" class="search-layer" role="dialog" :aria-label="$t('nav.searchProducts')" @click.self="searchOpen = false"
           @keydown.escape="searchOpen = false">
        <form class="search-box" role="search" @submit.prevent="submitSearch">
          <font-awesome-icon icon="search" class="text-crust text-xl" />
          <input ref="searchInput" v-model="searchQuery" type="search" :placeholder="$t('nav.searchPlaceholder')"
                 :aria-label="$t('nav.searchProducts')" />
          <button type="button" class="text-cream-faint hover:text-cream text-sm" @click="searchOpen = false">Esc</button>
        </form>
        <div class="search-hints">
          <span class="text-cream-faint">{{ $t('nav.popular') }}</span>
          <button v-for="hint in searchHints" :key="hint" type="button" @click="searchQuery = hint; submitSearch()">
            {{ hint }}
          </button>
        </div>
      </div>
    </transition>
  </header>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cartStore'
import { useAuthStore } from '@/stores/authStore'
import { useWishlistStore } from '@/stores/wishlistStore'
import { useCompareStore } from '@/stores/compareStore'
import { business } from '@/config/business'
import { formatEuro } from '@/utils/money'
import { PLACEHOLDER_IMAGE, applyImageFallback } from '@/utils/imageFallback'
import { gsap, lockScroll, prefersReducedMotion } from '@/motion'
import { useI18n } from 'vue-i18n'
import { LOCALES, setLocale } from '@/i18n'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()
const authStore = useAuthStore()
const wishlistStore = useWishlistStore()
const compareStore = useCompareStore()

const links = [
  { label: 'nav.shop', to: '/products' },
  { label: 'nav.seasonal', to: '/seasonal' },
  { label: 'nav.journal', to: '/blog' },
  { label: 'nav.about', to: '/about' },
  { label: 'nav.contact', to: '/contact' }
]
const mobileLinks = [{ label: 'nav.homeLink', to: '/' }, ...links]

const { locale, t } = useI18n()
const searchHints = computed(() => t('nav.hints').split(','))
const otherLocale = computed(() => LOCALES.find(l => l.code !== locale.value))
const toggleLocale = () => setLocale(otherLocale.value.code)

const scrolled = ref(false)
const hidden = ref(false)
const menuOpen = ref(false)
const menuEl = ref(null)
const searchOpen = ref(false)
const searchInput = ref(null)
const searchQuery = ref('')
const userMenuOpen = ref(false)
const cartPreview = ref(false)

const initials = computed(() => {
  const user = authStore.user || {}
  const letters = `${user.first_name?.[0] || ''}${user.last_name?.[0] || ''}`
  return (letters || user.email?.[0] || 'U').toUpperCase()
})

const isActive = (path) => route.path === path || route.path.startsWith(`${path}/`)

// Hide the bar while scrolling down, bring it back when scrolling up.
let lastY = 0
function onScroll() {
  const y = window.scrollY
  scrolled.value = y > 24
  hidden.value = y > 320 && y > lastY
  lastY = y
}

function toggleMenu() {
  menuOpen.value ? closeMenu() : openMenu()
}

async function openMenu() {
  menuOpen.value = true
  lockScroll(true)
  await nextTick()
  if (prefersReducedMotion()) return
  gsap.fromTo(menuEl.value, { clipPath: 'inset(0 0 100% 0)' }, { clipPath: 'inset(0 0 0% 0)', duration: 0.7, ease: 'expo.out' })
  gsap.fromTo(menuEl.value.querySelectorAll('.mobile-link'), { yPercent: 110 },
    { yPercent: 0, duration: 0.9, ease: 'expo.out', stagger: 0.05, delay: 0.1 })
}

function closeMenu() {
  if (!menuOpen.value) return
  menuOpen.value = false
  lockScroll(false)
}

async function openSearch() {
  searchOpen.value = true
  await nextTick()
  searchInput.value?.focus()
}

function submitSearch() {
  const query = searchQuery.value.trim()
  if (!query) return
  searchOpen.value = false
  router.push({ path: '/products', query: { search: query } })
}

async function logout() {
  userMenuOpen.value = false
  closeMenu()
  try {
    await authStore.logout()
  } finally {
    router.push('/login')
  }
}

const onDocumentClick = (event) => {
  if (userMenuOpen.value && !event.target.closest('[aria-haspopup], .nav-pop')) userMenuOpen.value = false
}
const onKey = (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
    event.preventDefault()
    openSearch()
  }
}

watch(() => route.fullPath, () => {
  closeMenu()
  userMenuOpen.value = false
  cartPreview.value = false
  hidden.value = false
})

onMounted(() => {
  onScroll()
  window.addEventListener('scroll', onScroll, { passive: true })
  document.addEventListener('click', onDocumentClick)
  window.addEventListener('keydown', onKey)
  cartStore.fetchCart({ silent: true })
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', onScroll)
  document.removeEventListener('click', onDocumentClick)
  window.removeEventListener('keydown', onKey)
  lockScroll(false)
})
</script>

<style scoped>
.nav-wrap {
  position: fixed;
  inset: 0 0 auto;
  z-index: 50;
  padding: 0.85rem 1rem 0;
  transition: transform 0.6s var(--ease-out-expo);
}

.nav-wrap.is-hidden {
  transform: translateY(-120%);
}

.nav {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  max-width: 80rem;
  margin: 0 auto;
  padding: 0.55rem 0.6rem 0.55rem 1.4rem;
  border-radius: 9999px;
  border: 1px solid transparent;
  transition: background 0.5s, border-color 0.5s, box-shadow 0.5s;
}

.is-scrolled .nav,
.nav-wrap:has(.mobile-menu:not([style*='none'])) .nav {
  background: rgba(21, 18, 15, 0.72);
  border-color: rgba(244, 236, 225, 0.08);
  box-shadow: 0 20px 40px -24px rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(20px) saturate(1.4);
  -webkit-backdrop-filter: blur(20px) saturate(1.4);
}

.nav-logo {
  font-family: 'Instrument Serif', Georgia, serif;
  font-size: 1.75rem;
  line-height: 1;
  color: #f4ece1;
  letter-spacing: -0.01em;
}

.nav-logo-mark {
  font-style: italic;
  color: #e6a15a;
}

.nav-links {
  display: none;
  gap: 0.25rem;
  margin: 0 auto;
}

@media (min-width: 768px) {
  .nav-links {
    display: flex;
  }
}

.nav-link {
  position: relative;
  display: block;
  padding: 0.5rem 0.9rem;
  border-radius: 9999px;
  font-size: 0.9rem;
  font-weight: 500;
  color: #b9ab98;
  transition: color 0.3s, background 0.3s;
}

.nav-link:hover {
  color: #f4ece1;
  background: rgba(244, 236, 225, 0.05);
}

.nav-link.is-active {
  color: #f4ece1;
}

.nav-link.is-active::after {
  content: '';
  position: absolute;
  left: 50%;
  bottom: 0.2rem;
  width: 0.3rem;
  height: 0.3rem;
  border-radius: 50%;
  background: #e6a15a;
  transform: translateX(-50%);
}

.nav-tools {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  margin-left: auto;
}

@media (min-width: 768px) {
  .nav-tools {
    margin-left: 0;
  }
}

.nav-icon {
  position: relative;
  display: grid;
  place-items: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 9999px;
  color: #d9cfc2;
  transition: background 0.3s, color 0.3s;
}

.nav-icon:hover {
  color: #f4ece1;
  background: rgba(244, 236, 225, 0.07);
}

.nav-avatar {
  display: grid;
  place-items: center;
  width: 2rem;
  height: 2rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 700;
  color: #0e0c0a;
  background: linear-gradient(135deg, #f2c48d, #d2603f);
}

.nav-badge {
  position: absolute;
  top: 0.2rem;
  right: 0.1rem;
  min-width: 1rem;
  height: 1rem;
  padding: 0 0.2rem;
  border-radius: 9999px;
  background: #e6a15a;
  color: #0e0c0a;
  font-size: 0.62rem;
  font-weight: 800;
  line-height: 1rem;
  text-align: center;
}

.nav-signin {
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  font-weight: 500;
  color: #d9cfc2;
}

.nav-signin:hover {
  color: #f4ece1;
}

.nav-cart {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  height: 2.6rem;
  padding: 0 1.1rem;
  border-radius: 9999px;
  font-weight: 700;
  font-size: 0.9rem;
  color: #0e0c0a;
  background: #e6a15a;
  transition: background 0.3s;
}

.nav-cart:hover {
  color: #0e0c0a;
  background: #f2c48d;
}

.nav-pop {
  position: absolute;
  right: 0;
  top: calc(100% + 0.75rem);
  padding: 0.6rem;
  border-radius: 1.25rem;
  background: rgba(21, 18, 15, 0.92);
  border: 1px solid rgba(244, 236, 225, 0.1);
  box-shadow: 0 30px 60px -20px rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(20px);
}

.nav-pop::before {
  /* Keeps the popover open while the pointer crosses the gap. */
  content: '';
  position: absolute;
  inset: -0.8rem 0 auto;
  height: 0.8rem;
}

.nav-pop-item {
  display: block;
  padding: 0.55rem 0.75rem;
  border-radius: 0.75rem;
  font-size: 0.9rem;
  color: #d9cfc2;
}

.nav-pop-item:hover {
  color: #f4ece1;
  background: rgba(244, 236, 225, 0.06);
}

.nav-lang {
  display: grid;
  place-items: center;
  height: 2.5rem;
  padding: 0 0.7rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #d9cfc2;
  transition: background 0.25s, color 0.25s;
}

.nav-lang:hover {
  color: #f4ece1;
  background: rgba(244, 236, 225, 0.07);
}

.nav-burger {
  display: grid;
  place-content: center;
  gap: 0.35rem;
  width: 2.6rem;
  height: 2.6rem;
  border-radius: 9999px;
  background: rgba(244, 236, 225, 0.07);
}

@media (min-width: 768px) {
  .nav-lang {
  display: grid;
  place-items: center;
  height: 2.5rem;
  padding: 0 0.7rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #d9cfc2;
  transition: background 0.25s, color 0.25s;
}

.nav-lang:hover {
  color: #f4ece1;
  background: rgba(244, 236, 225, 0.07);
}

.nav-burger {
    display: none;
  }
}

.nav-burger span {
  display: block;
  width: 1.1rem;
  height: 1.5px;
  background: #f4ece1;
  transition: transform 0.4s var(--ease-out-expo);
}

.nav-burger[aria-expanded='true'] span:first-child {
  transform: translateY(0.2rem) rotate(45deg);
}

.nav-burger[aria-expanded='true'] span:last-child {
  transform: translateY(-0.2rem) rotate(-45deg);
}

.mobile-menu {
  position: fixed;
  inset: 0;
  z-index: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 7rem 1.5rem 2rem;
  background: #0e0c0a;
  overflow-y: auto;
}

.mobile-link {
  display: flex;
  align-items: baseline;
  gap: 1rem;
  font-family: 'Instrument Serif', Georgia, serif;
  font-size: clamp(2.8rem, 12vw, 4.5rem);
  line-height: 1.1;
  color: #f4ece1;
}

.mobile-index {
  font-family: 'Manrope Variable', system-ui, sans-serif;
  font-size: 0.75rem;
  color: #e6a15a;
}

.mobile-foot {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1.5rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(244, 236, 225, 0.1);
  font-size: 0.95rem;
}

.mobile-foot a,
.mobile-foot button {
  color: #d9cfc2;
}

.search-layer {
  position: fixed;
  inset: 0;
  z-index: 3;
  padding: 6rem 1rem 0;
  background: rgba(14, 12, 10, 0.75);
  backdrop-filter: blur(16px);
}

.search-box {
  display: flex;
  align-items: center;
  gap: 1rem;
  max-width: 48rem;
  margin: 0 auto;
  padding: 1.1rem 1.5rem;
  border-radius: 1.5rem;
  background: #1e1914;
  border: 1px solid rgba(244, 236, 225, 0.12);
  box-shadow: 0 40px 80px -30px rgba(0, 0, 0, 0.9);
}

.search-box input {
  flex: 1;
  min-width: 0;
  border: 0;
  background: transparent;
  font-size: 1.35rem;
  color: #f4ece1;
  outline: none;
}

.search-box input::placeholder {
  color: #7d7061;
}

.search-hints {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  max-width: 48rem;
  margin: 1rem auto 0;
  font-size: 0.85rem;
}

.search-hints button {
  padding: 0.35rem 0.85rem;
  border-radius: 9999px;
  color: #d9cfc2;
  border: 1px solid rgba(244, 236, 225, 0.14);
}

.search-hints button:hover {
  color: #0e0c0a;
  background: #e6a15a;
}

.pop-enter-active,
.pop-leave-active {
  transition: opacity 0.25s, transform 0.35s var(--ease-out-expo);
}

.pop-enter-from,
.pop-leave-to {
  opacity: 0;
  transform: translateY(-6px) scale(0.98);
}

.search-enter-active,
.search-leave-active {
  transition: opacity 0.3s;
}

.search-enter-active .search-box {
  transition: transform 0.6s var(--ease-out-expo);
}

.search-enter-from,
.search-leave-to {
  opacity: 0;
}

.search-enter-from .search-box {
  transform: translateY(-24px);
}
</style>
