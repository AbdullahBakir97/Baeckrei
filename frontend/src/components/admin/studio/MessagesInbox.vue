<template>
  <div class="st-page">
    <div class="st-bar">
      <div class="st-tabs" role="tablist">
        <button v-for="tab in ['open', 'done', 'all']" :key="tab" type="button" role="tab" class="st-tab"
                :class="{ 'is-active': state === tab }" :aria-selected="state === tab" @click="state = tab">
          {{ $t(`admin.messages.states.${tab}`) }}
        </button>
      </div>
      <input v-model="search" type="search" class="st-input !w-64" :placeholder="$t('admin.messages.search')" :aria-label="$t('admin.messages.search')" />
    </div>

    <p v-if="error" class="st-alert" role="alert">{{ error }}</p>

    <div class="inbox">
      <!-- List -->
      <div class="st-card !p-0 overflow-hidden inbox-list" :class="{ 'has-open': current }">
        <p v-if="loading" class="st-empty">{{ $t('admin.common.loading') }}</p>
        <p v-else-if="!messages.length" class="st-empty">
          <font-awesome-icon icon="inbox" class="mb-3 text-2xl" /><br>{{ $t(`admin.messages.empty.${state}`) }}
        </p>
        <button v-for="m in messages" v-else :key="m.id" type="button" class="inbox-row"
                :class="{ 'is-active': current?.id === m.id, 'is-unread': !m.handled }" @click="open(m)">
          <span class="inbox-avatar">{{ initial(m.name) }}</span>
          <span class="min-w-0 flex-1 text-start">
            <span class="flex items-baseline justify-between gap-2">
              <strong class="truncate">{{ m.name }}</strong>
              <small class="flex-none">{{ ago(m.created_at) }}</small>
            </span>
            <span class="block truncate text-sm text-cream/80 text-auto">{{ m.subject || $t('admin.messages.noSubject') }}</span>
            <span class="block truncate text-xs text-cream-faint text-auto">{{ m.message }}</span>
          </span>
        </button>
      </div>

      <!-- Reading pane -->
      <div class="st-card inbox-read" :class="{ 'is-open': current }">
        <div v-if="!current" class="st-empty">{{ $t('admin.messages.pick') }}</div>
        <template v-else>
          <div class="st-bar">
            <button type="button" class="st-link text-sm lg:hidden" @click="current = null"><font-awesome-icon icon="arrow-left" /> {{ $t('admin.messages.back') }}</button>
            <div class="flex flex-wrap gap-2 ms-auto">
              <button type="button" class="st-btn st-btn-ghost st-btn-sm" @click="toggleHandled">
                <font-awesome-icon :icon="current.handled ? 'rotate' : 'check'" />
                {{ current.handled ? $t('admin.messages.reopen') : $t('admin.messages.markDone') }}
              </button>
              <a :href="mailto" class="st-btn st-btn-ghost st-btn-sm"><font-awesome-icon icon="envelope" /> {{ $t('admin.messages.ownMail') }}</a>
              <button v-if="!confirmDelete" type="button" class="st-btn st-btn-danger st-btn-sm" :aria-label="$t('admin.common.delete')" @click="confirmDelete = true">
                <font-awesome-icon icon="trash" />
              </button>
              <button v-else type="button" class="st-btn st-btn-danger st-btn-sm" @click="remove">{{ $t('admin.messages.confirmDelete') }}</button>
            </div>
          </div>

          <header class="read-head">
            <h2 class="text-auto">{{ current.subject || $t('admin.messages.noSubject') }}</h2>
            <p>
              <strong>{{ current.name }}</strong> · <a :href="`mailto:${current.email}`" class="st-link">{{ current.email }}</a>
              · {{ formatDate(current.created_at, intlLocale()) }}
            </p>
          </header>
          <p class="read-body text-auto">{{ current.message }}</p>

          <div v-if="current.replied_at" class="read-reply">
            <p class="read-reply-head">
              <font-awesome-icon icon="reply" />
              {{ $t('admin.messages.repliedBy', { name: current.replied_by_name, date: formatDate(current.replied_at, intlLocale()) }) }}
            </p>
            <p class="read-body text-auto">{{ current.reply }}</p>
          </div>

          <form class="reply-box" @submit.prevent="sendReply">
            <label class="st-label" for="reply">{{ current.replied_at ? $t('admin.messages.replyAgain') : $t('admin.messages.reply') }}</label>
            <div class="flex flex-wrap gap-2 mb-2">
              <button v-for="(snippet, i) in snippets" :key="i" type="button" class="st-chip hover:text-cream" @click="useSnippet(snippet)">
                {{ snippet.label }}
              </button>
            </div>
            <textarea id="reply" v-model="reply" class="st-input" rows="7" required :placeholder="$t('admin.messages.replyPlaceholder', { name: firstName })"></textarea>
            <div class="mt-3 flex flex-wrap items-center justify-between gap-3">
              <p class="st-hint !mt-0">{{ $t('admin.messages.replyHint', { email: current.email }) }}</p>
              <button type="submit" class="st-btn" :disabled="sending || !reply.trim()">
                <font-awesome-icon icon="paper-plane" /> {{ sending ? $t('admin.messages.sending') : $t('admin.messages.send') }}
              </button>
            </div>
            <p v-if="sent" class="st-success mt-3" role="status">{{ sent }}</p>
          </form>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import axios from '@/plugins/axios'
import { intlLocale } from '@/i18n'
import { business } from '@/config/business'
import { errorsFrom, formatDate, listOf } from './api'
import { refreshStudio } from '@/composables/useStudioSummary'

const { t } = useI18n()
const route = useRoute()
const state = ref('open')
const search = ref('')
const messages = ref([])
const current = ref(null)
const loading = ref(true)
const error = ref('')
const reply = ref('')
const sending = ref(false)
const sent = ref('')
const confirmDelete = ref(false)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const params = { state: state.value === 'all' ? undefined : state.value, search: search.value || undefined }
    messages.value = listOf((await axios.get('/api/studio/messages/', { params })).data)
  } catch {
    error.value = t('admin.common.loadError')
  } finally {
    loading.value = false
  }
}
let timer
watch(state, load)
watch(search, () => { clearTimeout(timer); timer = setTimeout(load, 300) })
onMounted(async () => {
  await load()
  const wanted = Number(route.query.id)
  if (wanted) open(messages.value.find(m => m.id === wanted) || (await axios.get(`/api/studio/messages/${wanted}/`).catch(() => ({}))).data)
})

function open(message) {
  if (!message) return
  current.value = message
  reply.value = ''
  sent.value = ''
  confirmDelete.value = false
}

const firstName = computed(() => (current.value?.name || '').split(' ')[0])
const signature = computed(() => `\n\n${t('admin.messages.regards')}\n${business.name}`)
const snippets = computed(() => [
  { label: t('admin.messages.snippets.thanks'), text: t('admin.messages.snippetText.thanks', { name: firstName.value }) },
  { label: t('admin.messages.snippets.order'), text: t('admin.messages.snippetText.order', { name: firstName.value }) },
  { label: t('admin.messages.snippets.call'), text: t('admin.messages.snippetText.call', { name: firstName.value }) }
])
const useSnippet = (snippet) => { reply.value = snippet.text + signature.value }
const mailto = computed(() => current.value
  ? `mailto:${current.value.email}?subject=${encodeURIComponent(`Re: ${current.value.subject || business.name}`)}`
  : '#')

async function sendReply() {
  sending.value = true
  error.value = ''
  try {
    const { data } = await axios.post(`/api/studio/messages/${current.value.id}/reply/`, { reply: reply.value }, { timeout: 30000 })
    replace(data)
    reply.value = ''
    sent.value = t('admin.messages.sent', { email: data.email })
    refreshStudio()
  } catch (err) {
    error.value = errorsFrom(err).message || t('admin.messages.sendError')
  } finally {
    sending.value = false
  }
}

async function toggleHandled() {
  try {
    const { data } = await axios.patch(`/api/studio/messages/${current.value.id}/`, { handled: !current.value.handled })
    replace(data)
    refreshStudio()
  } catch {
    error.value = t('admin.common.saveError')
  }
}

async function remove() {
  try {
    await axios.delete(`/api/studio/messages/${current.value.id}/`)
    messages.value = messages.value.filter(m => m.id !== current.value.id)
    current.value = null
    refreshStudio()
  } catch {
    error.value = t('admin.common.deleteError')
  }
}

function replace(data) {
  current.value = data
  const i = messages.value.findIndex(m => m.id === data.id)
  if (i >= 0) messages.value[i] = data
}

const initial = (name) => (name || '?').trim().charAt(0).toUpperCase()
function ago(iso) {
  const minutes = Math.round((Date.now() - new Date(iso)) / 60000)
  const rtf = new Intl.RelativeTimeFormat(intlLocale(), { numeric: 'auto', style: 'short' })
  if (minutes < 60) return rtf.format(-minutes, 'minute')
  if (minutes < 1440) return rtf.format(-Math.round(minutes / 60), 'hour')
  if (minutes < 10080) return rtf.format(-Math.round(minutes / 1440), 'day')
  return formatDate(iso, intlLocale(), false)
}
</script>

<style scoped>
.inbox { display: grid; gap: 1.5rem; align-items: start; }
@media (min-width: 1024px) { .inbox { grid-template-columns: 22rem minmax(0, 1fr); } }
@media (max-width: 1023px) {
  .inbox-list.has-open { display: none; }
  .inbox-read:not(.is-open) { display: none; }
}
.inbox-list { max-height: calc(100vh - 14rem); overflow-y: auto; }
.inbox-row { display: flex; gap: 0.8rem; width: 100%; padding: 0.95rem 1.1rem; border-bottom: 1px solid rgba(244, 236, 225, 0.06); transition: background 0.2s; }
.inbox-row:hover { background: rgba(244, 236, 225, 0.03); }
.inbox-row.is-active { background: rgba(230, 161, 90, 0.1); }
.inbox-row strong { font-size: 0.9rem; color: #f4ece1; font-weight: 600; }
.inbox-row.is-unread strong::before { content: ''; display: inline-block; width: 0.45rem; height: 0.45rem; margin-inline-end: 0.45rem; border-radius: 50%; background: #e6a15a; vertical-align: 0.1rem; }
.inbox-row small { font-size: 0.72rem; color: #85766a; }
.inbox-avatar { flex: none; display: grid; place-items: center; width: 2.4rem; height: 2.4rem; border-radius: 50%; font-weight: 700; color: #0e0c0a; background: linear-gradient(135deg, #f2c48d, #b6722c); }
.read-head { margin: 1.25rem 0 1rem; padding-bottom: 1rem; border-bottom: 1px solid rgba(244, 236, 225, 0.08); }
.read-head h2 { font-family: 'Instrument Serif', Georgia, serif; font-size: 1.9rem; font-weight: 400 !important; line-height: 1.15; color: #f4ece1; }
.read-head p { margin-top: 0.4rem; font-size: 0.85rem; color: #b9ab98; }
.read-body { white-space: pre-line; font-size: 0.95rem; line-height: 1.7; color: #d9cfc2; }
.read-reply { margin-top: 1.25rem; padding: 1rem 1.2rem; border-radius: 1rem; background: rgba(159, 212, 154, 0.06); border-inline-start: 3px solid #9fd49a; }
.read-reply-head { margin-bottom: 0.5rem; font-size: 0.8rem; font-weight: 600; color: #b8e3b2; }
.reply-box { margin-top: 1.5rem; padding-top: 1.25rem; border-top: 1px solid rgba(244, 236, 225, 0.08); }
</style>
