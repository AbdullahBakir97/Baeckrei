<template>
  <div class="board-viewport" :style="viewportStyle">
    <div ref="boardEl" class="board" :class="boardClass" :style="themeStyle" :lang="lang">
      <div v-if="design.background_image_url" class="board-photo" :style="{ backgroundImage: `url(${design.background_image_url})` }" aria-hidden="true">
        <span :style="{ opacity: (design.background_dim ?? 60) / 100 }"></span>
      </div>

      <!-- Header: brand, headline, opening status, clock -->
      <header class="board-head">
        <div class="board-brand">
          <span class="board-logo"><em>{{ shop.name.charAt(0) }}</em>{{ shop.name.slice(1) }}</span>
          <span class="board-place">{{ headline || shop.address }}</span>
        </div>
        <div class="board-status">
          <span v-if="design.show_status && status" class="board-open" :class="{ 'is-closed': !status.open_now }">
            <i aria-hidden="true"></i>{{ statusText }}
          </span>
          <span v-if="design.show_clock" class="board-clock">{{ clock }}</span>
        </div>
      </header>

      <transition name="swap" mode="out-in">
        <!-- A promotion -->
        <section v-if="item?.type === 'slide'" :key="`s${item.slide.id}-${lang}-${step}`" class="board-slide" :class="`is-${item.slide.style}`">
          <div v-if="item.slide.style === 'photo' && item.slide.image_url" class="slide-photo" :style="{ backgroundImage: `url(${item.slide.image_url})` }"></div>
          <div class="slide-copy">
            <p class="board-eyebrow">{{ tr('special') }}</p>
            <h2 class="slide-title">{{ text(item.slide, 'title') }}</h2>
            <p v-if="text(item.slide, 'text')" class="slide-text">{{ text(item.slide, 'text') }}</p>
            <p v-if="item.slide.price && design.show_prices" class="slide-price">
              {{ price(item.slide.price) }}
              <small v-if="text(item.slide, 'price_note')">{{ text(item.slide, 'price_note') }}</small>
            </p>
          </div>
          <div v-if="item.slide.style === 'product' && item.slide.image_url" class="slide-stage">
            <span class="feature-glow" aria-hidden="true"></span>
            <img :src="item.slide.image_url" alt="" />
          </div>
        </section>

        <!-- Spotlight: one product, large -->
        <section v-else-if="item?.type === 'spot'" :key="`p${item.product.id}-${lang}`" class="board-spot">
          <div class="spot-stage">
            <span class="feature-glow" aria-hidden="true"></span>
            <img v-if="design.show_images && image(item.product)" :src="image(item.product)" alt="" />
          </div>
          <div class="spot-copy">
            <p class="board-eyebrow">{{ categoryTitle(item.product.category) }}</p>
            <h2 class="spot-name">{{ nameOf(item.product) }}</h2>
            <p v-if="design.show_descriptions && descOf(item.product, 200)" class="spot-desc">{{ descOf(item.product, 200) }}</p>
            <p v-if="design.show_tags && tags(item.product).length" class="item-tags">
              <span v-for="tag in tags(item.product)" :key="tag" class="item-tag">{{ tag }}</span>
            </p>
            <p v-if="design.show_prices" class="spot-price">{{ soldOut(item.product) ? tr('soldOut') : price(item.product.price) }}</p>
            <ul v-if="item.others.length" class="spot-others">
              <li v-for="other in item.others" :key="other.id"><span>{{ nameOf(other) }}</span><b v-if="design.show_prices">{{ soldOut(other) ? tr('soldOut') : price(other.price) }}</b></li>
            </ul>
          </div>
        </section>

        <!-- Menu pages -->
        <div v-else :key="`m-${layout}-${item?.page?.key}-${lang}`" class="board-body" :class="`is-${layout}`">
          <!-- Feature column (columns layout) -->
          <aside v-if="layout === 'columns'" class="board-feature">
            <transition name="feature" mode="out-in">
              <div v-if="featured && design.show_images" :key="featured.id" class="feature-card">
                <p class="board-eyebrow">{{ tr('featured') }}</p>
                <div class="feature-stage">
                  <span class="feature-glow" aria-hidden="true"></span>
                  <img :src="image(featured)" :alt="nameOf(featured)" class="feature-img" />
                </div>
                <h2 class="feature-name">{{ nameOf(featured) }}</h2>
                <p v-if="design.show_prices" class="feature-price">{{ price(featured.price) }}</p>
              </div>
            </transition>
            <div v-if="design.show_qr && qr" class="board-qr">
              <img :src="qr" alt="" />
              <div>
                <p class="qr-title">{{ tr('orderAhead') }}</p>
                <p class="qr-text">{{ tr('orderAheadText') }}</p>
                <p class="qr-url">{{ shopHost }}</p>
              </div>
            </div>
          </aside>

          <section ref="menuEl" class="board-menu">
            <span v-if="menuPages.length > 1" class="menu-dots" aria-hidden="true">
              <i v-for="(p, i) in menuPages" :key="p.key" :class="{ 'is-on': p.key === item?.page?.key }"></i>
            </span>

            <!-- Grid of photo cards -->
            <template v-if="layout === 'grid' && item?.page">
              <h1 class="menu-title grid-title">{{ item.page.title }}</h1>
              <ul class="grid-cards" :style="{ '--cols': gridCols }">
                <li v-for="(p, i) in item.page.items" :key="p.id" class="grid-card" :class="{ 'is-sold-out': soldOut(p) }" :style="{ '--i': i }">
                  <span v-if="design.show_images" class="grid-img"><img v-if="image(p)" :src="image(p)" alt="" /></span>
                  <span class="grid-name">{{ nameOf(p) }}</span>
                  <span v-if="design.show_descriptions && descOf(p, 70)" class="grid-desc">{{ descOf(p, 70) }}</span>
                  <span class="grid-foot">
                    <span v-if="design.show_tags" class="item-tags"><span v-for="tag in tags(p)" :key="tag" class="item-tag">{{ tag }}</span></span>
                    <b v-if="design.show_prices" class="grid-price">{{ soldOut(p) ? tr('soldOut') : price(p.price) }}</b>
                  </span>
                </li>
              </ul>
            </template>

            <!-- Columns and list layouts -->
            <div v-else-if="item?.page" class="menu-page" :style="{ '--cols': columns }">
              <div v-for="(column, c) in item.page.columns" :key="c" class="menu-column">
                <div v-for="(section, s) in column" :key="section.key" class="menu-section">
                  <h1 class="menu-title" :style="{ '--i': c * 6 + s * 3 }">{{ section.title }}</h1>
                  <ul class="menu-grid">
                    <li v-for="(p, i) in section.items" :key="p.id" class="menu-item" :class="{ 'is-sold-out': soldOut(p) }"
                        :style="{ '--i': c * 6 + s * 3 + i + 1 }">
                      <span v-if="showRowImages" class="item-img"><img v-if="image(p)" :src="image(p)" alt="" /></span>
                      <span class="item-body">
                        <span class="item-line">
                          <span class="item-name">{{ nameOf(p) }}</span>
                          <span class="item-dots" aria-hidden="true"></span>
                          <span v-if="design.show_prices" class="item-price">{{ soldOut(p) ? tr('soldOut') : price(p.price) }}</span>
                        </span>
                        <span v-if="design.show_descriptions && descOf(p)" class="item-desc">{{ descOf(p) }}</span>
                        <span v-if="design.show_tags && tags(p).length" class="item-tags">
                          <span v-for="tag in tags(p)" :key="tag" class="item-tag">{{ tag }}</span>
                        </span>
                      </span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
            <p v-else-if="loaded" class="menu-empty">{{ tr('empty') }}</p>
          </section>

          <div v-if="layout !== 'columns' && design.show_qr && qr" class="board-qr is-corner">
            <img :src="qr" alt="" />
            <p class="qr-title">{{ tr('orderAhead') }}<br><span class="qr-url">{{ shopHost }}</span></p>
          </div>
        </div>
      </transition>

      <footer class="board-foot">
        <div v-if="ticker" class="board-ticker"><span :style="{ animationDuration: `${Math.max(18, ticker.length / 4)}s` }">{{ ticker }}&nbsp;&nbsp;✦&nbsp;&nbsp;{{ ticker }}&nbsp;&nbsp;✦&nbsp;&nbsp;</span></div>
        <span v-else>{{ tr('vatNote') }}</span>
        <span v-if="offline" class="board-offline">{{ tr('offline') }}</span>
        <span class="board-progress" aria-hidden="true"><i :key="step" :style="{ animationDuration: `${itemSeconds}s` }"></i></span>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from '@/plugins/axios'
import { i18n } from '@/i18n'

// The menu for the shop's screens. Each screen (designed in the admin under
// "Menu screens") has its own address, /menu-board/<name>; /menu-board shows
// the default one. Its design, the live menu, promotions and opening hours
// come from the board API and refresh every minute; the screen keeps showing
// the last menu when the internet drops, checks in so the admin sees it
// online, and reloads when the admin asks. See docs/menu-board.md.
// Older links still work: ?lang=de|en, ?alternate=1, ?categories=a,b, ?seconds=12.
const route = useRoute()
const query = route.query
const slug = String(route.params.slug || 'default')
const preview = query.preview === '1'
const CACHE_KEY = `menu-board:${slug}`

const payload = ref(readCache())
const draft = ref(null) // live changes from the admin's editor (preview only)
const draftSlides = ref(null)
const pinned = ref(null) // a promotion the editor is working on, shown until released
const loaded = ref(Boolean(payload.value))
const offline = ref(false)
const step = ref(0)
const now = ref(new Date())
const qr = ref('')
const portrait = ref(false)
const boardEl = ref(null)
const menuEl = ref(null)
const roomEm = ref(36)
const baseSize = ref(16)
const size = reactive({ w: window.innerWidth, h: window.innerHeight })

function readCache() {
  try { return JSON.parse(localStorage.getItem(CACHE_KEY) || 'null') } catch { return null }
}

// ---- design ------------------------------------------------------------------
const DEFAULTS = {
  layout: 'columns', theme: 'oven', font: 'serif', language: 'de', orientation: 'auto', background_dim: 60,
  show_prices: true, show_descriptions: true, show_images: true, show_tags: true, show_qr: true, show_clock: true,
  show_status: true, sold_out: 'mark', page_seconds: 12, slide_every: 2, headline: '', headline_en: '', ticker: '', ticker_en: ''
}
const design = computed(() => {
  const merged = { ...DEFAULTS, ...(payload.value?.screen || {}), ...(draft.value || {}) }
  // Options in the address (older links) win.
  if (['de', 'en'].includes(query.lang)) merged.language = query.lang
  if (query.alternate === '1') merged.language = 'alternate'
  if (Number(query.seconds)) merged.page_seconds = Number(query.seconds)
  return merged
})
const layout = computed(() => design.value.layout)

const THEMES = {
  oven: { bg: '#0e0c0a', text: '#f4ece1', muted: '#b9ab98', accent: '#e6a15a', glow: 'rgba(230, 161, 90, 0.16)' },
  paper: { bg: '#f6efe4', text: '#1d1712', muted: '#7a6b5e', accent: '#b6722c', glow: 'rgba(182, 114, 44, 0.12)' },
  espresso: { bg: '#24170f', text: '#f6e7d3', muted: '#c7a98c', accent: '#f0b86e', glow: 'rgba(240, 184, 110, 0.15)' },
  sage: { bg: '#e8ede2', text: '#1f2a1e', muted: '#5d6d5a', accent: '#4f7d43', glow: 'rgba(79, 125, 67, 0.12)' }
}
const themeStyle = computed(() => {
  const d = design.value
  const base = THEMES[d.theme] || THEMES.oven
  const custom = d.theme === 'custom'
  const bg = (custom && d.background_color) || base.bg
  const text = (custom && d.text_color) || base.text
  const accent = d.accent_color || base.accent
  return {
    '--bg': bg,
    '--text': text,
    '--muted': custom ? `color-mix(in srgb, ${text} 62%, ${bg})` : base.muted,
    '--accent': accent,
    '--glow': custom ? `color-mix(in srgb, ${accent} 18%, transparent)` : base.glow,
    '--line': `color-mix(in srgb, ${text} 12%, transparent)`,
    '--card': `color-mix(in srgb, ${text} 5%, transparent)`,
    fontSize: `${baseSize.value}px`
  }
})
const rotated = computed(() => ['rotate-right', 'rotate-left'].includes(design.value.orientation))
const boardClass = computed(() => [
  portrait.value ? 'is-portrait' : 'is-landscape',
  `font-${design.value.font}`,
  `layout-${layout.value}`,
  { 'is-light': ['paper', 'sage'].includes(design.value.theme) || (design.value.theme === 'custom' && isLight(design.value.background_color)) }
])
// A TV standing upright while its player sends a landscape picture: turn the board.
const viewportStyle = computed(() => {
  if (!rotated.value) return {}
  const right = design.value.orientation === 'rotate-right'
  return {
    width: `${size.h}px`,
    height: `${size.w}px`,
    transformOrigin: 'top left',
    transform: right ? `rotate(90deg) translateY(-100%)` : `rotate(-90deg) translateX(-100%)`
  }
})
function isLight(hex) {
  if (!/^#[0-9a-f]{6}$/i.test(hex || '')) return false
  const [r, g, b] = [1, 3, 5].map(i => parseInt(hex.slice(i, i + 2), 16))
  return (r * 299 + g * 587 + b * 114) / 1000 > 150
}

// ---- language ------------------------------------------------------------------
const lang = ref('de')
watch(() => design.value.language, (value) => { lang.value = value === 'en' ? 'en' : 'de' }, { immediate: true })
const tr = (key, params) => i18n.global.t(`board.${key}`, params || {}, { locale: lang.value })
const intl = computed(() => (lang.value === 'en' ? 'en-GB' : 'de-DE'))
const text = (obj, field) => (lang.value === 'en' && obj[`${field}_en`]) || obj[field] || ''
const headline = computed(() => text(design.value, 'headline'))
const ticker = computed(() => text(design.value, 'ticker'))
const shop = computed(() => payload.value?.shop || { name: 'Backlover', address: '', time_zone: 'Europe/Berlin' })
const zone = computed(() => shop.value.time_zone || 'Europe/Berlin')
const status = computed(() => payload.value?.status)
const shopHost = window.location.host

const nameOf = (p) => (lang.value === 'en' && p.name_en) || p.name
function descOf(p, max = 90) {
  const value = (lang.value === 'en' && p.description_en) || p.description || ''
  return value.length > max ? `${value.slice(0, max - 2).trim()}…` : value
}
const image = (p) => p.image_url || p.image
const soldOut = (p) => p.stock === 0
const price = (value) => new Intl.NumberFormat(intl.value, { style: 'currency', currency: 'EUR' }).format(Number(value))
const tags = (p) => [
  p.is_vegan ? tr('vegan') : p.is_vegetarian ? tr('vegetarian') : null,
  p.is_gluten_free ? tr('glutenFree') : null,
  p.is_seasonal ? tr('seasonal') : null
].filter(Boolean)

function categoryTitle(category) {
  if (!category) return ''
  if (lang.value === 'en' && category.name_en) return category.name_en
  const key = `categories.${category.slug}`
  // Categories created with the shop carry English names; show them translated.
  if (i18n.global.te(key, 'en') && category.name === i18n.global.t(key, {}, { locale: 'en' })) {
    return i18n.global.t(key, {}, { locale: lang.value })
  }
  return category.name
}

// ---- menu ----------------------------------------------------------------------
// The API already applies the screen's choices; the preview gets everything
// and applies the editor's unsaved choices here.
const categories = computed(() => {
  const all = payload.value?.categories || []
  const wanted = (design.value.categories || []).map(String)
  const fromQuery = String(query.categories || '').split(',').map(s => s.trim()).filter(Boolean)
  let list = wanted.length ? wanted.map(id => all.find(c => String(c.id) === id)).filter(Boolean) : all
  if (fromQuery.length) list = list.filter(c => fromQuery.includes(c.slug))
  return list
})
const products = computed(() => {
  const hidden = new Set((design.value.hidden_products || []).map(String))
  const allowed = new Set(categories.value.map(c => c.slug))
  return (payload.value?.products || []).filter(p => p.category && allowed.has(p.category.slug) && !hidden.has(String(p.id)) &&
    !(design.value.sold_out === 'hide' && soldOut(p)))
})
const groups = computed(() => categories.value
  .map(category => ({ category, items: products.value.filter(p => p.category.slug === category.slug) }))
  .filter(g => g.items.length))

const showRowImages = computed(() => layout.value === 'columns' && design.value.show_images)
const columns = computed(() => {
  if (layout.value === 'list') return portrait.value ? 1 : 3
  return portrait.value ? 1 : 2
})
const gridCols = computed(() => (portrait.value ? 2 : 4))

// Columns and list: categories flow down the columns of screen-sized pages
// like a printed menu. Sizes in em match the styles below.
function flowPages(rowEm, headingEm) {
  const out = []
  const room = Math.max(roomEm.value, headingEm + rowEm)
  let current = null
  let column = null
  let used = 0
  const nextColumn = () => {
    if (!current || current.columns.length >= columns.value) {
      current = { key: `p${out.length}`, columns: [] }
      out.push(current)
    }
    column = []
    current.columns.push(column)
    used = 0
  }
  for (const group of groups.value) {
    let items = group.items
    let part = 0
    while (items.length) {
      if (!column || room - used < headingEm + rowEm) nextColumn()
      const rows = Math.max(1, Math.floor((room - used - headingEm) / rowEm))
      const take = items.slice(0, rows)
      column.push({ key: `${group.category.slug}-${part}`, title: categoryTitle(group.category), items: take })
      used += headingEm + take.length * rowEm
      items = items.slice(take.length)
      part += 1
    }
  }
  return out
}

const menuPages = computed(() => {
  const d = design.value
  if (layout.value === 'grid') {
    const perPage = gridCols.value * 2
    return groups.value.flatMap(group => {
      const pages = []
      for (let i = 0; i < group.items.length; i += perPage) {
        pages.push({ key: `${group.category.slug}-${i}`, title: categoryTitle(group.category), items: group.items.slice(i, i + perPage) })
      }
      return pages
    })
  }
  if (layout.value === 'list') {
    const row = 2.6 + (d.show_descriptions ? 1.9 : 0) + (d.show_tags ? 0.6 : 0)
    return flowPages(row, 5.6)
  }
  if (layout.value === 'spotlight') return []
  const row = d.show_images ? 9 : 3.4 + (d.show_descriptions ? 2 : 0) + (d.show_tags ? 1.4 : 0)
  return flowPages(row, 7)
})

const featuredList = computed(() => {
  const wanted = (draft.value ? draft.value.featured_products || [] : payload.value?.featured || []).map(String)
  const byId = new Map(products.value.map(p => [String(p.id), p]))
  const chosen = wanted.map(id => byId.get(id)).filter(Boolean)
  return chosen.length ? chosen : products.value.filter(p => image(p) && !soldOut(p))
})

const slides = computed(() => draftSlides.value || payload.value?.slides || [])

// What the screen shows, in order: menu pages with a promotion after every
// few of them. Spotlight shows one product per step.
const sequence = computed(() => {
  const items = layout.value === 'spotlight'
    ? featuredList.value.map(product => ({
      type: 'spot', product,
      others: products.value.filter(p => p.category.slug === product.category.slug && p.id !== product.id).slice(0, 4)
    }))
    : menuPages.value.map(page => ({ type: 'page', page }))
  const promos = slides.value
  if (!promos.length) return items
  const every = Math.max(1, design.value.slide_every || 1)
  const out = []
  let s = 0
  items.forEach((entry, i) => {
    out.push(entry)
    if ((i + 1) % every === 0) out.push({ type: 'slide', slide: promos[s++ % promos.length] })
  })
  if (!items.length) promos.forEach(slide => out.push({ type: 'slide', slide }))
  return out
})
const item = computed(() => {
  if (pinned.value) return { type: 'slide', slide: pinned.value }
  return sequence.value.length ? sequence.value[step.value % sequence.value.length] : null
})
const itemSeconds = computed(() => Math.max(5, (item.value?.type === 'slide' && item.value.slide.seconds) || design.value.page_seconds || 12))

// The large product in the columns layout follows the page.
const featured = computed(() => {
  const page = item.value?.page
  const onPage = page?.columns ? page.columns.flat().flatMap(section => section.items).filter(p => image(p)) : []
  const list = featuredList.value.length ? featuredList.value : onPage
  return list.length ? list[step.value % list.length] : null
})

// ---- clock and status ----------------------------------------------------------
const clock = computed(() => new Intl.DateTimeFormat(intl.value, { timeZone: zone.value, hour: '2-digit', minute: '2-digit' }).format(now.value))
const statusText = computed(() => {
  const s = status.value
  if (!s) return ''
  if (s.open_now) return tr('openUntil', { time: s.closes_at })
  const closedNote = typeof s.closed_today === 'string' ? ` (${s.closed_today})` : ''
  if (!s.next_open) return tr('closed') + closedNote
  const next = new Date(s.next_open)
  const dayKey = (d) => new Intl.DateTimeFormat('en-CA', { timeZone: zone.value }).format(d)
  const time = new Intl.DateTimeFormat(intl.value, { timeZone: zone.value, hour: '2-digit', minute: '2-digit' }).format(next)
  let when
  if (dayKey(next) === dayKey(now.value)) when = tr('todayAt', { time })
  else if (dayKey(next) === dayKey(new Date(now.value.getTime() + 864e5))) when = tr('tomorrow', { time })
  else when = tr('onDay', { day: new Intl.DateTimeFormat(intl.value, { timeZone: zone.value, weekday: 'long' }).format(next), time })
  return `${tr('closed')}${closedNote} · ${tr('opensAt', { when })}`
})

// ---- data ----------------------------------------------------------------------
let reloadToken = null
async function load() {
  try {
    const { data } = await axios.get(`/api/menu-screens/${slug}/board/`, { params: preview ? { preview: 1 } : {}, timeout: 15000 })
    payload.value = data
    offline.value = false
    if (!preview) {
      try { localStorage.setItem(CACHE_KEY, JSON.stringify(data)) } catch { /* storage full: fine */ }
      checkReload(data.screen?.reload_token)
    }
  } catch (err) {
    if (err.response?.status === 404 && !payload.value) payload.value = { screen: {}, categories: [], products: [], slides: [] }
    offline.value = !err.response // keep showing the last menu
  } finally {
    loaded.value = true
  }
}

function checkReload(token) {
  if (token === undefined || token === null) return
  if (reloadToken === null) reloadToken = token
  else if (token !== reloadToken) window.location.reload()
}

async function heartbeat() {
  if (preview || slug === 'default' && !payload.value?.screen?.slug) return
  try {
    const { data } = await axios.post(`/api/menu-screens/${payload.value?.screen?.slug || slug}/heartbeat/`, {
      width: window.screen.width, height: window.screen.height, agent: navigator.userAgent.slice(0, 180), version: 'board-2'
    }, { timeout: 15000 })
    checkReload(data.reload_token)
  } catch { /* offline */ }
}

function advance() {
  const count = Math.max(sequence.value.length, 1)
  const next = step.value + 1
  if (next % count === 0 && design.value.language === 'alternate') lang.value = lang.value === 'de' ? 'en' : 'de'
  step.value = next
  schedule()
}
let stepTimer = null
function schedule() {
  clearTimeout(stepTimer)
  stepTimer = setTimeout(advance, itemSeconds.value * 1000)
}

async function measure() {
  size.w = window.innerWidth
  size.h = window.innerHeight
  const w = rotated.value ? size.h : size.w
  const h = rotated.value ? size.w : size.h
  portrait.value = h > w
  // One em: the layout keeps its proportions on any screen, HD to 4K.
  baseSize.value = portrait.value ? Math.min(w / 56.25, h / 100) : Math.min(w / 100, h / 56.25)
  await nextTick()
  const el = menuEl.value
  if (!el) return
  roomEm.value = el.clientHeight / (parseFloat(getComputedStyle(el).fontSize) || baseSize.value) - 1
}
watch([layout, () => design.value.orientation, () => design.value.show_images, () => design.value.show_descriptions], () => setTimeout(measure, 50))

// Keep the screen on while the board is showing.
let wakeLock = null
async function keepAwake() {
  try {
    if ('wakeLock' in navigator && document.visibilityState === 'visible') wakeLock = await navigator.wakeLock.request('screen')
  } catch { /* not allowed here; the TV's own settings apply */ }
}

// The admin's editor sends unsaved changes to this page in its preview frame.
function onMessage(event) {
  if (event.origin !== window.location.origin || event.data?.type !== 'board-preview') return
  draft.value = event.data.screen || null
  draftSlides.value = event.data.slides || null
  pinned.value = event.data.pin || null
  if (event.data.step !== undefined) step.value = event.data.step
  setTimeout(measure, 50)
}

let timers = []
onMounted(async () => {
  measure()
  window.addEventListener('resize', measure)
  if (preview) window.addEventListener('message', onMessage)
  else {
    document.addEventListener('visibilitychange', keepAwake)
    keepAwake()
  }
  await load()
  await measure()
  schedule()
  heartbeat()
  try {
    const QRCode = await import('qrcode')
    qr.value = await QRCode.toDataURL(`${window.location.origin}/products`, { margin: 0, width: 360, color: { dark: '#0e0c0a', light: '#f4ece1' } })
  } catch { /* no QR code */ }
  timers = [
    setInterval(load, 60_000),
    setInterval(heartbeat, 60_000),
    setInterval(() => { now.value = new Date() }, 10_000)
  ]
  // A fresh start twice a day picks up new versions of the site.
  if (!preview) timers.push(setTimeout(() => window.location.reload(), 12 * 3600_000))
  if (preview) window.parent?.postMessage({ type: 'board-ready' }, window.location.origin)
})

onBeforeUnmount(() => {
  timers.forEach(clearInterval)
  clearTimeout(stepTimer)
  window.removeEventListener('resize', measure)
  window.removeEventListener('message', onMessage)
  document.removeEventListener('visibilitychange', keepAwake)
  wakeLock?.release?.()
})
</script>

<style scoped>
/* Everything is sized in em from one base (set from the screen size), so the
   layout keeps its proportions on any screen: 1080p, 4K, landscape or portrait. */
.board-viewport { position: fixed; inset: 0; z-index: 50; overflow: hidden; background: #000; }
.board {
  --ease: cubic-bezier(0.16, 1, 0.3, 1);
  position: absolute;
  inset: 0;
  display: grid;
  grid-template-rows: auto 1fr auto;
  padding: 2.4em 3em 1.6em;
  color: var(--text);
  background:
    radial-gradient(60% 70% at 15% 55%, var(--glow), transparent 70%),
    radial-gradient(50% 60% at 100% 0%, color-mix(in srgb, var(--accent) 8%, transparent), transparent 70%),
    var(--bg);
  overflow: hidden;
  cursor: none;
  user-select: none;
  font-family: 'Manrope Variable', 'Manrope', system-ui, sans-serif;
}
.board.is-portrait { padding: 3em 3em 2em; }
.board-photo { position: absolute; inset: 0; background-size: cover; background-position: center; }
.board-photo span { position: absolute; inset: 0; background: var(--bg); }
.board > :not(.board-photo) { position: relative; }

.font-serif .board-logo, .font-serif .menu-title, .font-serif .feature-name, .font-serif .slide-title,
.font-serif .spot-name, .font-serif .grid-title, .board-clock-serif {
  font-family: 'Instrument Serif', Georgia, serif; font-weight: 400;
}
.font-sans .board-logo, .font-sans .menu-title, .font-sans .feature-name, .font-sans .slide-title,
.font-sans .spot-name, .font-sans .grid-title {
  font-family: 'Manrope Variable', system-ui, sans-serif; font-weight: 800; letter-spacing: -0.03em;
}
.board-logo em { color: var(--accent); font-style: normal; }

/* Header */
.board-head {
  display: flex; flex-wrap: wrap; gap: 1em 2em; align-items: center; justify-content: space-between;
  padding-bottom: 1.6em; margin-bottom: 2em; border-bottom: 1px solid var(--line);
}
.board-brand { display: flex; align-items: baseline; gap: 1.4em; min-width: 0; }
.board-logo { font-size: 3.4em; line-height: 1; white-space: nowrap; }
.board-place { font-size: 1.15em; color: var(--muted); letter-spacing: 0.02em; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.board-status { display: flex; align-items: center; gap: 1.6em; }
.board-open {
  display: inline-flex; align-items: center; gap: 0.6em; padding: 0.55em 1.1em; border-radius: 9999px;
  font-size: 1.1em; font-weight: 600; color: #3f8a4a; background: rgba(110, 190, 120, 0.14);
}
.board:not(.is-light) .board-open { color: #c7e6c2; }
.board-open i { width: 0.6em; height: 0.6em; border-radius: 50%; background: #6bbf6f; box-shadow: 0 0 0 0.25em rgba(110, 190, 120, 0.25); animation: pulse 2.4s ease-in-out infinite; }
.board-open.is-closed { color: #c4532f; background: rgba(240, 143, 121, 0.14); }
.board:not(.is-light) .board-open.is-closed { color: #f0b4a3; }
.board-open.is-closed i { background: #f08f79; box-shadow: none; animation: none; }
.board-clock { font-size: 2.2em; font-weight: 600; font-variant-numeric: tabular-nums; }

/* Body */
.board-body { display: grid; min-height: 0; }
.board-body.is-columns { grid-template-columns: 27em 1fr; gap: 0 3em; }
.is-portrait .board-body.is-columns { grid-template-columns: 1fr; grid-template-rows: auto 1fr; gap: 2em; }
.board-body.is-grid, .board-body.is-list { position: relative; }

.board-eyebrow { font-size: 1em; font-weight: 700; letter-spacing: 0.2em; text-transform: uppercase; color: var(--accent); }

/* Feature column */
.board-feature { display: flex; flex-direction: column; gap: 2em; min-height: 0; }
.is-portrait .board-feature { flex-direction: row; align-items: center; }
.feature-card { flex: 1; min-height: 0; display: flex; flex-direction: column; }
.is-portrait .feature-card { flex-direction: row; align-items: center; gap: 2em; }
.feature-stage { position: relative; flex: 1; min-height: 0; display: grid; place-items: center; margin: 1em 0; }
.is-portrait .feature-stage { flex: none; width: 18em; height: 14em; margin: 0; }
.feature-glow { position: absolute; inset: 10% 5%; border-radius: 50%; background: radial-gradient(closest-side, var(--glow), transparent); filter: blur(1em); }
.feature-img { position: relative; max-width: 100%; max-height: 100%; object-fit: contain; filter: drop-shadow(0 1.5em 2em rgba(0, 0, 0, 0.35)); animation: float 6s ease-in-out infinite; }
.feature-name { font-size: 3em; line-height: 1.05; }
.feature-price { margin-top: 0.3em; font-size: 1.8em; font-weight: 700; color: var(--accent); }
.board-qr { display: flex; align-items: center; gap: 1.2em; padding: 1.2em; border-radius: 1.4em; background: var(--card); border: 1px solid var(--line); }
.board-qr img { width: 7em; height: 7em; border-radius: 0.6em; background: #f4ece1; padding: 0.4em; }
.qr-title { font-size: 1.3em; font-weight: 700; }
.qr-text { margin-top: 0.2em; font-size: 0.95em; color: var(--muted); }
.qr-url { margin-top: 0.4em; font-size: 0.95em; font-weight: 600; color: var(--accent); }
.board-qr.is-corner { position: absolute; right: 0; bottom: 0; padding: 0.8em 1em; gap: 0.9em; }
.board-qr.is-corner img { width: 5.2em; height: 5.2em; }
.board-qr.is-corner .qr-title { font-size: 1em; }

/* Menu */
.board-menu { position: relative; min-height: 0; overflow: hidden; }
.menu-dots { position: absolute; top: 0.6em; right: 0; display: flex; gap: 0.5em; z-index: 1; }
.menu-dots i { width: 0.6em; height: 0.6em; border-radius: 50%; background: var(--line); transition: background 0.4s, transform 0.4s; }
.menu-dots i.is-on { background: var(--accent); transform: scale(1.3); }
.menu-page { display: grid; grid-template-columns: repeat(var(--cols), minmax(0, 1fr)); gap: 0 3em; height: 100%; }
.menu-column { min-width: 0; }
.menu-section + .menu-section { margin-top: 1.4em; }
.menu-title { font-size: 3.6em; line-height: 1; margin-bottom: 0.3em; animation: rise 0.8s var(--ease) both; animation-delay: calc(var(--i, 0) * 60ms); }
.menu-grid { display: grid; gap: 0; }
.menu-item { display: flex; align-items: center; gap: 1.4em; min-width: 0; height: 9em; animation: rise 0.8s var(--ease) both; animation-delay: calc(var(--i, 0) * 60ms); }
.layout-columns .menu-item:not(:has(.item-img)) { height: auto; padding: 0.9em 0; }
.item-img { flex: none; display: grid; place-items: center; width: 7em; height: 7em; border-radius: 50%; background: radial-gradient(closest-side, var(--glow), transparent); }
.item-img img { width: 6.4em; height: 6.4em; object-fit: contain; filter: drop-shadow(0 0.5em 0.6em rgba(0, 0, 0, 0.3)); }
.item-body { flex: 1; min-width: 0; display: grid; gap: 0.35em; }
.item-line { display: flex; align-items: baseline; gap: 0.6em; min-width: 0; }
.item-name { min-width: 0; font-size: 1.75em; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.item-dots { flex: 1; min-width: 0.6em; border-bottom: 0.12em dotted var(--line); transform: translateY(-0.35em); }
.item-price { flex: none; font-size: 1.75em; font-weight: 700; color: var(--accent); font-variant-numeric: tabular-nums; }
.item-desc { font-size: 1.15em; line-height: 1.35; color: var(--muted); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.item-tags { display: flex; flex-wrap: wrap; gap: 0.4em; }
.item-tag { padding: 0.15em 0.65em; border-radius: 9999px; font-size: 0.9em; font-weight: 700; color: #3f8a4a; background: rgba(110, 190, 120, 0.16); }
.board:not(.is-light) .item-tag { color: #b8e3b2; }
.menu-item.is-sold-out { opacity: 0.45; }
.menu-item.is-sold-out .item-price { color: var(--muted); font-size: 1.3em; }
.menu-empty { display: grid; place-items: center; height: 100%; font-size: 2em; color: var(--muted); }

/* List layout: a typographic menu */
.layout-list .menu-title { font-size: 3em; padding-bottom: 0.25em; border-bottom: 1px solid var(--line); margin-bottom: 0.6em; }
.layout-list .menu-item { height: auto; padding: 0.55em 0; }
.layout-list .item-name, .layout-list .item-price { font-size: 1.5em; }
.layout-list .item-desc { font-size: 1.05em; -webkit-line-clamp: 1; }

/* Grid layout: photo cards */
.grid-title { font-size: 3.6em; line-height: 1; margin-bottom: 0.5em; animation: rise 0.8s var(--ease) both; }
.grid-cards { display: grid; grid-template-columns: repeat(var(--cols), minmax(0, 1fr)); grid-auto-rows: 1fr; gap: 1.6em; height: calc(100% - 5em); }
.grid-card { display: flex; flex-direction: column; min-height: 0; padding: 1.2em 1.4em; border-radius: 1.6em; background: var(--card); border: 1px solid var(--line); animation: rise 0.8s var(--ease) both; animation-delay: calc(var(--i) * 70ms); }
.grid-img { flex: 1; min-height: 0; display: grid; place-items: center; margin-bottom: 0.6em; background: radial-gradient(closest-side, var(--glow), transparent); }
.grid-img img { max-width: 100%; max-height: 100%; object-fit: contain; filter: drop-shadow(0 0.8em 1em rgba(0, 0, 0, 0.3)); }
.grid-name { font-size: 1.7em; font-weight: 700; line-height: 1.15; }
.grid-desc { margin-top: 0.3em; font-size: 1.05em; line-height: 1.35; color: var(--muted); }
.grid-foot { display: flex; align-items: flex-end; justify-content: space-between; gap: 0.6em; margin-top: auto; padding-top: 0.6em; }
.grid-price { font-size: 1.8em; color: var(--accent); white-space: nowrap; }
.grid-card.is-sold-out { opacity: 0.45; }

/* Spotlight */
.board-spot { display: grid; grid-template-columns: 1.1fr 1fr; gap: 3em; align-items: center; min-height: 0; }
.is-portrait .board-spot { grid-template-columns: 1fr; grid-template-rows: 1fr auto; }
.spot-stage { position: relative; height: 100%; min-height: 0; display: grid; place-items: center; }
.spot-stage img { position: relative; max-width: 100%; max-height: 100%; object-fit: contain; filter: drop-shadow(0 2em 3em rgba(0, 0, 0, 0.35)); animation: zoom 1.2s var(--ease) both, float 6s ease-in-out 1.2s infinite; }
.spot-name { margin-top: 0.15em; font-size: 6em; line-height: 0.95; animation: rise 0.9s var(--ease) both; }
.spot-desc { margin-top: 0.7em; max-width: 30em; font-size: 1.5em; line-height: 1.45; color: var(--muted); animation: rise 0.9s var(--ease) 0.1s both; }
.spot-copy .item-tags { margin-top: 1em; font-size: 1.2em; }
.spot-price { margin-top: 0.4em; font-size: 4em; font-weight: 800; color: var(--accent); animation: rise 0.9s var(--ease) 0.2s both; }
.spot-others { margin-top: 1.6em; display: grid; gap: 0.5em; max-width: 28em; padding-top: 1.2em; border-top: 1px solid var(--line); }
.spot-others li { display: flex; justify-content: space-between; gap: 1em; font-size: 1.3em; color: var(--muted); }
.spot-others b { color: var(--text); }

/* Promotion slides */
.board-slide { position: relative; display: grid; grid-template-columns: 1fr 1fr; align-items: center; gap: 3em; min-height: 0; border-radius: 2em; overflow: hidden; }
.is-portrait .board-slide { grid-template-columns: 1fr; }
.board-slide.is-text { grid-template-columns: 1fr; text-align: center; place-items: center; background: var(--accent); color: var(--bg); }
.board-slide.is-text .board-eyebrow { color: var(--bg); opacity: 0.75; }
.board-slide.is-photo { grid-template-columns: 1fr; align-items: end; }
.slide-photo { position: absolute; inset: 0; background-size: cover; background-position: center; animation: kenburns 14s ease-out both; }
.board-slide.is-photo::after { content: ''; position: absolute; inset: 0; background: linear-gradient(0deg, rgba(0, 0, 0, 0.78), rgba(0, 0, 0, 0.1) 65%); }
.board-slide.is-photo .slide-copy { position: relative; z-index: 1; padding: 3em; color: #fff; }
.slide-copy { padding: 0 1em; }
.slide-title { margin-top: 0.15em; font-size: 6.4em; line-height: 0.95; animation: rise 0.9s var(--ease) both; }
.board-slide.is-text .slide-title { font-size: 7.5em; max-width: 14em; }
.slide-text { margin-top: 0.6em; max-width: 26em; font-size: 1.8em; line-height: 1.4; opacity: 0.85; animation: rise 0.9s var(--ease) 0.1s both; }
.board-slide.is-text .slide-text { margin-inline: auto; }
.slide-price { margin-top: 0.5em; font-size: 4.6em; font-weight: 800; color: var(--accent); animation: rise 0.9s var(--ease) 0.2s both; }
.board-slide.is-text .slide-price, .board-slide.is-photo .slide-price { color: inherit; }
.slide-price small { display: block; font-size: 0.3em; font-weight: 600; opacity: 0.7; }
.slide-stage { position: relative; height: 100%; min-height: 0; display: grid; place-items: center; }
.slide-stage img { position: relative; max-width: 100%; max-height: 100%; object-fit: contain; filter: drop-shadow(0 2em 3em rgba(0, 0, 0, 0.35)); animation: zoom 1.2s var(--ease) both; }

/* Footer */
.board-foot { display: flex; align-items: center; gap: 2em; margin-top: 1.6em; padding-top: 1.2em; border-top: 1px solid var(--line); font-size: 1em; color: var(--muted); }
.board-ticker { flex: 1; min-width: 0; overflow: hidden; white-space: nowrap; font-size: 1.4em; font-weight: 600; color: var(--text); }
.board-ticker span { display: inline-block; padding-left: 100%; animation: ticker linear infinite; }
.board-offline { padding: 0.2em 0.8em; border-radius: 9999px; color: #f0b4a3; background: rgba(240, 143, 121, 0.14); }
.board-progress { flex: none; width: 12em; height: 0.3em; margin-left: auto; border-radius: 9999px; background: var(--line); overflow: hidden; }
.board-progress i { display: block; height: 100%; background: var(--accent); animation: progress linear both; }

/* Motion */
.swap-enter-active { transition: opacity 0.6s var(--ease), transform 0.8s var(--ease); }
.swap-leave-active { transition: opacity 0.35s ease; }
.swap-enter-from { opacity: 0; transform: translateY(1.5em); }
.swap-leave-to { opacity: 0; }
.feature-enter-active, .feature-leave-active { transition: opacity 0.5s, transform 0.6s var(--ease); }
.feature-enter-from { opacity: 0; transform: scale(0.94); }
.feature-leave-to { opacity: 0; }
@keyframes rise { from { opacity: 0; transform: translateY(0.8em); } }
@keyframes zoom { from { opacity: 0; transform: scale(0.9) rotate(-3deg); } }
@keyframes float { 50% { transform: translateY(-0.6em) rotate(1deg); } }
@keyframes pulse { 50% { box-shadow: 0 0 0 0.5em rgba(110, 190, 120, 0); } }
@keyframes progress { from { width: 0; } to { width: 100%; } }
@keyframes ticker { to { transform: translateX(-100%); } }
@keyframes kenburns { from { transform: scale(1.12); } }
@media (prefers-reduced-motion: reduce) {
  .board *, .board *::before, .board *::after { animation-duration: 0.01ms !important; animation-iteration-count: 1 !important; }
  .board-ticker span { animation: none; padding-left: 0; }
}
</style>
