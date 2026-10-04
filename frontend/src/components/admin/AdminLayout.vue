<template>
  <div class="admin-shell">
    <!-- Sidebar -->
    <aside class="admin-side" :class="{ 'is-open': drawerOpen }" :aria-label="$t('admin.layout.sidebar')">
      <router-link to="/admin" class="admin-brand">
        <span><em>{{ business.name.charAt(0) }}</em>{{ business.name.slice(1) }}</span>
        <small>Studio</small>
      </router-link>

      <nav class="admin-nav">
        <template v-for="group in navGroups" :key="group.key">
          <p class="admin-nav-label">{{ $t(`admin.nav.groups.${group.key}`) }}</p>
          <router-link v-for="item in group.items" :key="item.path" :to="item.path" class="admin-link"
                       :class="{ 'is-active': isActive(item) }" @click="drawerOpen = false">
            <font-awesome-icon :icon="item.icon" class="w-4" />
            <span>{{ $t(`admin.nav.${item.key}`) }}</span>
            <span v-if="item.key === 'orders' && unseen" class="admin-badge" :aria-label="$t('admin.alerts.unseen', { count: unseen })">{{ unseen }}</span>
            <span v-if="item.key === 'messages' && studio.unread_messages" class="admin-badge">{{ studio.unread_messages }}</span>
            <span v-if="item.key === 'screens' && studio.screens" class="admin-dot" :class="{ 'is-on': studio.screens_online }"
                  :title="$t('admin.screens.onlineCount', { n: studio.screens_online, total: studio.screens })"></span>
          </router-link>
        </template>
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
        <button v-if="canNotify" type="button" class="admin-icon-btn admin-bell" :class="{ 'is-on': notificationsOn }"
                :aria-pressed="notificationsOn" :title="$t(notificationsOn ? 'admin.alerts.notificationsOn' : 'admin.alerts.enableNotifications')"
                :aria-label="$t(notificationsOn ? 'admin.alerts.notificationsOn' : 'admin.alerts.enableNotifications')"
                @click="enableOrderNotifications">
          <font-awesome-icon icon="bell" />
        </button>
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
import { LOCALES, i18n, intlLocale, setLocale } from '@/i18n'
import adminMessages from '@/i18n/messages/admin'
import studioMessages from '@/i18n/messages/studio'
import { enableOrderNotifications, markOrdersSeen, useNewOrderAlerts } from '@/composables/useNewOrderAlerts'
import { useStudioSummary } from '@/composables/useStudioSummary'

// Admin texts ship with the admin chunk, not with the storefront.
for (const source of [adminMessages, studioMessages]) {
  for (const [lang, messages] of Object.entries(source)) {
    i18n.global.mergeLocaleMessage(lang, { admin: messages })
  }
}

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const drawerOpen = ref(false)
const { t, te, locale } = useI18n()
const { unseen, notificationsOn, setTitle } = useNewOrderAlerts()
const canNotify = typeof Notification !== 'undefined'

const navGroups = [
  { key: 'sales', items: [
    { key: 'dashboard', path: '/admin', icon: 'chart-pie' },
    { key: 'orders', path: '/admin/orders', icon: 'receipt' }
  ] },
  { key: 'catalog', items: [
    { key: 'products', path: '/admin/products', icon: 'box-open' },
    { key: 'categories', path: '/admin/categories', icon: 'layer-group' },
    { key: 'ingredients', path: '/admin/ingredients', icon: 'wheat-awn' }
  ] },
  { key: 'content', items: [
    { key: 'journal', path: '/admin/journal', icon: 'newspaper' },
    { key: 'messages', path: '/admin/messages', icon: 'inbox' },
    { key: 'newsletter', path: '/admin/newsletter', icon: 'paper-plane' }
  ] },
  { key: 'shop', items: [
    { key: 'screens', path: '/admin/screens', icon: 'tv' },
    { key: 'settings', path: '/admin/settings', icon: 'gear' },
    { key: 'users', path: '/admin/users', icon: 'users' }
  ] }
]
const { studio, refreshStudio } = useStudioSummary()

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

watch(() => route.fullPath, () => { drawerOpen.value = false; refreshStudio() })
// Opening the orders page counts as having seen the new orders.
watch([() => route.path, unseen], ([path]) => {
  if (path.startsWith('/admin/orders') && unseen.value) {
    markOrdersSeen()
    setTitle()
  }
}, { immediate: true })

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

.admin-badge {
  margin-left: auto;
  min-width: 1.35rem;
  padding: 0 0.4rem;
  border-radius: 9999px;
  font-size: 0.7rem;
  font-weight: 700;
  line-height: 1.35rem;
  text-align: center;
  color: #0e0c0a;
  background: #e6a15a;
  animation: admin-badge-pop 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes admin-badge-pop {
  from { transform: scale(0.4); opacity: 0; }
}
.admin-dot {
  margin-left: auto;
  width: 0.55rem;
  height: 0.55rem;
  border-radius: 50%;
  background: #7d7061;
}
.admin-dot.is-on {
  background: #9fd49a;
  box-shadow: 0 0 0 3px rgba(159, 212, 154, 0.2);
}

/* Shared building blocks for the Studio pages */
.st-page { display: grid; gap: 1.5rem; }
.st-bar { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 0.75rem 1rem; }
.st-intro { max-width: 46rem; font-size: 0.9rem; line-height: 1.6; color: #b9ab98; }
.st-card { border-radius: 1.5rem; border: 1px solid rgba(244, 236, 225, 0.08);
  background: linear-gradient(180deg, rgba(30, 25, 20, 0.9), rgba(21, 18, 15, 0.9)); padding: 1.5rem; }
.st-card-title { margin-bottom: 1rem; font-size: 1.05rem; font-weight: 600; color: #f4ece1; }
.st-card-title small { display: block; margin-top: 0.2rem; font-size: 0.8rem; font-weight: 400; color: #85766a; }
.st-btn { display: inline-flex; align-items: center; justify-content: center; gap: 0.5rem; padding: 0.55rem 1.15rem;
  border-radius: 9999px; font-size: 0.875rem; font-weight: 600; color: #0e0c0a; background: #e6a15a;
  transition: background 0.2s, opacity 0.2s, transform 0.2s; white-space: nowrap; }
.st-btn:hover { background: #f2c48d; }
.st-btn:active { transform: scale(0.98); }
.st-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.st-btn-ghost { color: #f4ece1; background: rgba(244, 236, 225, 0.07); }
.st-btn-ghost:hover { background: rgba(244, 236, 225, 0.12); }
.st-btn-danger { color: #f6b8a8; background: rgba(240, 143, 121, 0.12); }
.st-btn-danger:hover { background: rgba(240, 143, 121, 0.22); }
.st-btn-sm { padding: 0.35rem 0.8rem; font-size: 0.8rem; }
.st-link { color: #e6a15a; font-weight: 600; }
.st-link:hover { color: #f2c48d; text-decoration: underline; }
.st-label { display: block; margin-bottom: 0.35rem; font-size: 0.8rem; font-weight: 600; color: rgba(244, 236, 225, 0.82); }
.st-label small { font-weight: 400; color: #85766a; }
.st-input { display: block; width: 100%; padding: 0.6rem 0.8rem; font-size: 0.9rem; border-width: 1px; }
textarea.st-input { line-height: 1.6; resize: vertical; }
.st-hint { margin-top: 0.3rem; font-size: 0.75rem; line-height: 1.5; color: #85766a; }
.st-error { margin-top: 0.3rem; font-size: 0.8rem; color: #f6b8a8; }
.st-alert { padding: 0.75rem 1rem; border-radius: 1rem; font-size: 0.875rem; color: #f6b8a8; background: rgba(240, 143, 121, 0.1); }
.st-success { padding: 0.75rem 1rem; border-radius: 1rem; font-size: 0.875rem; color: #c7e6c2; background: rgba(159, 212, 154, 0.1); }
.st-grid { display: grid; gap: 1rem; }
@media (min-width: 640px) { .st-grid-2 { grid-template-columns: 1fr 1fr; } .st-grid-3 { grid-template-columns: repeat(3, 1fr); } }
.st-span { grid-column: 1 / -1; }
.st-chip { display: inline-flex; align-items: center; gap: 0.35rem; padding: 0.15rem 0.6rem; border-radius: 9999px;
  font-size: 0.72rem; font-weight: 600; color: #b9ab98; background: rgba(244, 236, 225, 0.06); white-space: nowrap; }
.st-chip.is-green { color: #b8e3b2; background: rgba(159, 212, 154, 0.12); }
.st-chip.is-amber { color: #f2c48d; background: rgba(230, 161, 90, 0.14); }
.st-chip.is-blue { color: #a9c7f0; background: rgba(120, 160, 230, 0.14); }
.st-chip.is-red { color: #f6b8a8; background: rgba(240, 143, 121, 0.12); }
.st-tabs { display: inline-flex; flex-wrap: wrap; gap: 0.25rem; padding: 0.25rem; border-radius: 9999px; background: rgba(244, 236, 225, 0.05); }
.st-tab { padding: 0.4rem 0.95rem; border-radius: 9999px; font-size: 0.85rem; font-weight: 600; color: #b9ab98; transition: background 0.2s, color 0.2s; }
.st-tab:hover { color: #f4ece1; }
.st-tab.is-active { color: #0e0c0a; background: #f4ece1; }
.st-tab .st-count { margin-left: 0.35rem; font-size: 0.72rem; opacity: 0.7; }
.st-table { width: 100%; border-collapse: collapse; }
.st-table th { padding: 0.75rem 1rem; text-align: left; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.06em;
  text-transform: uppercase; color: #85766a; background: rgba(244, 236, 225, 0.03); border-bottom: 1px solid rgba(244, 236, 225, 0.08); }
.st-table td { padding: 0.8rem 1rem; font-size: 0.875rem; color: rgba(244, 236, 225, 0.82); border-bottom: 1px solid rgba(244, 236, 225, 0.06); vertical-align: middle; }
.st-table tr:last-child td { border-bottom: 0; }
.st-table .is-right { text-align: right; }
.st-empty { padding: 3rem 1rem; text-align: center; font-size: 0.9rem; color: #85766a; }
.st-switch { display: inline-flex; align-items: center; gap: 0.65rem; font-size: 0.875rem; color: rgba(244, 236, 225, 0.85); cursor: pointer; }
.st-switch input { position: absolute; opacity: 0; width: 1px; height: 1px; }
.st-switch i { position: relative; flex: none; width: 2.4rem; height: 1.4rem; border-radius: 9999px; background: rgba(244, 236, 225, 0.15); transition: background 0.2s; }
.st-switch i::after { content: ''; position: absolute; top: 0.2rem; left: 0.2rem; width: 1rem; height: 1rem; border-radius: 50%; background: #f4ece1; transition: transform 0.25s var(--ease-out-expo); }
.st-switch input:checked + i { background: #e6a15a; }
.st-switch input:checked + i::after { transform: translateX(1rem); }
.st-switch input:focus-visible + i { box-shadow: 0 0 0 3px rgba(230, 161, 90, 0.35); }
.st-savebar { position: sticky; bottom: 1rem; z-index: 5; display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 0.75rem;
  padding: 0.75rem 0.75rem 0.75rem 1.25rem; border-radius: 9999px; background: rgba(30, 25, 20, 0.96); border: 1px solid rgba(230, 161, 90, 0.3);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.45); backdrop-filter: blur(8px); }
.st-savebar p { font-size: 0.85rem; color: #b9ab98; }
.st-modal { position: fixed; inset: 0; z-index: 60; display: grid; place-items: center; padding: 1rem; background: rgba(14, 12, 10, 0.7); backdrop-filter: blur(4px); }
.st-modal-box { width: 100%; max-width: 32rem; max-height: calc(100vh - 2rem); overflow-y: auto; }
.st-thumb { width: 3rem; height: 3rem; border-radius: 0.75rem; object-fit: cover; background: rgba(244, 236, 225, 0.05); }

.admin-icon-btn.is-on {
  color: #e6a15a;
}

/* Pushed right on its own while the date is hidden (small screens). */
.admin-bell {
  margin-left: auto;
}

.admin-date + .admin-bell {
  margin-left: 0;
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
  overflow-y: auto;
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
  gap: 0.15rem;
  margin-top: -0.9rem;
}

.admin-nav-label {
  padding: 0.9rem 0.75rem 0.4rem;
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
