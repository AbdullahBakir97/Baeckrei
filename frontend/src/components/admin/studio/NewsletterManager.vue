<template>
  <div class="st-page">
    <div class="st-bar">
      <div class="st-tabs" role="tablist">
        <button type="button" role="tab" class="st-tab" :class="{ 'is-active': tab === 'campaigns' }" :aria-selected="tab === 'campaigns'" @click="tab = 'campaigns'">
          {{ $t('admin.newsletter.campaigns') }}
        </button>
        <button type="button" role="tab" class="st-tab" :class="{ 'is-active': tab === 'subscribers' }" :aria-selected="tab === 'subscribers'" @click="tab = 'subscribers'">
          {{ $t('admin.newsletter.subscribers') }} <span class="st-count">{{ activeCount }}</span>
        </button>
      </div>
      <button v-if="tab === 'campaigns'" type="button" class="st-btn" @click="newCampaign"><font-awesome-icon icon="plus" /> {{ $t('admin.newsletter.new') }}</button>
      <button v-else type="button" class="st-btn st-btn-ghost" @click="exportCsv"><font-awesome-icon icon="download" /> {{ $t('admin.newsletter.export') }}</button>
    </div>

    <p v-if="error" class="st-alert" role="alert">{{ error }}</p>
    <p v-if="notice" class="st-success" role="status">{{ notice }}</p>

    <!-- Campaigns -->
    <div v-if="tab === 'campaigns'" class="nl-grid">
      <div class="st-card !p-0 overflow-hidden">
        <p v-if="!campaigns.length" class="st-empty">{{ $t('admin.newsletter.noCampaigns') }}</p>
        <button v-for="c in campaigns" :key="c.id" type="button" class="nl-row" :class="{ 'is-active': draft?.id === c.id }" @click="openCampaign(c)">
          <span class="min-w-0 flex-1 text-start">
            <strong class="block truncate">{{ c.subject }}</strong>
            <small>{{ c.sent_at ? $t('admin.newsletter.sentTo', { n: c.recipient_count, date: formatDate(c.sent_at, intlLocale()) }) : $t('admin.newsletter.draftFrom', { date: formatDate(c.updated_at, intlLocale()) }) }}</small>
          </span>
          <span class="st-chip" :class="c.sent_at ? 'is-green' : ''">{{ c.sent_at ? $t('admin.newsletter.sent') : $t('admin.newsletter.draft') }}</span>
        </button>
      </div>

      <div v-if="draft" class="st-card st-grid">
        <template v-if="!draft.sent_at">
          <div>
            <label class="st-label" for="nl-subject">{{ $t('admin.newsletter.subject') }}</label>
            <input id="nl-subject" v-model="draft.subject" class="st-input" maxlength="200" required :placeholder="$t('admin.newsletter.subjectPlaceholder')" />
          </div>
          <div>
            <label class="st-label" for="nl-body">{{ $t('admin.newsletter.body') }} <small>· {{ $t('admin.journal.bodyHint') }}</small></label>
            <textarea id="nl-body" v-model="draft.body" class="st-input" rows="12" required></textarea>
          </div>
          <div class="flex flex-wrap gap-2">
            <button type="button" class="st-btn st-btn-ghost" :disabled="busy" @click="saveDraft()">{{ $t('admin.newsletter.saveDraft') }}</button>
            <button type="button" class="st-btn st-btn-ghost" :disabled="busy || !draft.subject" @click="sendTest"><font-awesome-icon icon="envelope" /> {{ $t('admin.newsletter.test') }}</button>
            <button type="button" class="st-btn ms-auto" :disabled="busy || !draft.subject || !draft.body || !activeCount" @click="confirmSend = true">
              <font-awesome-icon icon="paper-plane" /> {{ $t('admin.newsletter.sendTo', { n: activeCount }) }}
            </button>
            <button v-if="draft.id" type="button" class="st-btn st-btn-danger" :aria-label="$t('admin.common.delete')" @click="removeDraft"><font-awesome-icon icon="trash" /></button>
          </div>
        </template>
        <p v-else class="st-success">{{ $t('admin.newsletter.sentTo', { n: draft.recipient_count, date: formatDate(draft.sent_at, intlLocale()) }) }}</p>

        <p class="st-label !mb-0">{{ $t('admin.newsletter.preview') }}</p>
        <div class="mail-preview">
          <p class="mail-logo"><em>{{ business.name.charAt(0) }}</em>{{ business.name.slice(1) }}</p>
          <h3>{{ draft.subject || $t('admin.newsletter.subjectPlaceholder') }}</h3>
          <p v-for="(p, i) in paragraphs(draft.body)" :key="i">{{ p }}</p>
          <span class="mail-button">{{ business.name }} – Online-Shop</span>
          <small>Newsletter abbestellen · Unsubscribe</small>
        </div>
      </div>
      <div v-else class="st-card st-empty">{{ $t('admin.newsletter.pick') }}</div>
    </div>

    <!-- Subscribers -->
    <template v-else>
      <div class="grid gap-4 sm:grid-cols-3">
        <div class="st-card"><p class="stat-label">{{ $t('admin.newsletter.active') }}</p><p class="stat-value">{{ activeCount }}</p></div>
        <div class="st-card"><p class="stat-label">{{ $t('admin.newsletter.unsubscribed') }}</p><p class="stat-value">{{ subscribers.length - activeCount }}</p></div>
        <form class="st-card" @submit.prevent="addSubscriber">
          <label class="st-label" for="nl-add">{{ $t('admin.newsletter.add') }}</label>
          <div class="flex gap-2"><input id="nl-add" v-model.trim="newEmail" type="email" class="st-input" required placeholder="name@example.com" />
            <button type="submit" class="st-btn" :aria-label="$t('admin.newsletter.add')"><font-awesome-icon icon="plus" /></button></div>
          <p class="st-hint">{{ $t('admin.newsletter.addHint') }}</p>
        </form>
      </div>
      <div class="st-bar">
        <div class="st-tabs">
          <button v-for="f in ['all', 'active', 'unsubscribed']" :key="f" type="button" class="st-tab" :class="{ 'is-active': filter === f }" @click="filter = f">
            {{ $t(`admin.newsletter.filters.${f}`) }}
          </button>
        </div>
        <input v-model="search" type="search" class="st-input !w-64" :placeholder="$t('admin.newsletter.search')" :aria-label="$t('admin.newsletter.search')" />
      </div>
      <div class="st-card !p-0 overflow-x-auto">
        <table class="st-table">
          <thead><tr><th>{{ $t('admin.newsletter.email') }}</th><th>{{ $t('admin.newsletter.since') }}</th><th>{{ $t('admin.newsletter.status') }}</th><th></th></tr></thead>
          <tbody>
            <tr v-if="!shown.length"><td colspan="4" class="st-empty">{{ $t('admin.newsletter.noSubscribers') }}</td></tr>
            <tr v-for="s in shown" :key="s.id">
              <td class="font-medium text-cream">{{ s.email }}</td>
              <td>{{ formatDate(s.subscribed_at, intlLocale(), false) }}</td>
              <td><span class="st-chip" :class="s.active ? 'is-green' : ''">{{ s.active ? $t('admin.newsletter.active') : $t('admin.newsletter.unsubscribedOn', { date: formatDate(s.unsubscribed_at, intlLocale(), false) }) }}</span></td>
              <td class="is-right whitespace-nowrap">
                <button v-if="s.active" type="button" class="st-link text-sm me-3" @click="unsubscribe(s)">{{ $t('admin.newsletter.unsubscribe') }}</button>
                <button type="button" class="text-sm text-red-300" @click="removeSubscriber(s)">{{ $t('admin.common.delete') }}</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <!-- Confirm sending -->
    <div v-if="confirmSend" class="st-modal" role="dialog" aria-modal="true" @click.self="confirmSend = false">
      <div class="st-card st-modal-box st-grid">
        <h2 class="st-card-title !mb-0">{{ $t('admin.newsletter.confirmTitle') }}</h2>
        <p class="text-sm text-cream/80">{{ $t('admin.newsletter.confirmText', { n: activeCount, subject: draft.subject }) }}</p>
        <div class="flex justify-end gap-2">
          <button type="button" class="st-btn st-btn-ghost" @click="confirmSend = false">{{ $t('admin.common.cancel') }}</button>
          <button type="button" class="st-btn" :disabled="busy" @click="send"><font-awesome-icon icon="paper-plane" /> {{ busy ? $t('admin.messages.sending') : $t('admin.newsletter.sendNow') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from '@/plugins/axios'
import { intlLocale } from '@/i18n'
import { business } from '@/config/business'
import { errorsFrom, formatDate, listOf, paragraphs } from './api'

const { t } = useI18n()
const tab = ref('campaigns')
const campaigns = ref([])
const draft = ref(null)
const subscribers = ref([])
const filter = ref('all')
const search = ref('')
const newEmail = ref('')
const busy = ref(false)
const error = ref('')
const notice = ref('')
const confirmSend = ref(false)

const activeCount = computed(() => subscribers.value.filter(s => s.active).length)
const shown = computed(() => subscribers.value.filter(s =>
  (filter.value === 'all' || (filter.value === 'active') === s.active) &&
  (!search.value || s.email.includes(search.value.toLowerCase()))))

async function load() {
  try {
    const [c, s] = await Promise.all([axios.get('/api/studio/campaigns/'), axios.get('/api/studio/subscribers/')])
    campaigns.value = listOf(c.data)
    subscribers.value = listOf(s.data)
  } catch {
    error.value = t('admin.common.loadError')
  }
}
onMounted(load)

const flash = (text) => { notice.value = text; error.value = ''; setTimeout(() => { if (notice.value === text) notice.value = '' }, 5000) }
const fail = (err, fallback) => { error.value = errorsFrom(err).message || Object.values(errorsFrom(err).fields)[0] || fallback; notice.value = '' }

function newCampaign() { draft.value = { id: null, subject: '', body: '', sent_at: null } }
function openCampaign(c) { draft.value = { ...c } }

async function saveDraft(quiet = false) {
  busy.value = true
  try {
    const payload = { subject: draft.value.subject, body: draft.value.body }
    const { data } = draft.value.id
      ? await axios.patch(`/api/studio/campaigns/${draft.value.id}/`, payload)
      : await axios.post('/api/studio/campaigns/', payload)
    draft.value = { ...data }
    const i = campaigns.value.findIndex(c => c.id === data.id)
    if (i >= 0) campaigns.value[i] = data
    else campaigns.value.unshift(data)
    if (!quiet) flash(t('admin.newsletter.saved'))
    return true
  } catch (err) {
    fail(err, t('admin.common.saveError'))
    return false
  } finally {
    busy.value = false
  }
}

async function sendTest() {
  if (!(await saveDraft(true))) return
  busy.value = true
  try {
    const { data } = await axios.post(`/api/studio/campaigns/${draft.value.id}/test/`, {}, { timeout: 30000 })
    flash(t('admin.newsletter.testSent', { email: data.sent_to }))
  } catch (err) {
    fail(err, t('admin.messages.sendError'))
  } finally {
    busy.value = false
  }
}

async function send() {
  if (!(await saveDraft(true))) { confirmSend.value = false; return }
  busy.value = true
  try {
    const { data } = await axios.post(`/api/studio/campaigns/${draft.value.id}/send/`, {}, { timeout: 300000 })
    draft.value = { ...data }
    campaigns.value = campaigns.value.map(c => (c.id === data.id ? data : c))
    flash(t('admin.newsletter.sentTo', { n: data.recipient_count, date: formatDate(data.sent_at, intlLocale()) }))
  } catch (err) {
    fail(err, t('admin.messages.sendError'))
  } finally {
    busy.value = false
    confirmSend.value = false
  }
}

async function removeDraft() {
  try {
    await axios.delete(`/api/studio/campaigns/${draft.value.id}/`)
    campaigns.value = campaigns.value.filter(c => c.id !== draft.value.id)
    draft.value = null
  } catch (err) {
    fail(err, t('admin.common.deleteError'))
  }
}

async function addSubscriber() {
  try {
    const { data } = await axios.post('/api/studio/subscribers/', { email: newEmail.value })
    subscribers.value.unshift(data)
    newEmail.value = ''
    flash(t('admin.newsletter.added', { email: data.email }))
  } catch (err) {
    fail(err, t('admin.common.saveError'))
  }
}

async function unsubscribe(s) {
  try {
    const { data } = await axios.post(`/api/studio/subscribers/${s.id}/unsubscribe/`)
    Object.assign(s, data)
  } catch (err) {
    fail(err, t('admin.common.saveError'))
  }
}

async function removeSubscriber(s) {
  if (!window.confirm(t('admin.newsletter.confirmDelete', { email: s.email }))) return
  try {
    await axios.delete(`/api/studio/subscribers/${s.id}/`)
    subscribers.value = subscribers.value.filter(x => x.id !== s.id)
  } catch (err) {
    fail(err, t('admin.common.deleteError'))
  }
}

async function exportCsv() {
  try {
    const { data } = await axios.get('/api/studio/subscribers/export/', { responseType: 'blob' })
    const url = URL.createObjectURL(data)
    const link = Object.assign(document.createElement('a'), { href: url, download: 'newsletter-subscribers.csv' })
    link.click()
    URL.revokeObjectURL(url)
  } catch (err) {
    fail(err, t('admin.common.loadError'))
  }
}
</script>

<style scoped>
.nl-grid { display: grid; gap: 1.5rem; align-items: start; }
@media (min-width: 1024px) { .nl-grid { grid-template-columns: 20rem minmax(0, 1fr); } }
.nl-row { display: flex; align-items: center; gap: 0.75rem; width: 100%; padding: 0.95rem 1.1rem; border-bottom: 1px solid rgba(244, 236, 225, 0.06); }
.nl-row:hover { background: rgba(244, 236, 225, 0.03); }
.nl-row.is-active { background: rgba(230, 161, 90, 0.1); }
.nl-row strong { font-size: 0.9rem; color: #f4ece1; }
.nl-row small { font-size: 0.75rem; color: #85766a; }
.stat-label { font-size: 0.75rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #85766a; }
.stat-value { margin-top: 0.4rem; font-family: 'Instrument Serif', Georgia, serif; font-size: 2.4rem; line-height: 1; color: #f4ece1; }
.mail-preview { padding: 1.75rem; border-radius: 1.25rem; background: #1e1914; border: 1px solid #2a231c; color: #d9cfc2; font-size: 0.92rem; line-height: 1.65; }
.mail-logo { font-family: Georgia, serif; font-size: 1.6rem; color: #f4ece1; margin-bottom: 1rem; }
.mail-logo em { color: #e6a15a; }
.mail-preview h3 { font-family: Georgia, serif; font-weight: 400 !important; font-size: 1.6rem; color: #f4ece1; margin-bottom: 0.75rem; }
.mail-preview p + p { margin-top: 0.75rem; }
.mail-button { display: inline-block; margin-top: 1.25rem; padding: 0.6rem 1.2rem; border-radius: 999px; background: #e6a15a; color: #14110e; font-weight: 700; }
.mail-preview small { display: block; margin-top: 1.5rem; font-size: 0.72rem; color: #85766a; text-decoration: underline; }
</style>
