<template>
  <div class="min-h-screen py-12 px-4">
    <div class="max-w-3xl mx-auto">
      <router-link to="/blog" class="btn-ghost mb-6"><font-awesome-icon icon="arrow-left" /> All posts</router-link>

      <div v-if="loading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-white/20"></div>
      </div>
      <div v-else-if="notFound" class="glass-panel text-center py-12">
        <p class="text-lg text-white font-medium">This post doesn't exist</p>
        <p class="mt-2 text-gray-400">It may have been removed or not published yet.</p>
      </div>
      <article v-else-if="post" class="glass-panel">
        <img v-if="post.cover_image" :src="post.cover_image" :alt="post.title" class="mb-6 max-h-96 w-full rounded-xl object-cover" @error="applyImageFallback" />
        <p class="text-sm text-gray-500">{{ formatDate(post.published_at) }}<template v-if="post.author_name"> · {{ post.author_name }}</template></p>
        <h1 class="mt-2 text-3xl font-extrabold text-white">{{ post.title }}</h1>
        <div class="prose-dark mt-6">
          <p v-for="(paragraph, index) in paragraphs" :key="index" class="whitespace-pre-line">{{ paragraph }}</p>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from '@/plugins/axios'
import { applyImageFallback } from '@/utils/imageFallback'

const route = useRoute()
const post = ref(null)
const loading = ref(true)
const notFound = ref(false)

// Posts are plain text; blank lines separate paragraphs. Rendering text
// (not HTML) keeps post content from injecting markup.
const paragraphs = computed(() => (post.value?.body || '').split(/\n\s*\n/).map(p => p.trim()).filter(Boolean))
const formatDate = (value) => new Date(value).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' })

async function load(slug) {
  loading.value = true
  notFound.value = false
  try {
    const response = await axios.get(`/api/content/posts/${slug}/`)
    post.value = response.data
    document.title = `${response.data.title} - ${document.title.split(' - ').pop()}`
  } catch (err) {
    notFound.value = true
    post.value = null
  } finally {
    loading.value = false
  }
}

onMounted(() => load(route.params.slug))
watch(() => route.params.slug, (slug) => slug && load(slug))
</script>
