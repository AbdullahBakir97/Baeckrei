<template>
  <div class="pb-10">
    <!-- Reading progress -->
    <div v-if="post" class="progress" aria-hidden="true"><span ref="bar"></span></div>

    <div class="section max-w-3xl">
      <router-link to="/blog" class="btn-ghost mb-8"><font-awesome-icon icon="arrow-left" /> {{ $t('blog.allPosts') }}</router-link>

      <div v-if="loading" class="grid gap-4" aria-busy="true">
        <div class="skeleton h-12 w-2/3 rounded-full"></div>
        <div class="skeleton h-80 rounded-3xl"></div>
      </div>
      <div v-else-if="notFound" class="glass-panel text-center py-12">
        <p class="display-title text-4xl">{{ $t('blog.notFound') }}</p>
        <p class="mt-2 text-cream-muted">{{ $t('blog.notFoundText') }}</p>
      </div>
      <article v-else-if="post" ref="article">
        <p class="eyebrow">
          {{ formatDate(post.published_at) }}<template v-if="post.author_name"> · {{ post.author_name }}</template>
          · {{ $t('blog.minutes', readingMinutes) }}
        </p>
        <h1 v-split.load class="display-title text-5xl sm:text-7xl mt-4">{{ localized(post, 'title') }}</h1>
        <p v-if="post.excerpt" v-reveal="{ delay: 0.2 }" class="lede text-auto">{{ localized(post, 'excerpt') }}</p>
        <img v-if="post.cover_image" v-mask :src="post.cover_image" :alt="post.title"
             class="cover" @error="applyImageFallback" />
        <div class="body">
          <p v-for="(paragraph, index) in paragraphs" :key="index" v-reveal class="whitespace-pre-line text-auto">{{ paragraph }}</p>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from '@/plugins/axios'
import { applyImageFallback } from '@/utils/imageFallback'
import { formatDate } from '@/utils/money'
import { SITE_URL, absoluteUrl, usePageMeta } from '@/seo'
import { localized } from '@/i18n/catalog'
import { gsap, ScrollTrigger, prefersReducedMotion } from '@/motion'

const route = useRoute()
const post = ref(null)
const loading = ref(true)
const notFound = ref(false)
const article = ref(null)
const bar = ref(null)
let progress = null

// Posts are plain text; blank lines separate paragraphs. Rendering text
// (not HTML) keeps post content from injecting markup.
const body = computed(() => localized(post.value, 'body'))
const paragraphs = computed(() => body.value.split(/\n\s*\n/).map(p => p.trim()).filter(Boolean))
const readingMinutes = computed(() => Math.max(1, Math.round(body.value.split(/\s+/).length / 200)))

async function load(slug) {
  loading.value = true
  notFound.value = false
  try {
    const response = await axios.get(`/api/content/posts/${slug}/`)
    post.value = response.data
  } catch {
    notFound.value = true
    post.value = null
  } finally {
    loading.value = false
  }
  await nextTick()
  setupProgress()
}

usePageMeta(() => post.value ? {
  title: localized(post.value, 'title'),
  description: localized(post.value, 'excerpt') || body.value,
  image: post.value.cover_image || undefined,
  type: 'article',
  jsonLd: {
    '@type': 'BlogPosting',
    headline: localized(post.value, 'title'),
    description: post.value.excerpt || undefined,
    image: post.value.cover_image ? [post.value.cover_image] : undefined,
    datePublished: post.value.published_at,
    dateModified: post.value.updated_at || post.value.published_at,
    author: post.value.author_name ? { '@type': 'Person', name: post.value.author_name } : { '@id': `${SITE_URL}/#bakery` },
    publisher: { '@id': `${SITE_URL}/#bakery` },
    mainEntityOfPage: absoluteUrl(route.path)
  }
} : {})

// A thin bar at the top fills up as the article is read.
function setupProgress() {
  progress?.kill()
  if (!article.value || !bar.value) return
  progress = gsap.fromTo(bar.value, { scaleX: 0 }, {
    scaleX: 1,
    ease: 'none',
    scrollTrigger: { trigger: article.value, start: 'top 20%', end: 'bottom bottom', scrub: prefersReducedMotion() ? true : 0.3 }
  })
  ScrollTrigger.refresh()
}

onMounted(() => load(route.params.slug))
watch(() => route.params.slug, (slug) => slug && load(slug))
onBeforeUnmount(() => {
  progress?.scrollTrigger?.kill()
  progress?.kill()
})
</script>

<style scoped>
.progress {
  position: fixed;
  inset: 0 0 auto;
  z-index: 60;
  height: 3px;
  pointer-events: none;
}

.progress span {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, #d2603f, #e6a15a);
  transform-origin: left;
  transform: scaleX(0);
}

.lede {
  margin-top: 1.5rem;
  font-size: 1.3rem;
  line-height: 1.6;
  color: #d9cfc2;
}

.cover {
  width: 100%;
  max-height: 32rem;
  margin-top: 2.5rem;
  border-radius: 1.75rem;
  object-fit: cover;
}

.body {
  display: grid;
  gap: 1.4rem;
  margin-top: 3rem;
  font-size: 1.15rem;
  line-height: 1.85;
  color: #d9cfc2;
}

.body p:first-child::first-letter {
  float: left;
  margin: 0.35rem 0.6rem 0 0;
  font-family: 'Instrument Serif', Georgia, serif;
  font-size: 4.2rem;
  line-height: 0.8;
  color: #e6a15a;
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
