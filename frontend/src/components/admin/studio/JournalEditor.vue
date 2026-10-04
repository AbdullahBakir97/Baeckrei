<template>
  <form class="st-page" @submit.prevent="save()">
    <div class="st-bar">
      <router-link to="/admin/journal" class="st-link text-sm"><font-awesome-icon icon="arrow-left" /> {{ $t('admin.journal.back') }}</router-link>
      <div class="flex flex-wrap items-center gap-2">
        <span v-if="post.id" class="st-chip" :class="{ 'is-blue': state === 'scheduled', 'is-green': state === 'published' }">
          {{ $t(`admin.journal.states.${state}`) }}
        </span>
        <a v-if="post.id && state === 'published'" :href="`/blog/${post.slug}`" target="_blank" rel="noopener" class="st-btn st-btn-ghost st-btn-sm">
          <font-awesome-icon icon="up-right-from-square" /> {{ $t('admin.journal.viewInShop') }}
        </a>
        <template v-if="post.id">
          <button v-if="!confirmDelete" type="button" class="st-btn st-btn-danger st-btn-sm" @click="confirmDelete = true">
            <font-awesome-icon icon="trash" /> {{ $t('admin.common.delete') }}
          </button>
          <template v-else>
            <button type="button" class="st-btn st-btn-danger st-btn-sm" @click="remove">{{ $t('admin.journal.confirmDelete') }}</button>
            <button type="button" class="st-btn st-btn-ghost st-btn-sm" @click="confirmDelete = false">{{ $t('admin.common.cancel') }}</button>
          </template>
        </template>
      </div>
    </div>

    <p v-if="error" class="st-alert" role="alert">{{ error }}</p>
    <p v-if="saved" class="st-success" role="status">{{ saved }}</p>

    <div class="editor-grid">
      <!-- Text -->
      <div class="st-card st-grid">
        <div class="flex items-center justify-between gap-3">
          <div class="st-tabs" role="tablist" :aria-label="$t('admin.journal.language')">
            <button v-for="l in ['de', 'en']" :key="l" type="button" role="tab" class="st-tab" :class="{ 'is-active': lang === l }"
                    :aria-selected="lang === l" @click="lang = l">
              {{ l === 'de' ? 'Deutsch' : 'English' }}
            </button>
          </div>
          <div class="st-tabs">
            <button type="button" class="st-tab" :class="{ 'is-active': !preview }" @click="preview = false">{{ $t('admin.journal.write') }}</button>
            <button type="button" class="st-tab" :class="{ 'is-active': preview }" @click="preview = true">{{ $t('admin.journal.preview') }}</button>
          </div>
        </div>
        <p v-if="lang === 'en'" class="st-hint !mt-0">{{ $t('admin.journal.englishHint') }}</p>

        <template v-if="!preview">
          <div>
            <label class="st-label" for="post-title">{{ $t('admin.journal.title') }}</label>
            <input id="post-title" v-model="post[field('title')]" class="st-input post-title" :required="lang === 'de'" maxlength="200"
                   :lang="lang" :placeholder="$t('admin.journal.titlePlaceholder')" />
            <p v-if="fieldErrors.title" class="st-error">{{ fieldErrors.title }}</p>
          </div>
          <div>
            <label class="st-label" for="post-excerpt">{{ $t('admin.journal.excerpt') }} <small>· {{ $t('admin.journal.excerptHint') }}</small></label>
            <textarea id="post-excerpt" v-model="post[field('excerpt')]" class="st-input" rows="2" maxlength="300" :lang="lang"></textarea>
          </div>
          <div>
            <label class="st-label" for="post-body">{{ $t('admin.journal.body') }} <small>· {{ $t('admin.journal.bodyHint') }}</small></label>
            <textarea id="post-body" v-model="post[field('body')]" class="st-input post-body" rows="18" :required="lang === 'de'" :lang="lang"></textarea>
            <p v-if="fieldErrors.body" class="st-error">{{ fieldErrors.body }}</p>
            <p class="st-hint">{{ $t('admin.journal.words', { n: wordCount, min: readMinutes }) }}</p>
          </div>
        </template>

        <article v-else class="post-preview" :lang="lang">
          <img v-if="coverPreview" :src="coverPreview" alt="" class="post-preview-cover" />
          <h2>{{ post[field('title')] || post.title }}</h2>
          <p v-if="post[field('excerpt')]" class="post-preview-excerpt">{{ post[field('excerpt')] }}</p>
          <p v-for="(p, i) in paragraphs(post[field('body')] || post.body)" :key="i">{{ p }}</p>
        </article>
      </div>

      <!-- Publishing -->
      <aside class="st-grid content-start">
        <div class="st-card st-grid">
          <h2 class="st-card-title !mb-0">{{ $t('admin.journal.publishing') }}</h2>
          <label v-for="mode in ['draft', 'now', 'schedule']" :key="mode" class="publish-option" :class="{ 'is-on': publish === mode }">
            <input v-model="publish" type="radio" name="publish" :value="mode" />
            <span>
              <strong>{{ $t(`admin.journal.publish.${mode}`) }}</strong>
              <small>{{ $t(`admin.journal.publish.${mode}Hint`) }}</small>
            </span>
          </label>
          <input v-if="publish === 'schedule'" v-model="scheduleAt" type="datetime-local" class="st-input" required :aria-label="$t('admin.journal.publish.schedule')" />
          <button type="submit" class="st-btn w-full" :disabled="saving">
            <font-awesome-icon icon="check" /> {{ saving ? $t('admin.common.saving') : saveLabel }}
          </button>
        </div>

        <div class="st-card st-grid">
          <h2 class="st-card-title !mb-0">{{ $t('admin.journal.cover') }}</h2>
          <img v-if="coverPreview" :src="coverPreview" alt="" class="cover-preview" />
          <div v-else class="cover-empty"><font-awesome-icon icon="image" /></div>
          <input type="file" accept="image/jpeg,image/png,image/webp" :aria-label="$t('admin.journal.cover')" @change="pickCover" />
          <p class="st-hint !mt-0">{{ $t('admin.journal.coverHint') }}</p>
          <button v-if="coverPreview" type="button" class="st-btn st-btn-ghost st-btn-sm justify-self-start" @click="dropCover">
            {{ $t('admin.journal.removeCover') }}
          </button>
        </div>

        <div class="st-card">
          <label class="st-label" for="post-slug">{{ $t('admin.journal.address') }}</label>
          <div class="flex items-center gap-1 text-sm text-cream-faint"><span>/blog/</span>
            <input id="post-slug" v-model.trim="post.slug" class="st-input" :placeholder="$t('admin.journal.addressAuto')" maxlength="220" />
          </div>
          <p v-if="fieldErrors.slug" class="st-error">{{ fieldErrors.slug }}</p>
          <p v-if="post.author_name" class="st-hint">{{ $t('admin.journal.author', { name: post.author_name }) }}</p>
        </div>
      </aside>
    </div>
  </form>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import axios from '@/plugins/axios'
import { errorsFrom, fromLocalInput, paragraphs, toLocalInput } from './api'
import { refreshStudio } from '@/composables/useStudioSummary'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()

const post = reactive({ id: null, title: '', title_en: '', excerpt: '', excerpt_en: '', body: '', body_en: '', slug: '', published_at: null, cover_image_url: null, author_name: '' })
const lang = ref('de')
const preview = ref(false)
const publish = ref('draft')
const scheduleAt = ref('')
const coverFile = ref(null)
const coverPreview = ref(null)
const removeCover = ref(false)
const saving = ref(false)
const error = ref('')
const saved = ref('')
const fieldErrors = reactive({})
const confirmDelete = ref(false)

const field = (name) => (lang.value === 'en' ? `${name}_en` : name)
const state = computed(() => {
  if (!post.published_at) return 'draft'
  return new Date(post.published_at) > new Date() ? 'scheduled' : 'published'
})
const saveLabel = computed(() => t(`admin.journal.saveAs.${publish.value}`))
const wordCount = computed(() => String(post[field('body')] || '').split(/\s+/).filter(Boolean).length)
const readMinutes = computed(() => Math.max(1, Math.round(wordCount.value / 200)))

function fill(data) {
  Object.assign(post, data)
  coverPreview.value = data.cover_image_url
  if (!data.published_at) publish.value = 'draft'
  else if (new Date(data.published_at) > new Date()) { publish.value = 'schedule'; scheduleAt.value = toLocalInput(data.published_at) }
  else publish.value = 'now'
}

onMounted(async () => {
  if (route.params.id) {
    try {
      fill((await axios.get(`/api/studio/posts/${route.params.id}/`)).data)
    } catch {
      error.value = t('admin.common.loadError')
    }
  }
})

function pickCover(event) {
  const file = event.target.files?.[0]
  if (!file) return
  coverFile.value = file
  removeCover.value = false
  coverPreview.value = URL.createObjectURL(file)
}
function dropCover() {
  coverFile.value = null
  coverPreview.value = null
  removeCover.value = true
}

function publishedAt() {
  if (publish.value === 'draft') return null
  if (publish.value === 'schedule') return fromLocalInput(scheduleAt.value)
  // Keep the original date of a post that is already live.
  return state.value === 'published' ? post.published_at : new Date().toISOString()
}

async function save() {
  saving.value = true
  error.value = ''
  saved.value = ''
  Object.keys(fieldErrors).forEach(k => delete fieldErrors[k])
  const payload = {
    title: post.title, title_en: post.title_en, excerpt: post.excerpt, excerpt_en: post.excerpt_en,
    body: post.body, body_en: post.body_en, published_at: publishedAt(),
    ...(post.slug ? { slug: post.slug } : {}),
    ...(removeCover.value ? { remove_cover_image: true } : {})
  }
  try {
    let data = post.id
      ? (await axios.patch(`/api/studio/posts/${post.id}/`, payload)).data
      : (await axios.post('/api/studio/posts/', payload)).data
    if (coverFile.value) {
      const form = new FormData()
      form.append('cover_image', coverFile.value)
      data = (await axios.patch(`/api/studio/posts/${data.id}/`, form, { headers: { 'Content-Type': 'multipart/form-data' }, timeout: 60000 })).data
      coverFile.value = null
    }
    removeCover.value = false
    const created = !post.id
    fill(data)
    saved.value = t(`admin.journal.savedAs.${data.state}`)
    refreshStudio()
    if (created) router.replace(`/admin/journal/${data.id}`)
  } catch (err) {
    const { fields, message } = errorsFrom(err)
    Object.assign(fieldErrors, fields)
    if (fields.title || fields.body) lang.value = 'de'
    error.value = message || (Object.keys(fields).length ? t('admin.common.checkFields') : t('admin.common.saveError'))
  } finally {
    saving.value = false
  }
}

async function remove() {
  try {
    await axios.delete(`/api/studio/posts/${post.id}/`)
    refreshStudio()
    router.push('/admin/journal')
  } catch {
    error.value = t('admin.common.deleteError')
  }
}
</script>

<style scoped>
.editor-grid { display: grid; gap: 1.5rem; align-items: start; }
@media (min-width: 1100px) { .editor-grid { grid-template-columns: minmax(0, 1fr) 20rem; } }
.post-title { font-family: 'Instrument Serif', Georgia, serif; font-size: 1.6rem !important; padding: 0.5rem 0.8rem; }
.post-body { min-height: 24rem; font-size: 0.95rem !important; }
.publish-option { display: flex; gap: 0.75rem; padding: 0.75rem 0.9rem; border-radius: 1rem; border: 1px solid rgba(244, 236, 225, 0.08); cursor: pointer; transition: border-color 0.2s, background 0.2s; }
.publish-option.is-on { border-color: rgba(230, 161, 90, 0.6); background: rgba(230, 161, 90, 0.08); }
.publish-option input { margin-top: 0.2rem; accent-color: #e6a15a; }
.publish-option strong { display: block; font-size: 0.875rem; color: #f4ece1; }
.publish-option small { display: block; font-size: 0.75rem; color: #85766a; }
.cover-preview { width: 100%; aspect-ratio: 16 / 9; object-fit: cover; border-radius: 1rem; }
.cover-empty { display: grid; place-items: center; aspect-ratio: 16 / 9; border-radius: 1rem; font-size: 1.5rem; color: #7d7061; background: rgba(244, 236, 225, 0.04); border: 1px dashed rgba(244, 236, 225, 0.15); }
.post-preview { max-width: 42rem; padding: 0.5rem 0; color: #d9cfc2; line-height: 1.75; }
.post-preview h2 { margin: 1rem 0 0.75rem; font-family: 'Instrument Serif', Georgia, serif; font-size: 2.4rem; font-weight: 400; line-height: 1.1; color: #f4ece1; }
.post-preview p + p { margin-top: 1rem; }
.post-preview-excerpt { font-size: 1.1rem; color: #b9ab98; }
.post-preview-cover { width: 100%; aspect-ratio: 16 / 9; object-fit: cover; border-radius: 1.25rem; }
</style>
