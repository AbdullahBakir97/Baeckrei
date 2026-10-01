<template>
  <div class="section notfound">
    <img :src="pretzelImg" alt="" class="notfound-img" />
    <p class="notfound-code" aria-hidden="true">404</p>
    <h1 v-split.load class="display-title text-5xl sm:text-7xl">{{ $t('notFound.title') }}</h1>
    <i18n-t keypath="notFound.text" tag="p" class="mt-4 max-w-md text-cream-muted" scope="global">
      <template #path><span class="font-mono text-cream break-all">{{ route.fullPath }}</span></template>
    </i18n-t>
    <form class="notfound-search" role="search" @submit.prevent="search">
      <label for="not-found-search" class="sr-only">{{ $t('nav.searchProducts') }}</label>
      <input id="not-found-search" v-model.trim="query" :placeholder="$t('notFound.searchPlaceholder')" />
      <button type="submit" class="btn-amber !py-3 !px-6">{{ $t('common.search') }}</button>
    </form>
    <div class="mt-6 flex flex-wrap justify-center gap-3">
      <router-link to="/" class="btn-ghost">{{ $t('nav.homeLink') }}</router-link>
      <router-link to="/products" class="btn-ghost">{{ $t('common.browseProducts') }}</router-link>
      <router-link to="/contact" class="btn-ghost">{{ $t('common.contactUs') }}</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import pretzelImg from '@/assets/bakery/pretzel.png'

const route = useRoute()
const router = useRouter()
const query = ref('')

const search = () => {
  if (query.value) router.push({ name: 'products', query: { search: query.value } })
}
</script>

<style scoped>
.notfound {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 4rem;
  text-align: center;
}

.notfound-code {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  font-family: 'Instrument Serif', Georgia, serif;
  font-size: clamp(10rem, 30vw, 22rem);
  line-height: 1;
  color: rgba(230, 161, 90, 0.08);
  pointer-events: none;
  user-select: none;
}

.notfound-img {
  position: relative;
  width: 9rem;
  margin-bottom: 2rem;
  filter: drop-shadow(0 25px 25px rgba(0, 0, 0, 0.5));
  animation: wobble 6s ease-in-out infinite;
}

@keyframes wobble {
  50% { transform: translateY(-10px) rotate(8deg); }
}

@media (prefers-reduced-motion: reduce) {
  .notfound-img {
    animation: none;
  }
}

.notfound-search {
  display: flex;
  gap: 0.4rem;
  width: 100%;
  max-width: 28rem;
  margin-top: 2rem;
  padding: 0.35rem;
  border-radius: 9999px;
  background: rgba(244, 236, 225, 0.05);
  border: 1px solid rgba(244, 236, 225, 0.12);
}

.notfound-search input {
  flex: 1;
  min-width: 0;
  padding: 0 1rem;
  border: 0;
  background: transparent;
  color: #f4ece1;
  outline: none;
}
</style>
