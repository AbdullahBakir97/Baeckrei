<template>
  <div class="st-page">
    <div class="st-bar">
      <p class="st-intro">{{ $t('admin.screens.intro') }}</p>
      <button type="button" class="st-btn" :disabled="busy" @click="create"><font-awesome-icon icon="plus" /> {{ $t('admin.screens.new') }}</button>
    </div>
    <p v-if="error" class="st-alert" role="alert">{{ error }}</p>

    <p v-if="loading" class="st-empty">{{ $t('admin.common.loading') }}</p>
    <div v-else-if="!screens.length" class="st-card st-empty">
      <font-awesome-icon icon="tv" class="text-3xl mb-3" /><br>
      {{ $t('admin.screens.empty') }}<br>
      <button type="button" class="st-btn mt-4" @click="create">{{ $t('admin.screens.createFirst') }}</button>
    </div>

    <div v-else class="screen-grid">
      <article v-for="s in screens" :key="s.id" class="st-card !p-0 overflow-hidden screen-card">
        <router-link v-fit :to="`/admin/screens/${s.id}`" class="screen-thumb" :aria-label="$t('admin.common.edit')">
          <iframe :src="`/menu-board/${s.slug}?preview=1`" tabindex="-1" loading="lazy" :title="s.name" aria-hidden="true"></iframe>
        </router-link>
        <div class="p-5 st-grid !gap-3">
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <h2 class="text-lg font-semibold text-cream truncate">{{ s.name }}</h2>
              <p class="text-xs text-cream-faint">{{ $t(`admin.screens.layouts.${s.layout}`) }} · {{ $t(`admin.screens.themes.${s.theme}`) }}
                <template v-if="s.slide_count"> · {{ $t('admin.screens.slideCount', { n: s.slide_count }) }}</template></p>
            </div>
            <span v-if="s.is_default" class="st-chip is-amber">{{ $t('admin.screens.default') }}</span>
          </div>
          <div class="flex items-center justify-between gap-3">
            <span class="st-chip" :class="s.online ? 'is-green' : ''">
              <i class="dot" :class="{ 'is-on': s.online }"></i>{{ seen(s) }}
            </span>
            <span class="screen-code" :title="$t('admin.screens.codeHint')">{{ s.code }}</span>
          </div>
          <div class="flex flex-wrap gap-2">
            <router-link :to="`/admin/screens/${s.id}`" class="st-btn st-btn-sm"><font-awesome-icon icon="palette" /> {{ $t('admin.screens.design') }}</router-link>
            <a :href="`/menu-board/${s.slug}`" target="_blank" rel="noopener" class="st-btn st-btn-ghost st-btn-sm"><font-awesome-icon icon="up-right-from-square" /> {{ $t('admin.screens.open') }}</a>
            <button type="button" class="st-btn st-btn-ghost st-btn-sm" :title="$t('admin.screens.reloadHint')" @click="reload(s)"><font-awesome-icon icon="rotate" /></button>
            <button type="button" class="st-btn st-btn-ghost st-btn-sm" :title="$t('admin.screens.duplicate')" @click="duplicate(s)"><font-awesome-icon icon="copy" /></button>
            <button type="button" class="st-btn st-btn-danger st-btn-sm ms-auto" :title="$t('admin.common.delete')" @click="remove(s)"><font-awesome-icon icon="trash" /></button>
          </div>
        </div>
      </article>
    </div>

    <!-- How to put a screen on a TV -->
    <section class="st-card">
      <h2 class="st-card-title">{{ $t('admin.screens.setupTitle') }} <small>{{ $t('admin.screens.setupHint') }}</small></h2>
      <ol class="setup">
        <li><b>1</b><span>{{ $t('admin.screens.setup1', { url: tvUrl }) }}</span></li>
        <li><b>2</b><span>{{ $t('admin.screens.setup2') }}</span></li>
        <li><b>3</b><span>{{ $t('admin.screens.setup3') }}</span></li>
      </ol>
      <div class="devices">
        <div v-for="d in ['firetv', 'smarttv', 'pi', 'pc']" :key="d" class="device">
          <p class="font-semibold text-cream">{{ $t(`admin.screens.devices.${d}.title`) }}</p>
          <p class="text-sm text-cream-faint">{{ $t(`admin.screens.devices.${d}.text`) }}</p>
        </div>
      </div>
      <p class="st-hint">{{ $t('admin.screens.setupFoot') }}</p>
    </section>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import axios from '@/plugins/axios'
import { intlLocale } from '@/i18n'
import { errorsFrom, listOf } from './api'
import { refreshStudio } from '@/composables/useStudioSummary'

const { t } = useI18n()
const router = useRouter()
const screens = ref([])
const loading = ref(true)
const busy = ref(false)
const error = ref('')
const tvUrl = `${window.location.host}/tv`

// Scale the 1920 × 1080 preview to the card's width.
const vFit = {
  mounted(el) {
    const fit = () => el.style.setProperty('--s', String(el.clientWidth / 1920))
    el._fit = new ResizeObserver(fit)
    el._fit.observe(el)
    fit()
  },
  unmounted(el) { el._fit?.disconnect() }
}

async function load() {
  try {
    screens.value = listOf((await axios.get('/api/studio/menu-screens/')).data)
    error.value = ''
  } catch {
    error.value = t('admin.common.loadError')
  } finally {
    loading.value = false
  }
}
let timer
onMounted(() => { load(); timer = setInterval(load, 30_000) })
onBeforeUnmount(() => clearInterval(timer))

function seen(s) {
  if (s.online) {
    const info = s.last_seen_info || {}
    return info.width ? `${t('admin.screens.online')} · ${info.width}×${info.height}` : t('admin.screens.online')
  }
  if (!s.last_seen_at) return t('admin.screens.never')
  const minutes = Math.round((Date.now() - new Date(s.last_seen_at)) / 60000)
  const rtf = new Intl.RelativeTimeFormat(intlLocale(), { numeric: 'auto' })
  const ago = minutes < 60 ? rtf.format(-minutes, 'minute') : minutes < 1440 ? rtf.format(-Math.round(minutes / 60), 'hour') : rtf.format(-Math.round(minutes / 1440), 'day')
  return t('admin.screens.lastSeen', { ago })
}

async function create() {
  busy.value = true
  try {
    const n = screens.value.length + 1
    const { data } = await axios.post('/api/studio/menu-screens/', {
      name: n === 1 ? t('admin.screens.firstName') : t('admin.screens.newName', { n }), is_default: n === 1
    })
    refreshStudio()
    router.push(`/admin/screens/${data.id}`)
  } catch (err) {
    error.value = errorsFrom(err).message || t('admin.common.saveError')
  } finally {
    busy.value = false
  }
}

async function reload(s) {
  try {
    await axios.post(`/api/studio/menu-screens/${s.id}/reload/`)
    error.value = ''
    window.alert(t('admin.screens.reloadSent', { name: s.name }))
  } catch { error.value = t('admin.common.saveError') }
}

async function duplicate(s) {
  try {
    await axios.post(`/api/studio/menu-screens/${s.id}/duplicate/`)
    await load()
  } catch { error.value = t('admin.common.saveError') }
}

async function remove(s) {
  if (!window.confirm(t('admin.screens.confirmDelete', { name: s.name }))) return
  try {
    await axios.delete(`/api/studio/menu-screens/${s.id}/`)
    screens.value = screens.value.filter(x => x.id !== s.id)
    refreshStudio()
  } catch { error.value = t('admin.common.deleteError') }
}
</script>

<style scoped>
.screen-grid { display: grid; gap: 1.5rem; grid-template-columns: repeat(auto-fill, minmax(19rem, 1fr)); }
.screen-thumb { position: relative; display: block; aspect-ratio: 16 / 9; overflow: hidden; background: #000; border-bottom: 1px solid rgba(244, 236, 225, 0.08); }
.screen-thumb iframe { position: absolute; top: 0; left: 0; width: 1920px; height: 1080px; border: 0; transform-origin: top left; transform: scale(var(--s, 0.2)); pointer-events: none; }
.screen-code { font: 700 1.3rem/1 'Manrope Variable', monospace; letter-spacing: 0.2em; color: #f2c48d; }
.dot { display: inline-block; width: 0.5rem; height: 0.5rem; border-radius: 50%; background: #7d7061; }
.dot.is-on { background: #9fd49a; }
.setup { display: grid; gap: 0.75rem; margin-bottom: 1.25rem; }
@media (min-width: 900px) { .setup { grid-template-columns: repeat(3, 1fr); } }
.setup li { display: flex; gap: 0.8rem; padding: 1rem; border-radius: 1rem; background: rgba(244, 236, 225, 0.04); font-size: 0.9rem; line-height: 1.55; color: #d9cfc2; }
.setup b { flex: none; display: grid; place-items: center; width: 1.8rem; height: 1.8rem; border-radius: 50%; color: #0e0c0a; background: #e6a15a; }
.devices { display: grid; gap: 0.75rem; grid-template-columns: repeat(auto-fit, minmax(14rem, 1fr)); margin-bottom: 0.75rem; }
.device { padding: 1rem; border-radius: 1rem; border: 1px solid rgba(244, 236, 225, 0.08); }
.device p + p { margin-top: 0.35rem; line-height: 1.55; }
</style>
