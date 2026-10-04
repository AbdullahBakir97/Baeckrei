<template>
  <div class="board" :class="[`is-${orientation}`]" :lang="lang">
    <!-- Header: brand, opening status, clock -->
    <header class="board-head">
      <div class="board-brand">
        <span class="board-logo"><em>{{ business.name.charAt(0) }}</em>{{ business.name.slice(1) }}</span>
        <span class="board-place">{{ place }}</span>
      </div>
      <div class="board-status">
        <span v-if="status" class="board-open" :class="{ 'is-closed': !status.open_now }">
          <i aria-hidden="true"></i>{{ statusText }}
        </span>
        <span class="board-clock">{{ clock }}</span>
      </div>
    </header>

    <!-- Feature: one product, large -->
    <aside class="board-feature">
      <transition name="feature" mode="out-in">
        <div v-if="featured" :key="featured.id" class="feature-card">
          <p class="board-eyebrow">{{ tr('featured') }}</p>
          <div class="feature-stage">
            <span class="feature-glow" aria-hidden="true"></span>
            <img :src="featured.image_url || featured.image" :alt="nameOf(featured)" class="feature-img" />
          </div>
          <h2 class="feature-name">{{ nameOf(featured) }}</h2>
          <p class="feature-price">{{ price(featured.price) }}</p>
        </div>
      </transition>

      <div class="board-qr">
        <img v-if="qr" :src="qr" alt="" />
        <div>
          <p class="qr-title">{{ tr('orderAhead') }}</p>
          <p class="qr-text">{{ tr('orderAheadText') }}</p>
          <p class="qr-url">{{ shopHost }}</p>
        </div>
      </div>
    </aside>

    <!-- Current page of the menu -->
    <section ref="menuEl" class="board-menu">
      <span v-if="pages.length > 1" class="menu-dots" aria-hidden="true">
        <i v-for="(p, i) in pages" :key="p.key + i" :class="{ 'is-on': i === pageIndex }"></i>
      </span>

      <transition name="page" mode="out-in">
        <div v-if="page" :key="`${page.key}-${lang}`" class="menu-page" :style="{ '--cols': columns }">
          <div v-for="(column, c) in page.columns" :key="c" class="menu-column">
          <div v-for="(section, s) in column" :key="section.key" class="menu-section">
            <h1 class="menu-title" :style="{ '--i': c * 6 + s * 3 }">{{ section.title }}</h1>
            <ul class="menu-grid">
              <li v-for="(item, i) in section.items" :key="item.id" class="menu-item" :class="{ 'is-sold-out': item.stock === 0 }"
                  :style="{ '--i': c * 6 + s * 3 + i + 1 }">
            <span class="item-img"><img :src="item.image_url || item.image" alt="" loading="eager" /></span>
            <span class="item-body">
              <span class="item-line">
                <span class="item-name">{{ nameOf(item) }}</span>
                <span class="item-dots" aria-hidden="true"></span>
                <span class="item-price">{{ item.stock === 0 ? tr('soldOut') : price(item.price) }}</span>
              </span>
              <span v-if="descOf(item)" class="item-desc">{{ descOf(item) }}</span>
              <span v-if="tags(item).length" class="item-tags">
                <span v-for="tag in tags(item)" :key="tag" class="item-tag">{{ tag }}</span>
              </span>
            </span>
              </li>
            </ul>
          </div>
          </div>
        </div>
        <p v-else-if="loaded" class="menu-empty">{{ tr('empty') }}</p>
      </transition>
    </section>

    <footer class="board-foot">
      <span>{{ tr('vatNote') }}</span>
      <span v-if="offline" class="board-offline">{{ tr('offline') }}</span>
      <span class="board-progress" aria-hidden="true"><i :key="tick" :style="{ animationDuration: `${seconds}s` }"></i></span>
    </footer>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import axios from '@/plugins/axios'
import { i18n } from '@/i18n'
import { business, streetLine, cityLine } from '@/config/business'

// A menu for screens in the shop (TVs, monitors, portrait displays).
// Open /menu-board on the screen's browser in full screen. Options:
//   ?lang=de|en        language (default: German)
//   ?alternate=1       switch between German and English after each round
//   ?categories=a,b    only these category slugs (e.g. one screen per counter)
//   ?seconds=12        time per page
// Products, prices and "sold out" come live from the shop and refresh
// every minute. See docs/menu-board.md.
const route = useRoute()
const query = route.query
const LANGS = ['de', 'en']
const startLang = LANGS.includes(query.lang) ? query.lang : 'de'
const alternate = query.alternate === '1'
const seconds = Math.max(5, Number(query.seconds) || 12)
const onlyCategories = String(query.categories || '').split(',').map(s => s.trim()).filter(Boolean)

const lang = ref(startLang)
const products = ref([])
const categories = ref([])
const status = ref(null)
const loaded = ref(false)
const offline = ref(false)
const pageIndex = ref(0)
const tick = ref(0)
const now = ref(new Date())
const qr = ref('')
const orientation = ref('landscape')
const menuEl = ref(null)
const roomEm = ref(36) // height of the menu area, in em

const tr = (key, params) => i18n.global.t(`board.${key}`, params || {}, { locale: lang.value })
const intl = computed(() => (lang.value === 'en' ? 'en-GB' : 'de-DE'))
const place = [streetLine(), cityLine()].filter(Boolean).join(', ')
const shopHost = window.location.host

const nameOf = (p) => (lang.value === 'en' && p.name_en) || p.name
const descOf = (p) => {
  const text = (lang.value === 'en' && p.description_en) || p.description || ''
  return text.length > 90 ? `${text.slice(0, 88).trim()}…` : text
}
const price = (value) => new Intl.NumberFormat(intl.value, { style: 'currency', currency: 'EUR' }).format(Number(value))
const tags = (p) => [
  p.is_vegan ? tr('vegan') : p.is_vegetarian ? tr('vegetarian') : null,
  p.is_gluten_free ? tr('glutenFree') : null,
  p.is_seasonal ? tr('seasonal') : null
].filter(Boolean)

function categoryTitle(category) {
  if (lang.value === 'en' && category.name_en) return category.name_en
  const key = `categories.${category.slug}`
  // Categories created with the shop carry English names; show them translated.
  if (i18n.global.te(key, 'en') && category.name === i18n.global.t(key, {}, { locale: 'en' })) {
    return i18n.global.t(key, {}, { locale: lang.value })
  }
  return category.name
}

// Pages: categories in order, flowing down the columns of screen-sized
// pages like a printed menu. Small categories share a column; long ones
// continue in the next. Sizes in em match the styles below.
const ROW_EM = 9
const HEADING_EM = 7
const columns = computed(() => (orientation.value === 'portrait' ? 1 : 2))
const pages = computed(() => {
  const out = []
  const visible = products.value.filter(p => p.category && (!onlyCategories.length || onlyCategories.includes(p.category.slug)))
  const order = categories.value.map(c => c.slug)
  const groups = new Map()
  for (const product of visible) {
    const slug = product.category.slug
    if (!groups.has(slug)) groups.set(slug, { category: product.category, items: [] })
    groups.get(slug).items.push(product)
  }
  const sorted = [...groups.values()].sort((a, b) => {
    const ia = order.indexOf(a.category.slug)
    const ib = order.indexOf(b.category.slug)
    return (ia < 0 ? 99 : ia) - (ib < 0 ? 99 : ib)
  })
  const room = Math.max(roomEm.value, HEADING_EM + ROW_EM)
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
  for (const group of sorted) {
    let items = group.items
    let part = 0
    while (items.length) {
      if (!column || room - used < HEADING_EM + ROW_EM) nextColumn()
      const rows = Math.max(1, Math.floor((room - used - HEADING_EM) / ROW_EM))
      const take = items.slice(0, rows)
      column.push({ key: `${group.category.slug}-${part}`, title: categoryTitle(group.category), items: take })
      used += HEADING_EM + take.length * ROW_EM
      items = items.slice(take.length)
      part += 1
    }
  }
  return out
})
const page = computed(() => pages.value[pageIndex.value % Math.max(pages.value.length, 1)])

// The large product on the left follows the page, picking one with a photo.
const featured = computed(() => {
  const onPage = page.value ? page.value.columns.flat().flatMap(section => section.items) : products.value
  const candidates = onPage.filter(p => p.image_url || p.image)
  if (!candidates.length) return null
  return candidates[tick.value % candidates.length]
})

const clock = computed(() => new Intl.DateTimeFormat(intl.value, {
  timeZone: business.timeZone, hour: '2-digit', minute: '2-digit'
}).format(now.value))

const statusText = computed(() => {
  const s = status.value
  if (!s) return ''
  if (s.open_now) return tr('openUntil', { time: s.closes_at })
  if (!s.next_open) return tr('closed')
  const next = new Date(s.next_open)
  const dayKey = (d) => new Intl.DateTimeFormat('en-CA', { timeZone: business.timeZone }).format(d)
  const time = new Intl.DateTimeFormat(intl.value, { timeZone: business.timeZone, hour: '2-digit', minute: '2-digit' }).format(next)
  let when
  if (dayKey(next) === dayKey(now.value)) when = tr('todayAt', { time })
  else if (dayKey(next) === dayKey(new Date(now.value.getTime() + 864e5))) when = tr('tomorrow', { time })
  else when = tr('onDay', { day: new Intl.DateTimeFormat(intl.value, { timeZone: business.timeZone, weekday: 'long' }).format(next), time })
  return `${tr('closed')} · ${tr('opensAt', { when })}`
})

// ---- data -----------------------------------------------------------------
async function load() {
  try {
    const all = []
    let pageNo = 1
    for (;;) {
      const { data } = await axios.get('/api/products/', { params: { page_size: 100, page: pageNo } })
      all.push(...(data.results || data))
      if (!data.has_next) break
      pageNo += 1
    }
    products.value = all.filter(p => p.available !== false && p.status !== 'inactive')
    const cats = await axios.get('/api/products/categories/', { params: { page_size: 100 } }).catch(() => null)
    if (cats) categories.value = cats.data.results || cats.data
    status.value = (await axios.get('/api/orders/opening-hours/').catch(() => ({ data: status.value }))).data
    offline.value = false
  } catch {
    offline.value = true // keep showing what we have
  } finally {
    loaded.value = true
  }
}

function nextPage() {
  tick.value += 1
  const count = Math.max(pages.value.length, 1)
  const next = (pageIndex.value + 1) % count
  if (next === 0 && alternate) lang.value = lang.value === 'de' ? 'en' : 'de'
  pageIndex.value = next
}

async function measure() {
  orientation.value = window.innerHeight > window.innerWidth ? 'portrait' : 'landscape'
  await nextTick()
  const el = menuEl.value
  if (!el) return
  const em = parseFloat(getComputedStyle(el).fontSize) || 16
  roomEm.value = el.clientHeight / em - 1
}

// Keep the screen on while the board is showing.
let wakeLock = null
async function keepAwake() {
  try {
    if ('wakeLock' in navigator && document.visibilityState === 'visible') {
      wakeLock = await navigator.wakeLock.request('screen')
    }
  } catch { /* not allowed here; the TV's own settings apply */ }
}

let timers = []
onMounted(async () => {
  measure()
  window.addEventListener('resize', measure)
  document.addEventListener('visibilitychange', keepAwake)
  keepAwake()
  await load()
  measure()
  try {
    const QRCode = await import('qrcode')
    qr.value = await QRCode.toDataURL(`${window.location.origin}/products`, {
      margin: 0, width: 360, color: { dark: '#0e0c0a', light: '#f4ece1' }
    })
  } catch { /* no QR code */ }
  timers = [
    setInterval(nextPage, seconds * 1000),
    setInterval(load, 60_000),
    setInterval(() => { now.value = new Date() }, 10_000),
    // A fresh start twice a day picks up new versions of the site.
    setTimeout(() => window.location.reload(), 12 * 3600_000)
  ]
})

onBeforeUnmount(() => {
  timers.forEach(clearInterval)
  window.removeEventListener('resize', measure)
  document.removeEventListener('visibilitychange', keepAwake)
  wakeLock?.release?.()
})
</script>

<style scoped>
/* Everything is sized in em from one base, so the layout keeps its
   proportions on any screen: 1080p, 4K, landscape or portrait. */
.board {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: grid;
  grid-template-columns: 27em 1fr;
  grid-template-rows: auto 1fr auto;
  grid-template-areas:
    'head head'
    'feature menu'
    'foot foot';
  gap: 0 3em;
  padding: 2.4em 3em 1.6em;
  font-size: min(1vw, 1.7778vh);
  color: #f4ece1;
  background:
    radial-gradient(60% 70% at 15% 55%, rgba(230, 161, 90, 0.16), transparent 70%),
    radial-gradient(50% 60% at 100% 0%, rgba(210, 96, 63, 0.10), transparent 70%),
    #0e0c0a;
  overflow: hidden;
  cursor: none;
  user-select: none;
}

.board.is-portrait {
  font-size: min(1.7778vw, 1vh);
  grid-template-columns: 1fr;
  grid-template-rows: auto auto 1fr auto;
  grid-template-areas: 'head' 'feature' 'menu' 'foot';
  gap: 2em;
  padding: 3em 3em 2em;
}

/* Header */
.board-head {
  grid-area: head;
  display: flex;
  flex-wrap: wrap;
  gap: 1em 2em;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 1.6em;
  border-bottom: 1px solid rgba(244, 236, 225, 0.1);
  margin-bottom: 2em;
}

.is-portrait .board-head { margin-bottom: 0; }

.board-brand {
  display: flex;
  align-items: baseline;
  gap: 1.4em;
}

.board-logo {
  font-family: 'Instrument Serif', Georgia, serif;
  font-size: 3.4em;
  line-height: 1;
}

.board-logo em {
  color: #e6a15a;
}

.board-place {
  font-size: 1.15em;
  color: #b9ab98;
  letter-spacing: 0.02em;
}

.board-status {
  display: flex;
  align-items: center;
  gap: 1.6em;
}

.board-open {
  display: inline-flex;
  align-items: center;
  gap: 0.6em;
  padding: 0.55em 1.1em;
  border-radius: 9999px;
  font-size: 1.1em;
  font-weight: 600;
  color: #c7e6c2;
  background: rgba(159, 212, 154, 0.12);
}

.board-open i {
  width: 0.6em;
  height: 0.6em;
  border-radius: 50%;
  background: #9fd49a;
  box-shadow: 0 0 0 0.25em rgba(159, 212, 154, 0.25);
  animation: pulse 2.4s ease-in-out infinite;
}

.board-open.is-closed {
  color: #f0b4a3;
  background: rgba(240, 143, 121, 0.12);
}

.board-open.is-closed i {
  background: #f08f79;
  box-shadow: none;
  animation: none;
}

.board-clock {
  font-size: 2.2em;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

/* Feature */
.board-feature {
  grid-area: feature;
  display: flex;
  flex-direction: column;
  gap: 1.6em;
  min-height: 0;
}

.feature-card {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.is-portrait .feature-card {
  flex: none;
  display: grid;
  grid-template-columns: 20em 1fr;
  grid-template-rows: auto auto 1fr;
  column-gap: 2.4em;
  align-content: center;
}

.is-portrait .feature-card .board-eyebrow { grid-column: 2; }
.is-portrait .feature-stage { grid-row: 1 / span 3; grid-column: 1; }
.is-portrait .feature-name { grid-column: 2; }
.is-portrait .feature-price { grid-column: 2; align-self: start; }

.board-eyebrow {
  font-size: 1em;
  font-weight: 700;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: #e6a15a;
}

.feature-stage {
  position: relative;
  flex: 1;
  min-height: 0;
  display: grid;
  place-items: center;
  margin: 1em 0;
}

.is-portrait .feature-stage { height: 18em; margin: 0; }

.feature-glow {
  position: absolute;
  inset: 12% 8%;
  border-radius: 50%;
  background: radial-gradient(closest-side, rgba(230, 161, 90, 0.35), transparent);
  filter: blur(1.5em);
}

.feature-img {
  position: relative;
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 2em 2.4em rgba(0, 0, 0, 0.6));
  animation: float 7s ease-in-out infinite;
}

.feature-name {
  font-family: 'Instrument Serif', Georgia, serif;
  font-size: 3.6em;
  line-height: 1;
}

.feature-price {
  margin-top: 0.3em;
  font-size: 2em;
  font-weight: 700;
  color: #f2c48d;
}

.board-qr {
  display: flex;
  align-items: center;
  gap: 1.4em;
  padding: 1.2em;
  border-radius: 1.4em;
  background: rgba(244, 236, 225, 0.05);
  border: 1px solid rgba(244, 236, 225, 0.08);
}

.is-portrait .feature-name { align-self: end; margin-top: 0.4em; }

.board-qr img {
  width: 7.5em;
  height: 7.5em;
  border-radius: 0.6em;
  padding: 0.5em;
  background: #f4ece1;
}

.qr-title {
  font-size: 1.4em;
  font-weight: 700;
}

.qr-text {
  margin-top: 0.3em;
  font-size: 1em;
  color: #b9ab98;
  line-height: 1.4;
}

.qr-url {
  margin-top: 0.5em;
  font-size: 0.95em;
  color: #e6a15a;
}

/* Menu */
.board-menu {
  grid-area: menu;
  position: relative;
  min-height: 0;
  overflow: hidden;
}

/* Heights here must match ROW_EM and HEADING_EM in the script. */
.menu-page {
  display: grid;
  grid-template-columns: repeat(var(--cols), minmax(0, 1fr));
  gap: 0 4em;
}

.menu-section + .menu-section {
  margin-top: 1.4em;
}

.menu-title {
  height: 1.1em;
  margin-bottom: 0.45em;
  font-family: 'Instrument Serif', Georgia, serif;
  font-size: 3.6em;
  line-height: 1.1;
  letter-spacing: -0.01em;
  animation: item-in 0.8s cubic-bezier(0.16, 1, 0.3, 1) both;
  animation-delay: calc(var(--i) * 70ms);
}

.menu-dots {
  position: absolute;
  top: 1.6em;
  right: 0;
  display: flex;
  gap: 0.6em;
}

.menu-dots i {
  width: 0.7em;
  height: 0.7em;
  border-radius: 50%;
  background: rgba(244, 236, 225, 0.18);
  transition: background 0.4s, transform 0.4s;
}

.menu-dots i.is-on {
  background: #e6a15a;
  transform: scale(1.3);
}

.menu-grid {
  display: grid;
  grid-auto-rows: 7.6em;
  gap: 1.4em;
}

.menu-item {
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 1.4em;
  min-height: 0;
  animation: item-in 0.8s cubic-bezier(0.16, 1, 0.3, 1) both;
  animation-delay: calc(var(--i) * 70ms);
}

.item-img {
  flex: none;
  display: grid;
  place-items: center;
  width: 7.6em;
  height: 7.6em;
  border-radius: 1.4em;
  background: radial-gradient(closest-side, rgba(230, 161, 90, 0.16), rgba(244, 236, 225, 0.03));
}

.item-img img {
  width: 88%;
  height: 88%;
  object-fit: contain;
  filter: drop-shadow(0 0.6em 0.8em rgba(0, 0, 0, 0.5));
}

.item-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.35em;
}

.item-line {
  display: flex;
  align-items: baseline;
  gap: 0.8em;
}

.item-name {
  min-width: 0;
  font-size: 1.75em;
  font-weight: 600;
  line-height: 1.15;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-dots {
  flex: 1;
  min-width: 0.6em;
  border-bottom: 0.15em dotted rgba(244, 236, 225, 0.22);
  transform: translateY(-0.35em);
}

.item-price {
  flex: none;
  font-size: 1.75em;
  font-weight: 700;
  color: #f2c48d;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.item-desc {
  font-size: 1.1em;
  color: #b9ab98;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.item-tags {
  display: flex;
  gap: 0.5em;
}

.item-tag {
  padding: 0.25em 0.75em;
  border-radius: 9999px;
  font-size: 0.85em;
  font-weight: 600;
  color: #c7e6c2;
  background: rgba(159, 212, 154, 0.1);
}

.menu-item.is-sold-out { opacity: 0.45; }
.menu-item.is-sold-out .item-price { color: #f08f79; font-size: 1.3em; }

.menu-empty {
  font-size: 2em;
  color: #b9ab98;
}

/* Footer */
.board-foot {
  grid-area: foot;
  display: flex;
  align-items: center;
  gap: 2em;
  padding-top: 1.2em;
  font-size: 0.95em;
  color: #7d7061;
}

.board-offline {
  color: #f08f79;
}

.board-progress {
  flex: 1;
  height: 0.25em;
  border-radius: 9999px;
  background: rgba(244, 236, 225, 0.08);
  overflow: hidden;
}

.board-progress i {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, #e6a15a, #f2c48d);
  transform-origin: left;
  animation: progress linear both;
}

/* Motion */
.page-enter-active, .page-leave-active { transition: opacity 0.5s ease, transform 0.6s cubic-bezier(0.16, 1, 0.3, 1); }
.page-enter-from { opacity: 0; transform: translateY(1.5em); }
.page-leave-to { opacity: 0; transform: translateY(-1em); }
.fade-enter-active, .fade-leave-active { transition: opacity 0.45s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.feature-enter-active, .feature-leave-active { transition: opacity 0.6s ease, transform 0.8s cubic-bezier(0.16, 1, 0.3, 1); }
.feature-enter-from { opacity: 0; transform: scale(0.94) translateY(1em); }
.feature-leave-to { opacity: 0; transform: scale(1.03); }

@keyframes item-in {
  from { opacity: 0; transform: translateY(1.2em); }
}

@keyframes float {
  0%, 100% { transform: translateY(0) rotate(-1deg); }
  50% { transform: translateY(-0.8em) rotate(1deg); }
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0.2em rgba(159, 212, 154, 0.25); }
  50% { box-shadow: 0 0 0 0.45em rgba(159, 212, 154, 0.05); }
}

@keyframes progress {
  from { transform: scaleX(0); }
  to { transform: scaleX(1); }
}

@media (prefers-reduced-motion: reduce) {
  .feature-img, .board-open i { animation: none; }
  .menu-item { animation-duration: 0.01s; }
}
</style>
