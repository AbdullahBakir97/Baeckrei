<template>
  <form class="st-page" @submit.prevent="save" @input="dirty = true" @change="dirty = true">
    <p class="st-intro">{{ $t('admin.settings.intro') }}</p>
    <p v-if="error" class="st-alert" role="alert">{{ error }}</p>

    <div v-if="loaded" class="settings-grid">
      <nav class="settings-nav" :aria-label="$t('admin.settings.sections')">
        <a v-for="s in sections" :key="s" :href="`#set-${s}`" class="settings-nav-link">{{ $t(`admin.settings.section.${s}`) }}</a>
      </nav>

      <div class="st-grid">
        <!-- Opening hours -->
        <section id="set-hours" class="st-card">
          <h2 class="st-card-title">{{ $t('admin.settings.section.hours') }} <small>{{ $t('admin.settings.hoursHint') }}</small></h2>
          <div class="hours">
            <div v-for="(day, d) in hours" :key="d" class="hours-row">
              <label class="st-switch hours-day">
                <input v-model="day.open" type="checkbox" @change="day.open && !day.ranges.length && day.ranges.push(['07:00', '18:00'])" /><i></i>
                <span>{{ weekday(d) }}</span>
              </label>
              <div v-if="day.open" class="hours-ranges">
                <div v-for="(range, r) in day.ranges" :key="r" class="hours-range">
                  <input v-model="range[0]" type="time" class="st-input" required :aria-label="$t('admin.settings.opens', { day: weekday(d) })" />
                  <span>–</span>
                  <input v-model="range[1]" type="time" class="st-input" required :aria-label="$t('admin.settings.closes', { day: weekday(d) })" />
                  <button v-if="day.ranges.length > 1" type="button" class="icon-btn" :aria-label="$t('admin.settings.removeBreak')" @click="day.ranges.splice(r, 1); dirty = true"><font-awesome-icon icon="xmark" /></button>
                </div>
                <button v-if="day.ranges.length < 3" type="button" class="st-link text-xs" @click="day.ranges.push(['14:00', '18:00']); dirty = true">+ {{ $t('admin.settings.addBreak') }}</button>
              </div>
              <span v-else class="text-sm text-cream-faint">{{ $t('admin.settings.closed') }}</span>
            </div>
          </div>
          <button type="button" class="st-btn st-btn-ghost st-btn-sm mt-4" @click="copyMonday">{{ $t('admin.settings.copyMonday') }}</button>
        </section>

        <!-- Closing days -->
        <section id="set-closing" class="st-card">
          <h2 class="st-card-title">{{ $t('admin.settings.section.closing') }} <small>{{ $t('admin.settings.closingHint') }}</small></h2>
          <ul v-if="closures.length" class="closures">
            <li v-for="c in closures" :key="c.id">
              <font-awesome-icon icon="calendar-xmark" class="text-crust" />
              <span class="flex-1"><strong>{{ range(c) }}</strong> <span v-if="c.label" class="text-cream-faint">· {{ c.label }}</span></span>
              <button type="button" class="icon-btn" :aria-label="$t('admin.common.delete')" @click="removeClosure(c)"><font-awesome-icon icon="trash" /></button>
            </li>
          </ul>
          <p v-else class="text-sm text-cream-faint mb-4">{{ $t('admin.settings.noClosures') }}</p>
          <div class="st-grid sm:grid-cols-4 items-end closure-form">
            <div><label class="st-label" for="cl-start">{{ $t('admin.settings.from') }}</label><input id="cl-start" v-model="closure.start" type="date" class="st-input" /></div>
            <div><label class="st-label" for="cl-end">{{ $t('admin.settings.to') }} <small>({{ $t('admin.common.optional') }})</small></label><input id="cl-end" v-model="closure.end" type="date" class="st-input" :min="closure.start" /></div>
            <div><label class="st-label" for="cl-label">{{ $t('admin.settings.reason') }}</label><input id="cl-label" v-model.trim="closure.label" class="st-input" :placeholder="$t('admin.settings.reasonPlaceholder')" /></div>
            <button type="button" class="st-btn" :disabled="!closure.start" @click="addClosure"><font-awesome-icon icon="plus" /> {{ $t('admin.settings.addClosure') }}</button>
          </div>
        </section>

        <!-- Ordering -->
        <section id="set-ordering" class="st-card st-grid">
          <h2 class="st-card-title !mb-0">{{ $t('admin.settings.section.ordering') }}</h2>
          <div class="flex flex-wrap gap-6">
            <label class="st-switch"><input v-model="form.pickup_enabled" type="checkbox" /><i></i> {{ $t('admin.settings.pickup') }}</label>
            <label class="st-switch"><input v-model="form.delivery_enabled" type="checkbox" /><i></i> {{ $t('admin.settings.delivery') }}</label>
          </div>
          <div class="st-grid st-grid-3">
            <div v-for="f in numberFields" :key="f.key">
              <label class="st-label" :for="`set-${f.key}`">{{ $t(`admin.settings.fields.${f.key}`) }}</label>
              <input :id="`set-${f.key}`" v-model="form[f.key]" type="number" :min="f.min" :step="f.step || 1" class="st-input"
                     :placeholder="String(effective[f.key] ?? '')" />
              <p class="st-hint">{{ $t(`admin.settings.hints.${f.key}`) }}</p>
            </div>
          </div>
        </section>

        <!-- Notice -->
        <section id="set-notice" class="st-card st-grid">
          <h2 class="st-card-title !mb-0">{{ $t('admin.settings.section.notice') }} <small>{{ $t('admin.settings.noticeHint') }}</small></h2>
          <label class="st-switch"><input v-model="form.announcement_active" type="checkbox" /><i></i> {{ $t('admin.settings.showNotice') }}</label>
          <div class="st-grid st-grid-2">
            <div><label class="st-label" for="set-ann">Deutsch</label><input id="set-ann" v-model="form.announcement" class="st-input" maxlength="300" :placeholder="$t('admin.settings.noticePlaceholder')" /></div>
            <div><label class="st-label" for="set-ann-en">English</label><input id="set-ann-en" v-model="form.announcement_en" lang="en" class="st-input" maxlength="300" /></div>
          </div>
        </section>

        <!-- Business -->
        <section id="set-business" class="st-card st-grid">
          <h2 class="st-card-title !mb-0">{{ $t('admin.settings.section.business') }} <small>{{ $t('admin.settings.businessHint') }}</small></h2>
          <div class="st-grid st-grid-2">
            <div v-for="key in businessFields" :key="key" :class="{ 'st-span': key === 'transit' }">
              <label class="st-label" :for="`set-${key}`">{{ $t(`admin.settings.fields.${key}`) }}</label>
              <input :id="`set-${key}`" v-model.trim="form[key]" class="st-input" :type="key === 'email' ? 'email' : 'text'"
                     :placeholder="String(effective[key] || '')" />
              <p v-if="fieldErrors[key]" class="st-error">{{ fieldErrors[key] }}</p>
            </div>
          </div>
          <h3 class="st-label !mt-2">{{ $t('admin.settings.social') }}</h3>
          <div class="st-grid st-grid-3">
            <div v-for="key in ['instagram', 'facebook', 'twitter']" :key="key">
              <label class="st-label" :for="`set-${key}`">{{ key[0].toUpperCase() + key.slice(1) }}</label>
              <input :id="`set-${key}`" v-model.trim="form[key]" type="url" class="st-input" placeholder="https://…" />
              <p v-if="fieldErrors[key]" class="st-error">{{ fieldErrors[key] }}</p>
            </div>
          </div>
        </section>

        <!-- Legal -->
        <section id="set-legal" class="st-card st-grid">
          <h2 class="st-card-title !mb-0">{{ $t('admin.settings.section.legal') }} <small>{{ $t('admin.settings.legalHint') }}</small></h2>
          <div class="st-grid st-grid-2">
            <div v-for="key in ['legal_name', 'owner', 'vat_id', 'register']" :key="key">
              <label class="st-label" :for="`set-${key}`">{{ $t(`admin.settings.fields.${key}`) }}</label>
              <input :id="`set-${key}`" v-model.trim="form[key]" class="st-input" :placeholder="$t(`admin.settings.placeholders.${key}`)" />
            </div>
          </div>
        </section>

        <!-- Notifications -->
        <section id="set-notifications" class="st-card">
          <h2 class="st-card-title">{{ $t('admin.settings.section.notifications') }}</h2>
          <label class="st-label" for="set-notify">{{ $t('admin.settings.fields.notification_email') }}</label>
          <input id="set-notify" v-model.trim="form.notification_email" type="email" class="st-input" :placeholder="effective.notification_email || 'bestellung@…'" />
          <p class="st-hint">{{ $t('admin.settings.notifyHint') }}</p>
          <p v-if="fieldErrors.notification_email" class="st-error">{{ fieldErrors.notification_email }}</p>
        </section>

        <div class="st-savebar" :class="{ 'is-dirty': dirty }">
          <p>{{ dirty ? $t('admin.settings.unsaved') : savedNote }}</p>
          <button type="submit" class="st-btn" :disabled="saving || !dirty">{{ saving ? $t('admin.common.saving') : $t('admin.settings.save') }}</button>
        </div>
      </div>
    </div>
    <p v-else-if="!error" class="st-empty">{{ $t('admin.common.loading') }}</p>
  </form>
</template>

<script setup>
import { onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { onBeforeRouteLeave } from 'vue-router'
import { useI18n } from 'vue-i18n'
import axios from '@/plugins/axios'
import { intlLocale } from '@/i18n'
import { loadShopInfo } from '@/config/business'
import { errorsFrom, formatDate, listOf } from './api'

const { t } = useI18n()
const sections = ['hours', 'closing', 'ordering', 'notice', 'business', 'legal', 'notifications']
const businessFields = ['name', 'phone', 'street', 'house_number', 'postal_code', 'city', 'country', 'email', 'transit']
const numberFields = [
  { key: 'delivery_fee', min: 0, step: 0.1 },
  { key: 'pickup_lead_minutes', min: 0 },
  { key: 'delivery_lead_minutes', min: 0 },
  { key: 'slot_minutes', min: 5 },
  { key: 'slot_days', min: 1 },
  { key: 'slot_capacity', min: 0 }
]
const NUMBERS = numberFields.map(f => f.key)

const form = reactive({})
const effective = ref({})
const hours = ref([])
const closures = ref([])
const closure = reactive({ start: '', end: '', label: '' })
const loaded = ref(false)
const saving = ref(false)
const dirty = ref(false)
const error = ref('')
const savedNote = ref('')
const fieldErrors = reactive({})

const weekday = (d) => new Intl.DateTimeFormat(intlLocale(), { weekday: 'long' }).format(new Date(2024, 0, 1 + d))
const range = (c) => (c.end && c.end !== c.start
  ? `${formatDate(c.start, intlLocale(), false)} – ${formatDate(c.end, intlLocale(), false)}`
  : formatDate(c.start, intlLocale(), false))

function fill(data) {
  Object.assign(form, data.saved)
  for (const key of NUMBERS) form[key] = data.saved[key] ?? ''
  effective.value = data.effective
  const source = Object.keys(data.saved.opening_hours || {}).length ? data.saved.opening_hours : data.effective.opening_hours
  hours.value = Array.from({ length: 7 }, (_, d) => {
    const ranges = (source[String(d)] || []).map(r => [...r])
    return { open: ranges.length > 0, ranges }
  })
  savedNote.value = data.saved.updated_at ? t('admin.settings.savedAt', { date: formatDate(data.saved.updated_at, intlLocale()) }) : t('admin.settings.defaults')
}

onMounted(async () => {
  try {
    const [settings, days] = await Promise.all([axios.get('/api/studio/settings/'), axios.get('/api/studio/closing-days/', { params: { upcoming: 'true' } })])
    fill(settings.data)
    closures.value = listOf(days.data)
    loaded.value = true
  } catch {
    error.value = t('admin.common.loadError')
  }
})

function copyMonday() {
  const monday = hours.value[0]
  for (let d = 1; d < 5; d++) hours.value[d] = { open: monday.open, ranges: monday.ranges.map(r => [...r]) }
  dirty.value = true
}

async function save() {
  saving.value = true
  error.value = ''
  Object.keys(fieldErrors).forEach(k => delete fieldErrors[k])
  const payload = { ...form }
  delete payload.updated_at
  for (const key of NUMBERS) payload[key] = payload[key] === '' || payload[key] === null ? null : Number(payload[key])
  payload.opening_hours = Object.fromEntries(hours.value.map((day, d) => [String(d), day.open ? day.ranges : []]))
  try {
    fill((await axios.patch('/api/studio/settings/', payload)).data)
    dirty.value = false
    loadShopInfo()
  } catch (err) {
    const e = errorsFrom(err)
    Object.assign(fieldErrors, e.fields)
    error.value = e.fields.opening_hours || e.message || t('admin.common.checkFields')
  } finally {
    saving.value = false
  }
}

async function addClosure() {
  try {
    const { data } = await axios.post('/api/studio/closing-days/', { start: closure.start, end: closure.end || null, label: closure.label })
    closures.value = [...closures.value, data].sort((a, b) => a.start.localeCompare(b.start))
    Object.assign(closure, { start: '', end: '', label: '' })
    loadShopInfo()
  } catch (err) {
    const e = errorsFrom(err)
    error.value = e.message || Object.values(e.fields)[0] || t('admin.common.saveError')
  }
}

async function removeClosure(c) {
  try {
    await axios.delete(`/api/studio/closing-days/${c.id}/`)
    closures.value = closures.value.filter(x => x.id !== c.id)
    loadShopInfo()
  } catch {
    error.value = t('admin.common.deleteError')
  }
}

const beforeUnload = (event) => { if (dirty.value) { event.preventDefault(); event.returnValue = '' } }
onMounted(() => window.addEventListener('beforeunload', beforeUnload))
onBeforeUnmount(() => window.removeEventListener('beforeunload', beforeUnload))
onBeforeRouteLeave(() => (dirty.value ? window.confirm(t('admin.settings.leave')) : true))
</script>

<style scoped>
.settings-grid { display: grid; gap: 1.5rem; align-items: start; }
@media (min-width: 1200px) { .settings-grid { grid-template-columns: 12rem minmax(0, 1fr); } }
.settings-nav { position: sticky; top: 1.5rem; display: none; gap: 0.15rem; }
@media (min-width: 1200px) { .settings-nav { display: grid; } }
.settings-nav-link { padding: 0.5rem 0.75rem; border-radius: 0.75rem; font-size: 0.85rem; color: #b9ab98; }
.settings-nav-link:hover { color: #f4ece1; background: rgba(244, 236, 225, 0.05); }
.hours { display: grid; gap: 0.25rem; }
.hours-row { display: grid; grid-template-columns: 11rem 1fr; align-items: center; gap: 1rem; padding: 0.6rem 0; border-bottom: 1px solid rgba(244, 236, 225, 0.06); }
.hours-row:last-child { border-bottom: 0; }
@media (max-width: 640px) { .hours-row { grid-template-columns: 1fr; gap: 0.5rem; } }
.hours-ranges { display: flex; flex-wrap: wrap; align-items: center; gap: 0.5rem 1rem; }
.hours-range { display: flex; align-items: center; gap: 0.4rem; color: #85766a; }
.hours-range .st-input { width: 7.5rem; padding: 0.4rem 0.6rem; }
.icon-btn { padding: 0.3rem 0.45rem; border-radius: 0.5rem; font-size: 0.8rem; color: #85766a; }
.icon-btn:hover { color: #f4ece1; background: rgba(244, 236, 225, 0.07); }
.closures { display: grid; gap: 0.3rem; margin-bottom: 1rem; }
.closures li { display: flex; align-items: center; gap: 0.75rem; padding: 0.6rem 0.8rem; border-radius: 0.9rem; font-size: 0.9rem; color: #f4ece1; background: rgba(244, 236, 225, 0.04); }
.st-savebar:not(.is-dirty) { border-color: rgba(244, 236, 225, 0.1); }
</style>
