<template>
  <div class="admin-shell">
    <!-- Sidebar -->
    <aside class="admin-side" :class="{ 'is-open': drawerOpen }" :aria-label="$t('admin.layout.sidebar')">
      <router-link to="/admin" class="admin-brand">
        <span><em>{{ business.name.charAt(0) }}</em>{{ business.name.slice(1) }}</span>
        <small>Studio</small>
      </router-link>

      <nav class="admin-nav">
        <p class="admin-nav-label">{{ $t('admin.layout.manage') }}</p>
        <router-link v-for="item in navItems" :key="item.path" :to="item.path" class="admin-link"
                     :class="{ 'is-active': isActive(item) }" @click="drawerOpen = false">
          <font-awesome-icon :icon="item.icon" class="w-4" />
          <span>{{ $t(`admin.nav.${item.key}`) }}</span>
        </router-link>
      </nav>

      <div class="admin-side-foot">
        <button type="button" class="admin-link" :lang="otherLocale.code" @click="toggleLocale">
          <font-awesome-icon icon="globe" class="w-4" /> <span>{{ otherLocale.label }}</span>
        </button>
        <router-link to="/" class="admin-link">
          <font-awesome-icon icon="store" class="w-4" /> <span>{{ $t('admin.layout.viewShop') }}</span>
        </router-link>
        <div class="admin-user">
          <span class="admin-avatar">{{ initials }}</span>
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm text-cream">{{ displayName }}</p>
            <p class="truncate text-xs text-cream-faint">{{ authStore.user?.email }}</p>
          </div>
          <button type="button" class="admin-icon-btn" :aria-label="$t('admin.layout.signOut')" :title="$t('admin.layout.signOut')" @click="handleLogout">
            <font-awesome-icon icon="right-from-bracket" />
          </button>
        </div>
      </div>
    </aside>
    <div v-if="drawerOpen" class="admin-scrim" @click="drawerOpen = false"></div>

    <!-- Main -->
    <div class="admin-main">
      <header class="admin-top">
        <button type="button" class="admin-icon-btn lg:hidden" :aria-label="$t('admin.layout.openMenu')" @click="drawerOpen = true">
          <font-awesome-icon icon="bars" />
        </button>
        <div class="min-w-0">
          <p class="admin-crumb">{{ business.name }} Studio</p>
          <h1 class="admin-title">{{ currentPageTitle }}</h1>
        </div>
        <p class="admin-date">{{ today }}</p>
      </header>

      <main class="admin-content">
        <router-view v-slot="{ Component }">
          <transition name="admin-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useI18n } from 'vue-i18n'
import { business } from '@/config/business'
import { LOCALES, intlLocale, setLocale } from '@/i18n'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const drawerOpen = ref(false)
const { t, te, locale } = useI18n()

const navItems = [
  { key: 'dashboard', path: '/admin', icon: 'chart-pie' },
  { key: 'products', path: '/admin/products', icon: 'box-open' },
  { key: 'categories', path: '/admin/categories', icon: 'layer-group' },
  { key: 'orders', path: '/admin/orders', icon: 'receipt' },
  { key: 'users', path: '/admin/users', icon: 'users' }
]

const today = computed(() => {
  // Reading locale.value keeps the date in step with the chosen language.
  void locale.value
  return new Intl.DateTimeFormat(intlLocale(), { weekday: 'long', day: 'numeric', month: 'long' }).format(new Date())
})

const otherLocale = computed(() => LOCALES.find(l => l.code !== locale.value))
const toggleLocale = () => setLocale(otherLocale.value.code)

const displayName = computed(() => {
  const user = authStore.user || {}
  return [user.first_name, user.last_name].filter(Boolean).join(' ') || 'Admin'
})
const initials = computed(() => {
  const user = authStore.user || {}
  return (`${user.first_name?.[0] || ''}${user.last_name?.[0] || ''}` || user.email?.[0] || 'A').toUpperCase()
})

onMounted(() => {
  if (!authStore.isAdmin) router.push({ name: 'products' })
})

// '/admin' must only be active on the dashboard itself, not on every admin page.
const isActive = (item) => (item.path === '/admin' ? route.path === '/admin' : route.path.startsWith(item.path))

const currentPageTitle = computed(() => {
  const key = `admin.titles.${String(route.name)}`
  return te(key) ? t(key) : (route.meta.title || t('admin.titles.admin-dashboard'))
})

watch(() => route.fullPath, () => { drawerOpen.value = false })

const handleLogout = async () => {
  try {
    await authStore.logout()
  } finally {
    router.push('/login')
  }
}
</script>

<style>
/* Admin theme: the storefront palette on working surfaces. Unscoped so it
   also reaches modals and tables rendered by the admin pages. */
.admin-shell {
  min-height: 100vh;
  background:
    radial-gradient(60% 40% at 100% 0%, rgba(230, 161, 90, 0.06), transparent 70%),
    #0e0c0a;
  color: #f4ece1;
}

.admin-shell input:not([type='checkbox']):not([type='radio']):not([type='file']),
.admin-shell select,
.admin-shell textarea {
  background-color: rgba(244, 236, 225, 0.04);
  border-color: rgba(244, 236, 225, 0.12);
  color: #f4ece1;
  border-radius: 0.75rem;
}

.admin-shell input::placeholder,
.admin-shell textarea::placeholder {
  color: #7d7061;
}

.admin-shell select option {
  background: #1e1914;
}

.admin-shell input:focus,
.admin-shell select:focus,
.admin-shell textarea:focus {
  outline: none;
  border-color: #e6a15a;
  box-shadow: 0 0 0 3px rgba(230, 161, 90, 0.2);
}

.admin-shell input[type='file'] {
  color: #b9ab98;
}

.admin-shell input[type='file']::file-selector-button {
  margin-right: 0.75rem;
  padding: 0.45rem 0.9rem;
  border: 0;
  border-radius: 9999px;
  background: rgba(244, 236, 225, 0.08);
  color: #f4ece1;
  cursor: pointer;
}

.admin-shell table,
.admin-shell th,
.admin-shell td {
  background-color: transparent;
  border-color: rgba(244, 236, 225, 0.08);
}

.admin-shell tbody tr {
  transition: background 0.2s;
}

.admin-shell tbody tr:hover {
  background: rgba(244, 236, 225, 0.03);
}

.admin-shell h2,
.admin-shell h3 {
  font-weight: 600;
}

/* Page panels */
.admin-shell .admin-panel {
  border-radius: 1.5rem;
  border: 1px solid rgba(244, 236, 225, 0.08);
  background: linear-gradient(180deg, rgba(30, 25, 20, 0.9), rgba(21, 18, 15, 0.9));
}

.admin-fade-enter-active,
.admin-fade-leave-active {
  transition: opacity 0.2s, transform 0.3s var(--ease-out-expo);
}

.admin-fade-enter-from,
.admin-fade-leave-to {
  opacity: 0;
  transform: translateY(6px);
}
</style>

<style scoped>
.admin-side {
  position: fixed;
  inset: 0 auto 0 0;
  z-index: 40;
  display: flex;
  flex-direction: column;
  width: 16.5rem;
  padding: 1.5rem 1rem;
  background: #15120f;
  border-right: 1px solid rgba(244, 236, 225, 0.07);
  transition: transform 0.5s var(--ease-out-expo);
}

@media (max-width: 1023px) {
  .admin-side {
    transform: translateX(-100%);
  }

  .admin-side.is-open {
    transform: none;
    box-shadow: 30px 0 60px rgba(0, 0, 0, 0.6);
  }
}

.admin-scrim {
  position: fixed;
  inset: 0;
  z-index: 30;
  background: rgba(14, 12, 10, 0.6);
  backdrop-filter: blur(4px);
}

.admin-brand {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0 0.75rem 1.75rem;
  font-family: 'Instrument Serif', Georgia, serif;
  font-size: 1.9rem;
  line-height: 1;
  color: #f4ece1;
}

.admin-brand em {
  color: #e6a15a;
}

.admin-brand small {
  padding: 0.2rem 0.55rem;
  border-radius: 9999px;
  font-family: 'Manrope Variable', system-ui, sans-serif;
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #0e0c0a;
  background: #e6a15a;
}

.admin-nav {
  display: grid;
  gap: 0.2rem;
}

.admin-nav-label {
  padding: 0 0.75rem 0.5rem;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #7d7061;
}

.admin-link {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.65rem 0.75rem;
  border-radius: 0.9rem;
  font-size: 0.92rem;
  font-weight: 500;
  color: #b9ab98;
  transition: background 0.25s, color 0.25s;
}

button.admin-link {
  width: 100%;
  text-align: left;
}

.admin-link:hover {
  color: #f4ece1;
  background: rgba(244, 236, 225, 0.05);
}

.admin-link.is-active {
  color: #0e0c0a;
  background: #e6a15a;
  font-weight: 700;
}

.admin-side-foot {
  display: grid;
  gap: 0.75rem;
  margin-top: auto;
}

.admin-user {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding: 0.75rem;
  border-radius: 1rem;
  background: rgba(244, 236, 225, 0.04);
  border: 1px solid rgba(244, 236, 225, 0.07);
}

.admin-avatar {
  display: grid;
  place-items: center;
  flex-shrink: 0;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 9999px;
  font-size: 0.8rem;
  font-weight: 800;
  color: #0e0c0a;
  background: linear-gradient(135deg, #f2c48d, #d2603f);
}

.admin-icon-btn {
  display: grid;
  place-items: center;
  flex-shrink: 0;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 9999px;
  color: #b9ab98;
  transition: background 0.25s, color 0.25s;
}

@media (min-width: 1024px) {
  .admin-icon-btn.lg\:hidden {
    display: none;
  }
}

.admin-icon-btn:hover {
  color: #f4ece1;
  background: rgba(244, 236, 225, 0.08);
}

.admin-main {
  min-width: 0;
}

@media (min-width: 1024px) {
  .admin-main {
    padding-left: 16.5rem;
  }
}

.admin-top {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.1rem 1.25rem;
  background: rgba(14, 12, 10, 0.8);
  border-bottom: 1px solid rgba(244, 236, 225, 0.06);
  backdrop-filter: blur(16px);
}

@media (min-width: 768px) {
  .admin-top {
    padding: 1.25rem 2.5rem;
  }
}

.admin-crumb {
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #e6a15a;
}

.admin-title {
  margin-top: 0.15rem;
  font-family: 'Instrument Serif', Georgia, serif;
  font-size: 2.1rem;
  font-weight: 400;
  line-height: 1;
  color: #f4ece1;
}

.admin-date {
  display: none;
  margin-left: auto;
  font-size: 0.85rem;
  color: #7d7061;
}

@media (min-width: 768px) {
  .admin-date {
    display: block;
  }
}

.admin-content {
  padding: 1.5rem 1.25rem 4rem;
}

@media (min-width: 768px) {
  .admin-content {
    padding: 2rem 2.5rem 4rem;
  }
}
</style>
