<template>
  <div class="min-h-screen py-12 px-4">
    <div class="max-w-5xl mx-auto">
      <PageHeader title="From the bakery" subtitle="News, seasonal bakes and stories from our kitchen" icon="newspaper" />

      <div v-if="loading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-white/20"></div>
      </div>
      <p v-else-if="error" class="glass-panel text-red-300" role="alert">{{ error }}</p>
      <div v-else-if="!posts.length" class="glass-panel text-center py-12">
        <p class="text-lg text-white font-medium">No posts yet</p>
        <p class="mt-2 text-gray-400">Check back soon for news from the bakery.</p>
      </div>
      <div v-else class="grid sm:grid-cols-2 gap-6">
        <article v-for="post in posts" :key="post.id" class="glass-panel flex flex-col gap-3">
          <router-link v-if="post.cover_image" :to="{ name: 'blog-post', params: { slug: post.slug } }">
            <img :src="post.cover_image" :alt="post.title" class="h-48 w-full rounded-xl object-cover" loading="lazy" @error="applyImageFallback" />
          </router-link>
          <p class="text-sm text-gray-500">{{ formatDate(post.published_at) }}<template v-if="post.author_name"> · {{ post.author_name }}</template></p>
          <h2 class="text-xl font-semibold text-white">
            <router-link :to="{ name: 'blog-post', params: { slug: post.slug } }" class="hover:text-amber-300">{{ post.title }}</router-link>
          </h2>
          <p v-if="post.excerpt" class="text-gray-300 flex-1">{{ post.excerpt }}</p>
          <router-link :to="{ name: 'blog-post', params: { slug: post.slug } }" class="text-amber-400 hover:text-amber-300">Read more</router-link>
        </article>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import axios from '@/plugins/axios'
import PageHeader from '@/components/common/PageHeader.vue'
import { applyImageFallback } from '@/utils/imageFallback'

const posts = ref([])
const loading = ref(true)
const error = ref('')

const formatDate = (value) => new Date(value).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' })

onMounted(async () => {
  try {
    const response = await axios.get('/api/content/posts/')
    posts.value = Array.isArray(response.data) ? response.data : response.data.results || []
  } catch (err) {
    error.value = 'The blog could not be loaded. Please try again later.'
  } finally {
    loading.value = false
  }
})
</script>
