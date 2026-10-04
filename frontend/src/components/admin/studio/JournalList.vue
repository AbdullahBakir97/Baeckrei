<template>
  <div class="st-page">
    <div class="st-bar">
      <div class="st-tabs" role="tablist">
        <button v-for="tab in tabs" :key="tab" type="button" role="tab" class="st-tab" :class="{ 'is-active': state === tab }"
                :aria-selected="state === tab" @click="state = tab">
          {{ $t(`admin.journal.states.${tab}`) }}
        </button>
      </div>
      <div class="flex flex-wrap gap-2">
        <input v-model="search" type="search" class="st-input !w-56" :placeholder="$t('admin.journal.search')" :aria-label="$t('admin.journal.search')" />
        <router-link to="/admin/journal/new" class="st-btn"><font-awesome-icon icon="plus" /> {{ $t('admin.journal.new') }}</router-link>
      </div>
    </div>

    <p v-if="error" class="st-alert" role="alert">{{ error }}</p>

    <div class="st-card !p-0 overflow-hidden">
      <p v-if="loading" class="st-empty">{{ $t('admin.common.loading') }}</p>
      <div v-else-if="!posts.length" class="st-empty">
        <p>{{ $t('admin.journal.empty') }}</p>
        <router-link to="/admin/journal/new" class="st-btn mt-4">{{ $t('admin.journal.writeFirst') }}</router-link>
      </div>
      <ul v-else class="journal-list">
        <li v-for="post in posts" :key="post.id">
          <router-link :to="`/admin/journal/${post.id}`" class="journal-row">
            <img v-if="post.cover_image_url" :src="post.cover_image_url" alt="" class="journal-cover" />
            <span v-else class="journal-cover is-empty"><font-awesome-icon icon="newspaper" /></span>
            <span class="min-w-0 flex-1">
              <span class="journal-title">{{ post.title }}</span>
              <span class="journal-meta">
                {{ post.excerpt || firstLine(post.body) }}
              </span>
            </span>
            <span class="journal-side">
              <span class="st-chip" :class="chipClass(post.state)">{{ $t(`admin.journal.states.${post.state}`) }}</span>
              <span class="text-xs text-cream-faint">{{ when(post) }}</span>
              <span v-if="post.title_en" class="st-chip">EN</span>
            </span>
          </router-link>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from '@/plugins/axios'
import { intlLocale } from '@/i18n'
import { formatDate, listOf } from './api'

const { t } = useI18n()
const tabs = ['all', 'draft', 'scheduled', 'published']
const state = ref('all')
const search = ref('')
const posts = ref([])
const loading = ref(true)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    const params = { search: search.value || undefined, state: state.value === 'all' ? undefined : state.value }
    posts.value = listOf((await axios.get('/api/studio/posts/', { params })).data)
  } catch {
    error.value = t('admin.common.loadError')
  } finally {
    loading.value = false
  }
}

let timer
watch(state, load)
watch(search, () => { clearTimeout(timer); timer = setTimeout(load, 300) })
onMounted(load)

const chipClass = (s) => ({ draft: '', scheduled: 'is-blue', published: 'is-green' }[s])
const firstLine = (text) => String(text || '').split('\n')[0].slice(0, 140)
function when(post) {
  if (post.state === 'draft') return t('admin.journal.editedAt', { date: formatDate(post.updated_at, intlLocale()) })
  return formatDate(post.published_at, intlLocale())
}
</script>

<style scoped>
.journal-list > li + li { border-top: 1px solid rgba(244, 236, 225, 0.06); }
.journal-row { display: flex; align-items: center; gap: 1rem; padding: 1rem 1.25rem; transition: background 0.2s; }
.journal-row:hover { background: rgba(244, 236, 225, 0.03); }
.journal-cover { flex: none; width: 4.5rem; height: 3.25rem; border-radius: 0.75rem; object-fit: cover; }
.journal-cover.is-empty { display: grid; place-items: center; color: #7d7061; background: rgba(244, 236, 225, 0.05); }
.journal-title { display: block; font-weight: 600; color: #f4ece1; }
.journal-meta { display: block; margin-top: 0.2rem; font-size: 0.82rem; color: #85766a; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.journal-side { display: flex; flex-direction: column; align-items: flex-end; gap: 0.35rem; }
</style>
