<template>
  <div class="section pb-10">
    <PageHeader :eyebrow="$t('blog.eyebrow')" :title="$t('blog.title')" :subtitle="$t('blog.subtitle')" />

    <div v-if="loading" class="grid gap-6 sm:grid-cols-2" aria-busy="true">
      <div class="skeleton h-96 rounded-3xl sm:col-span-2"></div>
      <div v-for="n in 2" :key="n" class="skeleton h-72 rounded-3xl"></div>
    </div>
    <p v-else-if="error" class="glass-panel text-red-300" role="alert">{{ $t('blog.loadError') }}</p>
    <div v-else-if="!posts.length" class="glass-panel text-center py-12">
      <p class="display-title text-4xl">{{ $t('blog.emptyTitle') }}</p>
      <p class="mt-2 text-cream-muted">{{ $t('blog.emptyText') }}</p>
    </div>

    <div v-else v-reveal.stagger class="posts">
      <article v-for="(post, index) in posts" :key="post.id" class="post lux-card" :class="{ 'is-featured': index === 0 }">
        <router-link :to="{ name: 'blog-post', params: { slug: post.slug } }" class="post-media" tabindex="-1" aria-hidden="true">
          <img v-if="post.cover_image" :src="post.cover_image" alt="" loading="lazy" @error="applyImageFallback" />
          <span v-else class="post-placeholder"><img :src="fallbackImage(index)" alt="" /></span>
        </router-link>
        <div class="post-body">
          <p class="text-sm text-cream-faint">
            {{ formatDate(post.published_at) }}<template v-if="post.author_name"> · {{ post.author_name }}</template>
          </p>
          <h2 class="post-title">
            <router-link :to="{ name: 'blog-post', params: { slug: post.slug } }">{{ post.title }}</router-link>
          </h2>
          <p v-if="post.excerpt" class="text-cream-muted">{{ post.excerpt }}</p>
          <span class="post-more">{{ $t('blog.readMore') }} <font-awesome-icon icon="arrow-right" /></span>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import axios from '@/plugins/axios'
import PageHeader from '@/components/common/PageHeader.vue'
import { applyImageFallback } from '@/utils/imageFallback'
import { formatDate } from '@/utils/money'
import croissantImg from '@/assets/bakery/croissant-butter.png'
import pretzelImg from '@/assets/bakery/pretzel.png'
import cupcakeImg from '@/assets/bakery/cupcake.png'

const posts = ref([])
const loading = ref(true)
const error = ref(false)
const fallbackImage = (index) => [croissantImg, pretzelImg, cupcakeImg][index % 3]

onMounted(async () => {
  try {
    const response = await axios.get('/api/content/posts/')
    posts.value = Array.isArray(response.data) ? response.data : response.data.results || []
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.posts {
  display: grid;
  gap: 1.5rem;
}

@media (min-width: 768px) {
  .posts {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .post.is-featured {
    grid-column: 1 / -1;
    grid-template-columns: 1.2fr 1fr;
    display: grid;
  }
}

.post {
  position: relative;
  display: flex;
  flex-direction: column;
}

.post-media {
  display: block;
  aspect-ratio: 16 / 10;
  overflow: hidden;
  border-radius: 1.5rem 1.5rem 0 0;
}

.is-featured .post-media {
  aspect-ratio: auto;
  min-height: 20rem;
}

@media (min-width: 768px) {
  .is-featured .post-media {
    border-radius: 1.5rem 0 0 1.5rem;
  }
}

.post-media img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: scale 0.9s var(--ease-out-expo);
}

.post:hover .post-media img {
  scale: 1.05;
}

.post-placeholder {
  display: grid;
  place-items: center;
  width: 100%;
  height: 100%;
  background: radial-gradient(60% 60% at 50% 55%, rgba(230, 161, 90, 0.2), transparent 70%), #1e1914;
}

.post-placeholder img {
  width: 45%;
  height: auto;
  object-fit: contain;
  filter: drop-shadow(0 20px 20px rgba(0, 0, 0, 0.5));
}

.post-body {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1.75rem;
}

.is-featured .post-body {
  justify-content: center;
  padding: 2.5rem;
}

.post-title {
  font-family: 'Instrument Serif', Georgia, serif;
  font-size: 2.2rem;
  font-weight: 400;
  line-height: 1.05;
  color: #f4ece1;
}

.is-featured .post-title {
  font-size: clamp(2.5rem, 4vw, 3.75rem);
}

.post-title a {
  color: inherit;
}

.post-title a::after {
  content: '';
  position: absolute;
  inset: 0;
}

.post-more {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
  font-weight: 600;
  color: #e6a15a;
  transition: gap 0.4s var(--ease-out-expo);
}

.post:hover .post-more {
  gap: 0.9rem;
}

.skeleton {
  background: linear-gradient(100deg, rgba(244, 236, 225, 0.04) 30%, rgba(244, 236, 225, 0.09) 50%, rgba(244, 236, 225, 0.04) 70%);
  background-size: 200% 100%;
  animation: shimmer 1.4s linear infinite;
}

@keyframes shimmer {
  to { background-position: -200% 0; }
}
</style>
