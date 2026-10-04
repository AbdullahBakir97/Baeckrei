<template>
  <div class="st-page">
    <div class="st-bar">
      <router-link to="/admin/screens" class="st-link text-sm"><font-awesome-icon icon="arrow-left" /> {{ $t('admin.screens.back') }}</router-link>
      <div v-if="screen" class="flex flex-wrap items-center gap-2">
        <span class="st-chip" :class="screen.online ? 'is-green' : ''">{{ screen.online ? $t('admin.screens.online') : $t('admin.screens.offline') }}</span>
        <span class="st-chip is-amber">{{ $t('admin.screens.code') }} {{ screen.code }}</span>
        <a :href="`/menu-board/${screen.slug}`" target="_blank" rel="noopener" class="st-btn st-btn-ghost st-btn-sm"><font-awesome-icon icon="up-right-from-square" /> {{ $t('admin.screens.open') }}</a>
      </div>
    </div>
    <p v-if="error" class="st-alert" role="alert">{{ error }}</p>

    <div v-if="screen" class="editor">
      <!-- Controls -->
      <div class="st-grid content-start">
        <div class="st-tabs self-start" role="tablist">
          <button v-for="tab in tabs" :key="tab" type="button" role="tab" class="st-tab" :class="{ 'is-active': current === tab }"
                  :aria-selected="current === tab" @click="current = tab">{{ $t(`admin.screens.tabs.${tab}`) }}</button>
        </div>

        <!-- Design -->
        <template v-if="current === 'design'">
          <section class="st-card st-grid">
            <div class="st-grid st-grid-2">
              <div>
                <label class="st-label" for="sc-name">{{ $t('admin.screens.name') }}</label>
                <input id="sc-name" v-model.trim="screen.name" class="st-input" maxlength="100" required @input="touch" />
              </div>
              <label class="st-switch self-end pb-2"><input v-model="screen.is_default" type="checkbox" @change="touch" /><i></i> {{ $t('admin.screens.makeDefault') }}</label>
            </div>
            <div>
              <p class="st-label">{{ $t('admin.screens.layout') }}</p>
              <div class="choice-grid">
                <button v-for="l in layouts" :key="l" type="button" class="choice" :class="{ 'is-on': screen.layout === l }" @click="set('layout', l)">
                  <span class="layout-icon" :class="`is-${l}`"><i></i><i></i><i></i><i></i></span>
                  <strong>{{ $t(`admin.screens.layouts.${l}`) }}</strong>
                  <small>{{ $t(`admin.screens.layoutHints.${l}`) }}</small>
                </button>
              </div>
            </div>
            <div>
              <p class="st-label">{{ $t('admin.screens.theme') }}</p>
              <div class="theme-row">
                <button v-for="th in themes" :key="th.key" type="button" class="theme" :class="{ 'is-on': screen.theme === th.key }" @click="set('theme', th.key)">
                  <span class="theme-swatch" :style="{ background: th.bg, color: th.accent, borderColor: th.text }">Aa</span>
                  {{ $t(`admin.screens.themes.${th.key}`) }}
                </button>
              </div>
            </div>
            <div class="st-grid st-grid-3">
              <div v-if="screen.theme === 'custom'">
                <label class="st-label" for="sc-bg">{{ $t('admin.screens.background') }}</label>
                <input id="sc-bg" v-model="screen.background_color" type="color" class="color" @input="touch" />
              </div>
              <div v-if="screen.theme === 'custom'">
                <label class="st-label" for="sc-text">{{ $t('admin.screens.textColor') }}</label>
                <input id="sc-text" v-model="screen.text_color" type="color" class="color" @input="touch" />
              </div>
              <div>
                <label class="st-label" for="sc-accent">{{ $t('admin.screens.accent') }}</label>
                <div class="flex items-center gap-2">
                  <input id="sc-accent" :value="screen.accent_color || themeAccent" type="color" class="color" @input="set('accent_color', $event.target.value)" />
                  <button v-if="screen.accent_color" type="button" class="st-link text-xs" @click="set('accent_color', '')">{{ $t('admin.screens.reset') }}</button>
                </div>
              </div>
              <div>
                <p class="st-label">{{ $t('admin.screens.font') }}</p>
                <div class="st-tabs">
                  <button v-for="f in ['serif', 'sans']" :key="f" type="button" class="st-tab" :class="{ 'is-active': screen.font === f }" @click="set('font', f)">
                    {{ $t(`admin.screens.fonts.${f}`) }}
                  </button>
                </div>
              </div>
            </div>
            <div class="st-grid st-grid-2">
              <div>
                <p class="st-label">{{ $t('admin.screens.backgroundPhoto') }}</p>
                <div class="flex items-center gap-3">
                  <img v-if="screen.background_image_url" :src="screen.background_image_url" alt="" class="st-thumb !w-20" />
                  <input type="file" accept="image/jpeg,image/png,image/webp" :aria-label="$t('admin.screens.backgroundPhoto')" @change="uploadBackground" />
                </div>
                <button v-if="screen.background_image_url" type="button" class="st-link text-xs mt-2" @click="removeBackground">{{ $t('admin.screens.removePhoto') }}</button>
              </div>
              <div v-if="screen.background_image_url">
                <label class="st-label" for="sc-dim">{{ $t('admin.screens.dim', { n: screen.background_dim }) }}</label>
                <input id="sc-dim" v-model.number="screen.background_dim" type="range" min="0" max="90" step="5" class="w-full accent-[#e6a15a]" @input="touch" />
              </div>
            </div>
            <div class="st-grid st-grid-2">
              <div>
                <label class="st-label" for="sc-lang">{{ $t('admin.screens.language') }}</label>
                <select id="sc-lang" v-model="screen.language" class="st-input" @change="touch">
                  <option value="de">Deutsch</option><option value="en">English</option><option value="alternate">{{ $t('admin.screens.alternate') }}</option>
                </select>
              </div>
              <div>
                <label class="st-label" for="sc-orient">{{ $t('admin.screens.orientation') }}</label>
                <select id="sc-orient" v-model="screen.orientation" class="st-input" @change="touch">
                  <option v-for="o in ['auto', 'rotate-right', 'rotate-left']" :key="o" :value="o">{{ $t(`admin.screens.orientations.${o}`) }}</option>
                </select>
              </div>
            </div>
          </section>
        </template>

        <!-- Content -->
        <template v-if="current === 'content'">
          <section class="st-card st-grid">
            <div class="st-grid st-grid-2">
              <div><label class="st-label" for="sc-head">{{ $t('admin.screens.headline') }} <small>· {{ $t('admin.screens.headlineHint') }}</small></label>
                <input id="sc-head" v-model="screen.headline" class="st-input" maxlength="120" @input="touch" /></div>
              <div><label class="st-label" for="sc-head-en">{{ $t('admin.screens.headline') }} (English)</label>
                <input id="sc-head-en" v-model="screen.headline_en" lang="en" class="st-input" maxlength="120" @input="touch" /></div>
              <div><label class="st-label" for="sc-tick">{{ $t('admin.screens.ticker') }} <small>· {{ $t('admin.screens.tickerHint') }}</small></label>
                <input id="sc-tick" v-model="screen.ticker" class="st-input" maxlength="300" @input="touch" /></div>
              <div><label class="st-label" for="sc-tick-en">{{ $t('admin.screens.ticker') }} (English)</label>
                <input id="sc-tick-en" v-model="screen.ticker_en" lang="en" class="st-input" maxlength="300" @input="touch" /></div>
            </div>
            <div class="flex flex-wrap gap-x-6 gap-y-3">
              <label v-for="key in toggles" :key="key" class="st-switch"><input v-model="screen[key]" type="checkbox" @change="touch" /><i></i> {{ $t(`admin.screens.show.${key}`) }}</label>
            </div>
            <div class="st-grid st-grid-3">
              <div>
                <label class="st-label" for="sc-sold">{{ $t('admin.screens.soldOut') }}</label>
                <select id="sc-sold" v-model="screen.sold_out" class="st-input" @change="touch">
                  <option value="mark">{{ $t('admin.screens.soldOutMark') }}</option><option value="hide">{{ $t('admin.screens.soldOutHide') }}</option>
                </select>
              </div>
              <div>
                <label class="st-label" for="sc-sec">{{ $t('admin.screens.seconds', { n: screen.page_seconds }) }}</label>
                <input id="sc-sec" v-model.number="screen.page_seconds" type="range" min="5" max="40" class="w-full accent-[#e6a15a]" @input="touch" />
              </div>
              <div>
                <label class="st-label" for="sc-every">{{ $t('admin.screens.slideEvery', { n: screen.slide_every }) }}</label>
                <input id="sc-every" v-model.number="screen.slide_every" type="range" min="1" max="8" class="w-full accent-[#e6a15a]" @input="touch" />
              </div>
            </div>
          </section>

          <section class="st-card st-grid">
            <h2 class="st-card-title !mb-0">{{ $t('admin.screens.categories') }} <small>{{ $t('admin.screens.categoriesHint') }}</small></h2>
            <label class="st-switch"><input :checked="!screen.categories.length" type="checkbox" @change="toggleAllCategories($event.target.checked)" /><i></i> {{ $t('admin.screens.allCategories') }}</label>
            <ul v-if="screen.categories.length" class="cat-list">
              <li v-for="(id, i) in screen.categories" :key="id">
                <span class="flex-1">{{ categoryName(id) }}</span>
                <button type="button" class="icon-btn" :disabled="i === 0" :aria-label="$t('admin.screens.up')" @click="move(i, -1)">↑</button>
                <button type="button" class="icon-btn" :disabled="i === screen.categories.length - 1" :aria-label="$t('admin.screens.down')" @click="move(i, 1)">↓</button>
                <button type="button" class="icon-btn" :aria-label="$t('admin.common.delete')" @click="screen.categories.splice(i, 1); touch()"><font-awesome-icon icon="xmark" /></button>
              </li>
            </ul>
            <div v-if="screen.categories.length && unusedCategories.length" class="flex flex-wrap gap-2">
              <button v-for="c in unusedCategories" :key="c.id" type="button" class="st-chip hover:text-cream" @click="screen.categories.push(c.id); touch()">+ {{ c.name }}</button>
            </div>
          </section>

          <section class="st-card st-grid">
            <h2 class="st-card-title !mb-0">{{ $t('admin.screens.products') }} <small>{{ $t('admin.screens.productsHint') }}</small></h2>
            <input v-model="productSearch" type="search" class="st-input" :placeholder="$t('admin.screens.searchProducts')" :aria-label="$t('admin.screens.searchProducts')" />
            <ul class="product-picks">
              <li v-for="p in shownProducts" :key="p.id">
                <img v-if="p.image_url" :src="p.image_url" alt="" class="st-thumb" />
                <span class="flex-1 min-w-0"><span class="block truncate text-cream">{{ p.name }}</span><small class="text-cream-faint">{{ p.category?.name }}</small></span>
                <button type="button" class="pick-btn" :class="{ 'is-on': isIn('featured_products', p.id) }" @click="toggle('featured_products', p.id)">★ {{ $t('admin.screens.feature') }}</button>
                <button type="button" class="pick-btn is-hide" :class="{ 'is-on': isIn('hidden_products', p.id) }" @click="toggle('hidden_products', p.id)">{{ $t('admin.screens.hide') }}</button>
              </li>
            </ul>
          </section>
        </template>

        <!-- Promotions -->
        <template v-if="current === 'slides'">
          <section class="st-card st-grid">
            <div class="st-bar">
              <h2 class="st-card-title !mb-0">{{ $t('admin.screens.slides') }} <small>{{ $t('admin.screens.slidesHint') }}</small></h2>
              <button type="button" class="st-btn st-btn-sm" @click="editSlide()"><font-awesome-icon icon="plus" /> {{ $t('admin.screens.addSlide') }}</button>
            </div>
            <p v-if="!slides.length" class="st-empty !py-6">{{ $t('admin.screens.noSlides') }}</p>
            <ul class="slide-list">
              <li v-for="(sl, i) in slides" :key="sl.id" :class="{ 'is-off': !sl.active }">
                <img v-if="sl.image_url" :src="sl.image_url" alt="" class="st-thumb" />
                <span v-else class="st-thumb grid place-items-center text-cream-faint"><font-awesome-icon icon="bullhorn" /></span>
                <span class="flex-1 min-w-0">
                  <span class="block truncate font-semibold text-cream">{{ sl.title }}</span>
                  <small class="text-cream-faint">{{ $t(`admin.screens.slideStyles.${sl.style}`) }} · {{ scheduleText(sl) }}</small>
                </span>
                <button type="button" class="icon-btn" :disabled="i === 0" :aria-label="$t('admin.screens.up')" @click="moveSlide(i, -1)">↑</button>
                <button type="button" class="icon-btn" :disabled="i === slides.length - 1" :aria-label="$t('admin.screens.down')" @click="moveSlide(i, 1)">↓</button>
                <button type="button" class="icon-btn" :aria-label="$t('admin.screens.showInPreview')" @click="pin(sl)"><font-awesome-icon icon="eye" /></button>
                <button type="button" class="st-link text-sm" @click="editSlide(sl)">{{ $t('admin.common.edit') }}</button>
              </li>
            </ul>
          </section>

          <form v-if="slideForm" class="st-card st-grid" @submit.prevent="saveSlide" @input="pinForm">
            <h2 class="st-card-title !mb-0">{{ slideForm.id ? $t('admin.screens.editSlide') : $t('admin.screens.addSlide') }}</h2>
            <div class="st-tabs self-start">
              <button v-for="st in ['product', 'photo', 'text']" :key="st" type="button" class="st-tab" :class="{ 'is-active': slideForm.style === st }"
                      @click="slideForm.style = st; pinForm()">{{ $t(`admin.screens.slideStyles.${st}`) }}</button>
            </div>
            <div class="st-grid st-grid-2">
              <div><label class="st-label" for="sl-title">{{ $t('admin.screens.slideTitle') }}</label><input id="sl-title" v-model="slideForm.title" class="st-input" required maxlength="120" /></div>
              <div><label class="st-label" for="sl-title-en">{{ $t('admin.screens.slideTitle') }} (English)</label><input id="sl-title-en" v-model="slideForm.title_en" lang="en" class="st-input" maxlength="120" /></div>
              <div><label class="st-label" for="sl-text">{{ $t('admin.screens.slideText') }}</label><input id="sl-text" v-model="slideForm.text" class="st-input" maxlength="300" /></div>
              <div><label class="st-label" for="sl-text-en">{{ $t('admin.screens.slideText') }} (English)</label><input id="sl-text-en" v-model="slideForm.text_en" lang="en" class="st-input" maxlength="300" /></div>
              <div><label class="st-label" for="sl-price">{{ $t('admin.screens.slidePrice') }} <small>({{ $t('admin.common.optional') }})</small></label><input id="sl-price" v-model="slideForm.price" type="number" min="0" step="0.01" class="st-input" /></div>
              <div><label class="st-label" for="sl-note">{{ $t('admin.screens.priceNote') }}</label><input id="sl-note" v-model="slideForm.price_note" class="st-input" maxlength="60" :placeholder="$t('admin.screens.priceNotePlaceholder')" /></div>
            </div>
            <div v-if="slideForm.style === 'product'">
              <label class="st-label" for="sl-product">{{ $t('admin.screens.slideProduct') }}</label>
              <select id="sl-product" v-model="slideForm.product" class="st-input" @change="pinForm">
                <option :value="null">—</option>
                <option v-for="p in allProducts" :key="p.id" :value="p.id">{{ p.name }}</option>
              </select>
              <p class="st-hint">{{ $t('admin.screens.slideProductHint') }}</p>
            </div>
            <div v-if="slideForm.style !== 'text'" class="flex items-center gap-3">
              <img v-if="slideImagePreview" :src="slideImagePreview" alt="" class="st-thumb !w-20" />
              <div>
                <label class="st-label" for="sl-image">{{ $t('admin.screens.slideImage') }}</label>
                <input id="sl-image" type="file" accept="image/jpeg,image/png,image/webp" @change="pickSlideImage" />
              </div>
            </div>
            <fieldset class="st-grid st-grid-2">
              <legend class="st-label">{{ $t('admin.screens.when') }} <small>· {{ $t('admin.screens.whenHint') }}</small></legend>
              <div class="flex gap-2"><input v-model="slideForm.start_date" type="date" class="st-input" :aria-label="$t('admin.settings.from')" />
                <input v-model="slideForm.end_date" type="date" class="st-input" :aria-label="$t('admin.settings.to')" /></div>
              <div class="flex gap-2"><input v-model="slideForm.start_time" type="time" class="st-input" :aria-label="$t('admin.screens.fromTime')" />
                <input v-model="slideForm.end_time" type="time" class="st-input" :aria-label="$t('admin.screens.toTime')" /></div>
              <div class="st-span flex flex-wrap gap-2">
                <button v-for="d in 7" :key="d" type="button" class="day-chip" :class="{ 'is-on': slideForm.weekdays.includes(d - 1) }" @click="toggleDay(d - 1)">{{ weekday(d - 1) }}</button>
              </div>
            </fieldset>
            <div class="flex flex-wrap items-center gap-3">
              <label class="st-switch"><input v-model="slideForm.active" type="checkbox" /><i></i> {{ $t('admin.screens.slideActive') }}</label>
              <label class="text-sm text-cream/80 flex items-center gap-2">{{ $t('admin.screens.slideSeconds') }}
                <input v-model.number="slideForm.seconds" type="number" min="5" max="60" class="st-input !w-20" :placeholder="String(screen.page_seconds)" /></label>
            </div>
            <div class="flex gap-2">
              <button type="submit" class="st-btn" :disabled="busy">{{ $t('admin.common.save') }}</button>
              <button type="button" class="st-btn st-btn-ghost" @click="slideForm = null; pin(null)">{{ $t('admin.common.cancel') }}</button>
              <button v-if="slideForm.id" type="button" class="st-btn st-btn-danger ml-auto" @click="removeSlide"><font-awesome-icon icon="trash" /></button>
            </div>
          </form>
        </template>

        <!-- Device -->
        <template v-if="current === 'device'">
          <section class="st-card st-grid">
            <div class="device-code">
              <p class="st-label">{{ $t('admin.screens.code') }}</p>
              <p class="big-code">{{ screen.code }}</p>
              <p class="st-hint">{{ $t('admin.screens.codeLong', { url: tvUrl }) }}</p>
            </div>
            <div class="flex flex-wrap items-center gap-4">
              <img v-if="qrUrl" :src="qrUrl" alt="" class="w-28 h-28 rounded-xl bg-cream p-2" />
              <div class="st-grid !gap-2 text-sm text-cream/80">
                <p>{{ $t('admin.screens.address') }} <a :href="boardUrl" target="_blank" rel="noopener" class="st-link break-all">{{ boardUrl }}</a></p>
                <p>{{ $t('admin.screens.status') }}: <b>{{ screen.online ? $t('admin.screens.online') : (screen.last_seen_at ? $t('admin.screens.offline') : $t('admin.screens.never')) }}</b>
                  <template v-if="screen.last_seen_info?.width"> · {{ screen.last_seen_info.width }}×{{ screen.last_seen_info.height }}</template></p>
                <p v-if="screen.last_seen_info?.agent" class="text-xs text-cream-faint break-all">{{ screen.last_seen_info.agent }}</p>
              </div>
            </div>
            <div class="flex flex-wrap gap-2">
              <button type="button" class="st-btn st-btn-ghost" @click="reload"><font-awesome-icon icon="rotate" /> {{ $t('admin.screens.reloadNow') }}</button>
              <button type="button" class="st-btn st-btn-ghost" @click="duplicate"><font-awesome-icon icon="copy" /> {{ $t('admin.screens.duplicate') }}</button>
              <button type="button" class="st-btn st-btn-danger ml-auto" @click="remove"><font-awesome-icon icon="trash" /> {{ $t('admin.screens.deleteScreen') }}</button>
            </div>
            <p v-if="notice" class="st-success">{{ notice }}</p>
          </section>
        </template>

        <div class="st-savebar" :class="{ 'is-dirty': dirty }">
          <p>{{ dirty ? $t('admin.screens.unsaved') : $t('admin.screens.live') }}</p>
          <button type="button" class="st-btn" :disabled="busy || !dirty" @click="save">{{ busy ? $t('admin.common.saving') : $t('admin.screens.save') }}</button>
        </div>
      </div>

      <!-- Live preview -->
      <aside class="preview">
        <div class="preview-bar">
          <span>{{ $t('admin.screens.preview') }}</span>
          <div class="st-tabs">
            <button type="button" class="st-tab" :class="{ 'is-active': !upright }" @click="upright = false"><font-awesome-icon icon="display" /></button>
            <button type="button" class="st-tab" :class="{ 'is-active': upright }" @click="upright = true"><font-awesome-icon icon="mobile-screen" /></button>
          </div>
        </div>
        <div ref="frameBox" class="preview-frame" :class="{ 'is-upright': upright }" :style="{ '--s': scale }">
          <iframe ref="frame" :src="`/menu-board/${screen.slug}?preview=1`" :style="frameSize" title="Preview" @load="post"></iframe>
        </div>
        <p class="st-hint">{{ $t('admin.screens.previewHint') }}</p>
      </aside>
    </div>
    <p v-else-if="!error" class="st-empty">{{ $t('admin.common.loading') }}</p>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { onBeforeRouteLeave, useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import axios from '@/plugins/axios'
import { intlLocale } from '@/i18n'
import { errorsFrom, listOf } from './api'
import { refreshStudio } from '@/composables/useStudioSummary'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const tabs = ['design', 'content', 'slides', 'device']
const layouts = ['columns', 'grid', 'list', 'spotlight']
const themes = [
  { key: 'oven', bg: '#0e0c0a', text: '#f4ece1', accent: '#e6a15a' },
  { key: 'paper', bg: '#f6efe4', text: '#1d1712', accent: '#b6722c' },
  { key: 'espresso', bg: '#24170f', text: '#f6e7d3', accent: '#f0b86e' },
  { key: 'sage', bg: '#e8ede2', text: '#1f2a1e', accent: '#4f7d43' },
  { key: 'custom', bg: 'conic-gradient(#e6a15a, #4f7d43, #24170f, #f6efe4, #e6a15a)', text: '#fff', accent: '#fff' }
]
const toggles = ['show_prices', 'show_descriptions', 'show_images', 'show_tags', 'show_qr', 'show_clock', 'show_status']

const screen = ref(null)
const slides = ref([])
const allCategories = ref([])
const allProducts = ref([])
const current = ref('design')
const dirty = ref(false)
const busy = ref(false)
const error = ref('')
const notice = ref('')
const productSearch = ref('')
const slideForm = ref(null)
const slideFile = ref(null)
const slideImagePreview = ref(null)
const upright = ref(false)
const frame = ref(null)
const frameBox = ref(null)
const boxWidth = ref(640)
const qrUrl = ref('')

const tvUrl = `${window.location.host}/tv`
const boardUrl = computed(() => `${window.location.origin}/menu-board/${screen.value?.slug}`)
const themeAccent = computed(() => themes.find(th => th.key === screen.value?.theme)?.accent || '#e6a15a')
const frameSize = computed(() => (upright.value ? { width: '1080px', height: '1920px' } : { width: '1920px', height: '1080px' }))
const scale = computed(() => boxWidth.value / (upright.value ? 1080 : 1920))

async function load() {
  try {
    const { data } = await axios.get(`/api/studio/menu-screens/${route.params.id}/`)
    const board = (await axios.get(`/api/menu-screens/${data.slug}/board/`, { params: { preview: 1 } })).data
    allCategories.value = board.categories
    allProducts.value = board.products
    slides.value = listOf((await axios.get('/api/studio/menu-slides/', { params: { screen: data.id } })).data)
    screen.value = { ...data, background_color: data.background_color || '#14110e', text_color: data.text_color || '#f4ece1' }
    upright.value = data.orientation !== 'auto'
    const QRCode = await import('qrcode')
    qrUrl.value = await QRCode.toDataURL(`${window.location.origin}/menu-board/${data.slug}`, { margin: 0, width: 240 })
    await nextTick()
    observe()
  } catch {
    error.value = t('admin.common.loadError')
  }
}
onMounted(load)

let observer
function observe() {
  if (!frameBox.value) return
  observer = new ResizeObserver(() => { boxWidth.value = frameBox.value.clientWidth })
  observer.observe(frameBox.value)
}
onBeforeUnmount(() => observer?.disconnect())

// ---- preview ---------------------------------------------------------------------
let pinned = null
function publicSlide(sl) {
  const product = allProducts.value.find(p => p.id === sl.product)
  return { ...sl, image_url: sl.image_url || product?.image_url || null }
}
function post() {
  if (!frame.value?.contentWindow || !screen.value) return
  frame.value.contentWindow.postMessage(JSON.parse(JSON.stringify({
    type: 'board-preview',
    screen: screen.value,
    slides: slides.value.filter(sl => sl.active).map(publicSlide),
    pin: pinned
  })), window.location.origin)
}
let postTimer
const schedulePost = () => { clearTimeout(postTimer); postTimer = setTimeout(post, 120) }
watch(screen, schedulePost, { deep: true })
watch(slides, schedulePost, { deep: true })
const onReady = (event) => { if (event.data?.type === 'board-ready') post() }
onMounted(() => window.addEventListener('message', onReady))
onBeforeUnmount(() => window.removeEventListener('message', onReady))

function pin(slide) {
  pinned = slide ? publicSlide(slide) : null
  post()
}
function pinForm() {
  if (!slideForm.value) return
  pin({ ...slideForm.value, image_url: slideImagePreview.value })
}

// ---- screen ----------------------------------------------------------------------
const touch = () => { dirty.value = true }
function set(key, value) { screen.value[key] = value; touch() }

const DESIGN = ['name', 'is_default', 'layout', 'theme', 'font', 'background_color', 'text_color', 'accent_color', 'background_dim',
  'orientation', 'language', 'headline', 'headline_en', 'ticker', 'ticker_en', 'categories', 'featured_products', 'hidden_products',
  'show_prices', 'show_descriptions', 'show_images', 'show_tags', 'show_qr', 'show_clock', 'show_status', 'sold_out', 'page_seconds', 'slide_every']

async function save() {
  busy.value = true
  error.value = ''
  try {
    const payload = Object.fromEntries(DESIGN.map(key => [key, screen.value[key]]))
    if (screen.value.theme !== 'custom') { payload.background_color = ''; payload.text_color = '' }
    const { data } = await axios.patch(`/api/studio/menu-screens/${screen.value.id}/`, payload)
    screen.value = { ...screen.value, ...data, background_color: screen.value.background_color, text_color: screen.value.text_color }
    dirty.value = false
    refreshStudio()
  } catch (err) {
    const e = errorsFrom(err)
    error.value = e.message || Object.values(e.fields)[0] || t('admin.common.saveError')
  } finally {
    busy.value = false
  }
}

async function uploadBackground(event) {
  const file = event.target.files?.[0]
  if (!file) return
  const form = new FormData()
  form.append('background_image', file)
  try {
    const { data } = await axios.patch(`/api/studio/menu-screens/${screen.value.id}/`, form, { headers: { 'Content-Type': 'multipart/form-data' }, timeout: 60000 })
    screen.value.background_image_url = data.background_image_url
  } catch (err) { error.value = errorsFrom(err).message || t('admin.common.saveError') }
}
async function removeBackground() {
  try {
    await axios.patch(`/api/studio/menu-screens/${screen.value.id}/`, { remove_background_image: true })
    screen.value.background_image_url = null
  } catch { error.value = t('admin.common.saveError') }
}

const categoryName = (id) => allCategories.value.find(c => String(c.id) === String(id))?.name || '—'
const unusedCategories = computed(() => allCategories.value.filter(c => !screen.value.categories.map(String).includes(String(c.id))))
function toggleAllCategories(all) {
  screen.value.categories = all ? [] : allCategories.value.map(c => c.id)
  touch()
}
function move(i, delta) {
  const list = screen.value.categories
  ;[list[i], list[i + delta]] = [list[i + delta], list[i]]
  touch()
}
const shownProducts = computed(() => allProducts.value.filter(p => !productSearch.value || p.name.toLowerCase().includes(productSearch.value.toLowerCase())))
const isIn = (key, id) => (screen.value[key] || []).map(String).includes(String(id))
function toggle(key, id) {
  const list = (screen.value[key] || []).map(String)
  screen.value[key] = list.includes(String(id)) ? list.filter(x => x !== String(id)) : [...list, String(id)]
  touch()
}

async function reload() {
  try {
    await axios.post(`/api/studio/menu-screens/${screen.value.id}/reload/`)
    notice.value = t('admin.screens.reloadSent', { name: screen.value.name })
  } catch { error.value = t('admin.common.saveError') }
}
async function duplicate() {
  try {
    const { data } = await axios.post(`/api/studio/menu-screens/${screen.value.id}/duplicate/`)
    router.push(`/admin/screens/${data.id}`).then(() => router.go(0))
  } catch { error.value = t('admin.common.saveError') }
}
async function remove() {
  if (!window.confirm(t('admin.screens.confirmDelete', { name: screen.value.name }))) return
  try {
    await axios.delete(`/api/studio/menu-screens/${screen.value.id}/`)
    dirty.value = false
    refreshStudio()
    router.push('/admin/screens')
  } catch { error.value = t('admin.common.deleteError') }
}

// ---- promotions -------------------------------------------------------------------
const weekday = (d) => new Intl.DateTimeFormat(intlLocale(), { weekday: 'short' }).format(new Date(2024, 0, 1 + d))
function scheduleText(sl) {
  const parts = []
  if (!sl.active) parts.push(t('admin.screens.paused'))
  if (sl.start_date || sl.end_date) parts.push([sl.start_date, sl.end_date].filter(Boolean).join(' – '))
  if (sl.start_time || sl.end_time) parts.push(`${(sl.start_time || '').slice(0, 5)}–${(sl.end_time || '').slice(0, 5)}`)
  if (sl.weekdays?.length) parts.push(sl.weekdays.map(weekday).join(', '))
  return parts.join(' · ') || t('admin.screens.always')
}

function editSlide(sl) {
  slideFile.value = null
  slideForm.value = sl
    ? { ...sl, weekdays: [...(sl.weekdays || [])], start_time: sl.start_time?.slice(0, 5) || '', end_time: sl.end_time?.slice(0, 5) || '' }
    : { id: null, style: 'product', title: '', title_en: '', text: '', text_en: '', price: '', price_note: '', price_note_en: '', product: null,
        active: true, seconds: null, start_date: '', end_date: '', start_time: '', end_time: '', weekdays: [] }
  slideImagePreview.value = sl?.image_url || null
  pinForm()
}
function toggleDay(d) {
  const days = slideForm.value.weekdays
  slideForm.value.weekdays = days.includes(d) ? days.filter(x => x !== d) : [...days, d].sort()
}
function pickSlideImage(event) {
  const file = event.target.files?.[0]
  if (!file) return
  slideFile.value = file
  slideImagePreview.value = URL.createObjectURL(file)
  pinForm()
}

async function saveSlide() {
  busy.value = true
  error.value = ''
  const f = slideForm.value
  const payload = {
    screen: screen.value.id, style: f.style, title: f.title, title_en: f.title_en, text: f.text, text_en: f.text_en,
    price: f.price === '' || f.price === null ? null : f.price, price_note: f.price_note, price_note_en: f.price_note_en,
    product: f.style === 'product' ? f.product : null, active: f.active, seconds: f.seconds || null,
    start_date: f.start_date || null, end_date: f.end_date || null, start_time: f.start_time || null, end_time: f.end_time || null,
    weekdays: f.weekdays, order: f.id ? f.order : slides.value.length
  }
  try {
    let { data } = f.id ? await axios.patch(`/api/studio/menu-slides/${f.id}/`, payload) : await axios.post('/api/studio/menu-slides/', payload)
    if (slideFile.value) {
      const form = new FormData()
      form.append('image', slideFile.value)
      data = (await axios.patch(`/api/studio/menu-slides/${data.id}/`, form, { headers: { 'Content-Type': 'multipart/form-data' }, timeout: 60000 })).data
    }
    const i = slides.value.findIndex(s => s.id === data.id)
    if (i >= 0) slides.value[i] = data
    else slides.value.push(data)
    slideForm.value = null
    pin(null)
  } catch (err) {
    const e = errorsFrom(err)
    error.value = e.message || Object.entries(e.fields).map(([k, v]) => `${k}: ${v}`)[0] || t('admin.common.saveError')
  } finally {
    busy.value = false
  }
}

async function removeSlide() {
  try {
    await axios.delete(`/api/studio/menu-slides/${slideForm.value.id}/`)
    slides.value = slides.value.filter(s => s.id !== slideForm.value.id)
    slideForm.value = null
    pin(null)
  } catch { error.value = t('admin.common.deleteError') }
}

async function moveSlide(i, delta) {
  const list = slides.value
  ;[list[i], list[i + delta]] = [list[i + delta], list[i]]
  try {
    await Promise.all(list.map((sl, order) => sl.order !== order
      ? axios.patch(`/api/studio/menu-slides/${sl.id}/`, { order }).then(() => { sl.order = order })
      : null))
  } catch { error.value = t('admin.common.saveError') }
}

onBeforeRouteLeave(() => (dirty.value ? window.confirm(t('admin.settings.leave')) : true))
</script>

<style scoped>
.editor { display: grid; gap: 1.5rem; align-items: start; }
@media (min-width: 1280px) { .editor { grid-template-columns: minmax(0, 1fr) minmax(0, 1.05fr); } }
.preview { position: sticky; top: 1.5rem; display: grid; gap: 0.75rem; }
.preview-bar { display: flex; align-items: center; justify-content: space-between; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #85766a; }
.preview-frame { position: relative; width: 100%; aspect-ratio: 16 / 9; overflow: hidden; border-radius: 1rem; background: #000; box-shadow: 0 0 0 0.5rem #0b0908, 0 30px 60px rgba(0, 0, 0, 0.5); }
.preview-frame.is-upright { width: min(100%, 22rem); aspect-ratio: 9 / 16; margin: 0 auto; }
.preview-frame iframe { position: absolute; top: 0; left: 0; border: 0; transform-origin: top left; transform: scale(var(--s)); }
.choice-grid { display: grid; gap: 0.6rem; grid-template-columns: repeat(auto-fill, minmax(9rem, 1fr)); }
.choice { display: grid; gap: 0.3rem; padding: 0.85rem; border-radius: 1rem; text-align: left; border: 1px solid rgba(244, 236, 225, 0.1); transition: border-color 0.2s, background 0.2s; }
.choice:hover { border-color: rgba(244, 236, 225, 0.25); }
.choice.is-on { border-color: #e6a15a; background: rgba(230, 161, 90, 0.1); }
.choice strong { font-size: 0.85rem; color: #f4ece1; }
.choice small { font-size: 0.72rem; line-height: 1.4; color: #85766a; }
.layout-icon { display: grid; gap: 3px; height: 2.6rem; padding: 4px; border-radius: 0.5rem; background: rgba(244, 236, 225, 0.06); }
.layout-icon i { border-radius: 3px; background: rgba(230, 161, 90, 0.55); }
.layout-icon.is-columns { grid-template-columns: 1fr 1fr 1fr; } .layout-icon.is-columns i:first-child { grid-row: span 2; } .layout-icon.is-columns i:nth-child(4) { display: none; }
.layout-icon.is-grid { grid-template-columns: repeat(4, 1fr); } .layout-icon.is-grid i { height: 100%; }
.layout-icon.is-list { grid-template-columns: 1fr 1fr; } .layout-icon.is-list i { height: 4px; align-self: center; }
.layout-icon.is-spotlight { grid-template-columns: 1fr; } .layout-icon.is-spotlight i:not(:first-child) { display: none; }
.theme-row { display: flex; flex-wrap: wrap; gap: 0.6rem; }
.theme { display: flex; align-items: center; gap: 0.55rem; padding: 0.4rem 0.8rem 0.4rem 0.4rem; border-radius: 999px; font-size: 0.82rem; color: #d9cfc2; border: 1px solid rgba(244, 236, 225, 0.1); }
.theme.is-on { border-color: #e6a15a; background: rgba(230, 161, 90, 0.1); }
.theme-swatch { display: grid; place-items: center; width: 2rem; height: 2rem; border-radius: 50%; font: 700 0.8rem 'Instrument Serif', serif; border: 1px solid; }
.color { width: 3rem; height: 2.4rem; padding: 0.15rem; border-radius: 0.6rem; background: transparent; cursor: pointer; }
.icon-btn { padding: 0.25rem 0.5rem; border-radius: 0.5rem; font-size: 0.85rem; color: #85766a; }
.icon-btn:hover:not(:disabled) { color: #f4ece1; background: rgba(244, 236, 225, 0.07); }
.icon-btn:disabled { opacity: 0.3; }
.cat-list { display: grid; gap: 0.25rem; }
.cat-list li, .slide-list li, .product-picks li { display: flex; align-items: center; gap: 0.6rem; padding: 0.45rem 0.6rem; border-radius: 0.8rem; background: rgba(244, 236, 225, 0.04); font-size: 0.88rem; color: #f4ece1; }
.product-picks { display: grid; gap: 0.3rem; max-height: 26rem; overflow-y: auto; }
.product-picks .st-thumb, .slide-list .st-thumb { width: 2.6rem; height: 2.6rem; object-fit: contain; }
.pick-btn { padding: 0.25rem 0.65rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; color: #b9ab98; background: rgba(244, 236, 225, 0.06); white-space: nowrap; }
.pick-btn.is-on { color: #0e0c0a; background: #f2c48d; }
.pick-btn.is-hide.is-on { color: #f6b8a8; background: rgba(240, 143, 121, 0.15); }
.slide-list { display: grid; gap: 0.35rem; }
.slide-list li.is-off { opacity: 0.55; }
.day-chip { padding: 0.3rem 0.7rem; border-radius: 999px; font-size: 0.8rem; color: #b9ab98; background: rgba(244, 236, 225, 0.06); }
.day-chip.is-on { color: #0e0c0a; background: #f2c48d; }
.device-code { text-align: center; padding: 0.5rem 0 1rem; border-bottom: 1px solid rgba(244, 236, 225, 0.08); }
.big-code { font: 800 4rem/1 'Manrope Variable', monospace; letter-spacing: 0.3em; text-indent: 0.3em; color: #f2c48d; }
.st-savebar:not(.is-dirty) { border-color: rgba(244, 236, 225, 0.1); }
</style>
